/**
 * IoT 485 总线指令队列
 *
 * 防止 RS485 总线指令冲突导致设备假死：
 * - FIFO 队列，一次只处理一条指令
 * - 同设备同类型指令自动去重（防抖）
 * - 冲突指令检测（如"全关"后紧跟"全开"）
 * - 每条指令记录发送时间、状态到 audit_log
 */

export interface DeviceCommand {
  id: string
  deviceId: string
  deviceName: string
  roomName: string
  type: 'Lock' | 'AC' | 'Light' | 'Curtain' | 'Speaker' | 'Scene'
  action: string
  payload?: Record<string, any>
  timestamp: number
  status: 'pending' | 'sending' | 'success' | 'failed'
  operator?: string
  sourceIp?: string
}

type CommandCallback = (cmd: DeviceCommand) => void

class CommandQueue {
  private queue: DeviceCommand[] = []
  private processing = false
  private cmdId = 0
  private onEachCallback: CommandCallback | null = null
  private onCompleteCallback: CommandCallback | null = null

  /** 设置每个指令处理后的回调（用于更新 UI） */
  onEach(cb: CommandCallback) { this.onEachCallback = cb; return this }

  /** 设置全部完成后的回调 */
  onComplete(cb: CommandCallback) { this.onCompleteCallback = cb; return this }

  /**
   * 提交指令到队列。
   * 如果同设备同 action 的指令已在队列中（pending），
   * 则用新指令覆盖旧指令（防抖：只执行最后一次操作）。
   */
  enqueue(cmd: Omit<DeviceCommand, 'id' | 'timestamp' | 'status'>): string {
    const id = `CMD${String(++this.cmdId).padStart(4, '0')}`
    const fullCmd: DeviceCommand = { ...cmd, id, timestamp: Date.now(), status: 'pending' }

    // 防抖：同设备同类型指令去重
    const existingIdx = this.queue.findIndex(
      c => c.deviceId === cmd.deviceId && c.action === cmd.action && c.status === 'pending'
    )
    if (existingIdx >= 0) {
      this.queue[existingIdx] = fullCmd
      return fullCmd.id
    }

    // 冲突检测：如果已有关联指令正在处理，记录警告
    const conflict = this.queue.find(
      c => c.deviceId === cmd.deviceId && isConflict(c.action, cmd.action)
    )
    if (conflict) {
      console.warn(`[CMD-Q] 冲突指令: ${cmd.action} 入队时 ${conflict.action} 尚未执行`)
    }

    this.queue.push(fullCmd)
    this.processNext()
    return fullCmd.id
  }

  /** 批量提交场景指令（如"全关"涉及多个设备） */
  enqueueBatch(commands: Omit<DeviceCommand, 'id' | 'timestamp' | 'status'>[]): string[] {
    return commands.map(cmd => this.enqueue(cmd))
  }

  /** 获取队列长度 */
  get length() { return this.queue.length }

  /** 当前是否正在处理 */
  get isProcessing() { return this.processing }

  /** 清空 pending 队列 */
  clear() {
    this.queue = this.queue.filter(c => c.status !== 'pending')
  }

  private processNext() {
    if (this.processing || this.queue.length === 0) return
    this.processing = true

    // 找出第一个 pending 指令
    const idx = this.queue.findIndex(c => c.status === 'pending')
    if (idx < 0) { this.processing = false; return }

    const cmd = this.queue[idx]
    cmd.status = 'sending'

    // 模拟 485 总线发送延迟 (300~800ms)
    const delay = 300 + Math.random() * 500

    setTimeout(() => {
      // 95% 成功率模拟
      cmd.status = Math.random() > 0.05 ? 'success' : 'failed'

      if (this.onEachCallback) this.onEachCallback(cmd)

      this.processing = false
      // 从队列移除已处理的指令
      this.queue.splice(idx, 1)

      if (this.queue.length === 0) {
        if (this.onCompleteCallback) this.onCompleteCallback(cmd)
      } else {
        // 处理下一条指令有 200ms 间隔（总线释放时间）
        setTimeout(() => this.processNext(), 200)
      }
    }, delay)
  }
}

/** 检测两个 action 是否冲突 */
function isConflict(a: string, b: string): boolean {
  const conflictPairs = [
    ['open', 'close'], ['close', 'open'],
    ['lock', 'unlock'], ['unlock', 'lock'],
    ['on', 'off'], ['off', 'on'],
    ['全开', '全关'], ['全关', '全开'],
    ['营业模式', '节能模式'], ['节能模式', '营业模式'],
  ]
  // 标准动作映射
  const norm = (s: string) => s.toLowerCase().trim()
  return conflictPairs.some(([x, y]) => norm(a) === x && norm(b) === y)
}

/** 创建审计日志条目 */
export function buildAuditLog(cmd: DeviceCommand, operator: string, ip: string) {
  return {
    id: cmd.id,
    action: cmd.type === 'Scene' ? 'SceneOverride' : `DeviceControl`,
    deviceId: cmd.deviceId,
    deviceName: cmd.deviceName,
    roomName: cmd.roomName,
    operatorName: operator,
    operatorRole: localStorage.getItem('erp_user') || '店员',
    sourceIp: ip,
    reason: `远程${cmd.type === 'Scene' ? '场景' : '设备'}控制: ${cmd.action}`,
    targetStatus: cmd.action,
    status: cmd.status,
    createdAt: new Date().toISOString(),
    auditStatus: 'Pending',
  }
}

// 全局单例
export const commandQueue = new CommandQueue()

export default commandQueue
