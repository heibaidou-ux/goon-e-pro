import workflow from '@mock/workflow.json'

export interface WorkflowContext {
  [key: string]: any
}

export interface WorkflowAction {
  targetNode: string
}

export interface WorkflowNode {
  nodeId: string
  name: string
  type: string
  assigneeType: string
  assignee: string
  timeoutHours: number
  conditions: { field: string; operator: string; value: number }[]
  actions: Record<string, string>
}

export interface WorkflowDef {
  workflowId: string
  name: string
  entityType: string
  entityLabel: string
  description: string
  version: number
  enabled: boolean
  nodes: WorkflowNode[]
  conditionEval?: string
}

export interface ApprovalTask {
  taskId: string
  instanceId: string
  workflowId: string
  nodeId: string
  nodeName: string
  entityId: string
  entityName: string
  entityType: string
  summary: string
  assigneeRole: string
  assigneeName: string
  priority: string
  status: string
  createdAt: string
  formData?: any
}

function getDef(workflowId: string): WorkflowDef | undefined {
  return (workflow.workflowDefs as WorkflowDef[]).find(d => d.workflowId === workflowId)
}

function evaluateCondition(context: WorkflowContext, field: string, operator: string, value: number): boolean {
  const actual = context[field]
  if (actual === undefined) return false
  switch (operator) {
    case '>': return actual > value
    case '>=': return actual >= value
    case '<': return actual < value
    case '<=': return actual <= value
    case '==': return actual === value
    case '!=': return actual !== value
    default: return false
  }
}

function evaluateNodeConditions(def: WorkflowDef, node: WorkflowNode, context: WorkflowContext): boolean {
  if (!node.conditions || node.conditions.length === 0) return true
  const mode = def.conditionEval || 'any'
  const results = node.conditions.map(c => evaluateCondition(context, c.field, c.operator, c.value))
  return mode === 'all' ? results.every(Boolean) : results.some(Boolean)
}

export function resolveNextNode(workflowId: string, context: WorkflowContext): { nodeId: string; nodeName: string; assigneeRole: string } | null {
  const def = getDef(workflowId)
  if (!def) return null

  for (const node of def.nodes) {
    if (node.conditions.length === 0) continue
    if (evaluateNodeConditions(def, node, context)) {
      return { nodeId: node.nodeId, nodeName: node.name, assigneeRole: node.assignee }
    }
  }

  const lastNode = def.nodes[def.nodes.length - 1]
  return { nodeId: lastNode.nodeId, nodeName: lastNode.name, assigneeRole: lastNode.assignee }
}

export function getFirstNode(workflowId: string): WorkflowNode | null {
  const def = getDef(workflowId)
  if (!def || def.nodes.length === 0) return null
  return def.nodes[0]
}

export function getNextNode(workflowId: string, currentNodeId: string, action: string): { targetNodeId: string; isFinal: boolean } {
  const def = getDef(workflowId)
  if (!def) return { targetNodeId: '__rejected__', isFinal: true }

  const node = def.nodes.find(n => n.nodeId === currentNodeId)
  if (!node) return { targetNodeId: '__rejected__', isFinal: true }

  const targetId = node.actions[action] || '__rejected__'
  const isFinal = targetId.startsWith('__')
  return { targetNodeId: targetId, isFinal }
}

export function getTasksForRole(role: string): ApprovalTask[] {
  return (workflow.approvalTasks as ApprovalTask[]).filter(t => t.assigneeRole === role && t.status === 'pending')
}

export function getTasksForInstance(instanceId: string): ApprovalTask[] {
  return (workflow.approvalTasks as ApprovalTask[]).filter(t => t.instanceId === instanceId)
}

export function getInstance(instanceId: string) {
  return (workflow.workflowInstances as any[]).find(i => i.instanceId === instanceId)
}

export function getDefs(): WorkflowDef[] {
  return workflow.workflowDefs as WorkflowDef[]
}

export {
  workflow,
}
