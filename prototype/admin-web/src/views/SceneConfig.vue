<template>
  <div>
    <h2 class="page-header">场景配置</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="6">
        <t-card title="场景列表" :bordered="true">
          <template #actions><t-button size="small" theme="primary">新建场景</t-button></template>
          <div v-for="scene in scenes.scenes" :key="scene.sceneId" class="scene-item" @click="selectScene(scene)">
            <div class="scene-left">
              <span class="scene-icon">{{ sceneIcon(scene.name) }}</span>
              <div class="scene-info">
                <div class="scene-name">{{ scene.label }}</div>
                <div class="scene-desc">{{ sceneTriggerLabel(scene.triggerType) }} · {{ scene.applicableRoomTypes.map(rtLabel).join('、') }}</div>
              </div>
            </div>
            <div class="scene-right">
              <t-tag size="small" variant="light" :theme="scene.triggerType === 'Auto' ? 'success' : scene.triggerType === 'Schedule' ? 'primary' : 'default'">
                {{ scene.triggerType === 'Auto' ? '自动' : scene.triggerType === 'Schedule' ? '定时' : '手动' }}
              </t-tag>
              <t-switch size="small" :value="true" />
            </div>
          </div>
        </t-card>
      </t-col>
      <t-col :span="6">
        <t-card v-if="selectedScene" :title="`${selectedScene.label} - 规则配置`" :bordered="true">
          <template #actions>
            <t-button size="small" theme="primary" variant="outline">保存修改</t-button>
          </template>
          <div class="scene-meta">
            <div class="detail-row"><span>触发方式</span><t-tag size="small">{{ sceneTriggerLabel(selectedScene.triggerType) }}</t-tag></div>
            <div class="detail-row"><span>适用房型</span><span>{{ selectedScene.applicableRoomTypes.map(rtLabel).join('、') }}</span></div>
          </div>
          <t-divider />
          <h4 class="section-title">执行步骤</h4>
          <div v-for="rule in selectedScene.rules" :key="rule.sequence" class="rule-item">
            <div class="rule-seq">步骤 {{ rule.sequence }}</div>
            <div class="rule-content">
              <t-tag variant="outline" size="small">{{ deviceTypeLabel(rule.deviceType) }}</t-tag>
              <span class="rule-action">{{ actionLabel(rule.action) }}</span>
              <span v-if="rule.params.brightness !== undefined" class="rule-param">亮度 {{ rule.params.brightness }}%</span>
              <span v-if="rule.params.colorTemp !== undefined" class="rule-param">色温 {{ rule.params.colorTemp }}K</span>
              <span v-if="rule.params.temperature !== undefined" class="rule-param">温度 {{ rule.params.temperature }}°C</span>
              <span v-if="rule.params.volume !== undefined" class="rule-param">音量 {{ rule.params.volume }}%</span>
              <span v-if="rule.params.source !== undefined" class="rule-param">音源 {{ rule.params.source }}</span>
              <span v-if="rule.params.effect !== undefined" class="rule-param">效果 {{ rule.params.effect }}</span>
            </div>
          </div>
          <t-divider />
          <h4 class="section-title">触发条件</h4>
          <div class="trigger-info">
            <div v-if="selectedScene.triggerType === 'Auto'" class="detail-row">
              <span>触发事件</span><span>门锁开门 / 订单开始</span>
            </div>
            <div v-if="selectedScene.triggerType === 'Schedule'" class="detail-row">
              <span>定时规则</span><span>预约开始前15分钟</span>
            </div>
            <div v-if="selectedScene.triggerType === 'Manual'" class="detail-row">
              <span>触发方式</span><span>客人/店员手动选择</span>
            </div>
          </div>
        </t-card>
        <t-card v-else :bordered="true" style="text-align:center;padding:40px;color:#999">
          请选择左侧场景查看规则详情
        </t-card>
      </t-col>
    </t-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { scenes } from '@/mock/data'

const selectedScene = ref<any>(null)

function selectScene(scene: any) { selectedScene.value = scene }

function sceneIcon(name: string) {
  const map: Record<string, string> = { Welcome: '🚪', TeaSession: '🍵', Meeting: '💡', Karaoke: '🎤', EnergySave: '♻', PreOpen: '⏰' }
  return map[name] || '🎬'
}

function sceneTriggerLabel(type: string) {
  const map: Record<string, string> = { Auto: '自动触发', Manual: '手动触发', Schedule: '定时触发' }
  return map[type] || type
}

function rtLabel(type: string) {
  const map: Record<string, string> = { MeetingRoom: '会议室', TeaRoom: '茶室', Exhibition: '展厅', Workspace: '工作间' }
  return map[type] || type
}

function deviceTypeLabel(type: string) {
  const map: Record<string, string> = { Lock: '门锁', AC: '空调', Light: '灯光', Curtain: '窗帘', Speaker: '音响' }
  return map[type] || type
}

function actionLabel(action: string) {
  const map: Record<string, string> = {
    On: '开启', Off: '关闭', Temperature: '调温', ColorTemp: '调色温',
    Color: '彩色效果', Volume: '音量', Mute: '静音', Close: '关闭',
  }
  return map[action] || action
}
</script>

<style scoped>
.scene-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; border-bottom: 1px solid #f0f0f0; cursor: pointer; transition: background 0.15s; }
.scene-item:hover { background: #f5f7fa; }
.scene-left { display: flex; align-items: center; gap: 12px; }
.scene-icon { font-size: 22px; }
.scene-info { display: flex; flex-direction: column; gap: 4px; }
.scene-name { font-size: 14px; font-weight: 600; }
.scene-desc { font-size: 12px; color: #999; }
.scene-right { display: flex; align-items: center; gap: 8px; }
.scene-meta { background: #f9f9f9; padding: 12px; border-radius: 6px; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 0; font-size: 13px; color: #666; }
.section-title { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: #333; }
.rule-item { display: flex; gap: 12px; align-items: center; padding: 8px 0; border-bottom: 1px solid #f5f5f5; }
.rule-item:last-child { border-bottom: none; }
.rule-seq { font-size: 12px; color: #999; min-width: 48px; }
.rule-content { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; font-size: 13px; }
.rule-action { font-weight: 500; }
.rule-param { color: #999; font-size: 12px; }
.trigger-info { font-size: 13px; color: #666; }
</style>
