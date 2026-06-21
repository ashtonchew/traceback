import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  BackgroundVariant,
  useReactFlow,
  type Edge,
  type Node,
  type NodeMouseHandler,
} from '@xyflow/react'
import { Maximize2, Minus, Plus, Lock } from 'lucide-react'
import { nodeTypes } from '../nodes/nodes'
import { edgeTypes } from '../nodes/ClusterEdge'

function ZoomBar() {
  const { zoomIn, zoomOut, fitView } = useReactFlow()
  return (
    <div className="absolute right-4 top-4 z-10 flex items-center gap-1 rounded-lg border border-hairline bg-surface-raised p-1 shadow-sm">
      <button onClick={() => fitView({ duration: 300 })} className="flex h-7 w-7 items-center justify-center rounded-md text-ink-tertiary hover:bg-surface hover:text-ink-secondary">
        <Maximize2 size={14} />
      </button>
      <button onClick={() => zoomOut({ duration: 150 })} className="flex h-7 w-7 items-center justify-center rounded-md text-ink-tertiary hover:bg-surface hover:text-ink-secondary">
        <Minus size={15} />
      </button>
      <span className="px-1 text-xs font-medium text-ink-secondary-strong">100%</span>
      <button onClick={() => zoomIn({ duration: 150 })} className="flex h-7 w-7 items-center justify-center rounded-md text-ink-tertiary hover:bg-surface hover:text-ink-secondary">
        <Plus size={15} />
      </button>
      <button className="flex h-7 w-7 items-center justify-center rounded-md text-ink-tertiary hover:bg-surface hover:text-ink-secondary">
        <Lock size={13} />
      </button>
    </div>
  )
}

export function RunCanvas({
  nodes,
  edges,
  onNodeClick,
  fitPadding = 0.2,
}: {
  nodes: Node[]
  edges: Edge[]
  onNodeClick?: NodeMouseHandler
  fitPadding?: number
}) {
  return (
    <ReactFlowProvider>
    <div className="relative h-full w-full">
      <ZoomBar />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{ padding: fitPadding }}
        minZoom={0.3}
        maxZoom={1.6}
        proOptions={{ hideAttribution: true }}
        nodesDraggable
        nodesConnectable={false}
        elementsSelectable
      >
        <Background variant={BackgroundVariant.Dots} gap={26} size={1} color="var(--ds-neutral-200)" />
      </ReactFlow>
    </div>
    </ReactFlowProvider>
  )
}
