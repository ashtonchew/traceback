import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  BackgroundVariant,
  useReactFlow,
  useViewport,
  type Edge,
  type Node,
  type NodeMouseHandler,
} from '@xyflow/react'
import { Maximize2, Minus, Plus } from './icons'
import { nodeTypes } from '../nodes/nodes'
import { edgeTypes } from '../nodes/ClusterEdge'

const DEFAULT_FIT_MAX_ZOOM = 0.62
const ENTER_ANIMATION_MS = 320

function ZoomBar() {
  const { zoomIn, zoomOut, fitView } = useReactFlow()
  const { zoom } = useViewport()
  const zoomPercent = `${Math.round(zoom * 100)}%`

  return (
    <div className="absolute right-4 top-4 z-10 flex items-center gap-1 rounded-lg border border-hairline bg-surface-raised p-1 shadow-sm">
      <button type="button" aria-label="Fit graph" onClick={() => fitView({ duration: 180 })} className="flex h-7 w-7 items-center justify-center rounded-md text-ink-tertiary transition-[background-color,color,transform] duration-150 ease-out hover:bg-surface hover:text-ink-secondary active:scale-[0.94] focus:outline-none focus-visible:ring-2 focus-visible:ring-ring">
        <Maximize2 size={14} />
      </button>
      <button type="button" aria-label="Zoom out" onClick={() => zoomOut({ duration: 160 })} className="flex h-7 w-7 items-center justify-center rounded-md text-ink-tertiary transition-[background-color,color,transform] duration-150 ease-out hover:bg-surface hover:text-ink-secondary active:scale-[0.94] focus:outline-none focus-visible:ring-2 focus-visible:ring-ring">
        <Minus size={15} />
      </button>
      <span className="min-w-10 px-1 text-center text-xs font-medium text-ink-secondary-strong" aria-live="polite">
        {zoomPercent}
      </span>
      <button type="button" aria-label="Zoom in" onClick={() => zoomIn({ duration: 160 })} className="flex h-7 w-7 items-center justify-center rounded-md text-ink-tertiary transition-[background-color,color,transform] duration-150 ease-out hover:bg-surface hover:text-ink-secondary active:scale-[0.94] focus:outline-none focus-visible:ring-2 focus-visible:ring-ring">
        <Plus size={15} />
      </button>
    </div>
  )
}

function FlowInner({
  nodes,
  edges,
  onNodeClick,
  fitPadding,
  fitMaxZoom,
}: {
  nodes: Node[]
  edges: Edge[]
  onNodeClick?: NodeMouseHandler
  fitPadding: number
  fitMaxZoom: number
}) {
  const { fitView, getViewport, setViewport } = useReactFlow()
  const [flowReady, setFlowReady] = useState(false)
  const flowRootRef = useRef<HTMLDivElement | null>(null)
  const lastFitSignature = useRef<string | null>(null)
  const fitFrame = useRef<number | null>(null)
  const fitTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const seenNodeIds = useRef<Set<string> | null>(null)
  const seenEdgeIds = useRef<Set<string> | null>(null)
  const nodeEnterTimers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map())
  const edgeEnterTimers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map())
  const nodeRevealFrames = useRef<Map<string, number>>(new Map())
  const edgeRevealFrames = useRef<Map<string, number>>(new Map())
  const [enteringNodeIds, setEnteringNodeIds] = useState<Set<string>>(() => new Set())
  const [enteringEdgeIds, setEnteringEdgeIds] = useState<Set<string>>(() => new Set())
  const [revealedNodeIds, setRevealedNodeIds] = useState<Set<string>>(() => new Set())
  const [revealedEdgeIds, setRevealedEdgeIds] = useState<Set<string>>(() => new Set())

  const animatedNodes = useMemo(() => {
    const seen = seenNodeIds.current
    return nodes.map((node) => {
      const isNew = seen !== null && !seen.has(node.id)
      const isEntering = isNew || enteringNodeIds.has(node.id)
      if (!isEntering) return node

      const isRevealed = revealedNodeIds.has(node.id)
      const className = ['fp-enter', isRevealed && 'fp-enter-revealed', node.className].filter(Boolean).join(' ')
      return { ...node, className }
    })
  }, [nodes, enteringNodeIds, revealedNodeIds])

  const animatedEdges = useMemo(() => {
    const seen = seenEdgeIds.current
    return edges.map((edge) => {
      const isNew = seen !== null && !seen.has(edge.id)
      const isEntering = isNew || enteringEdgeIds.has(edge.id)
      return isEntering
        ? { ...edge, data: { ...(edge.data ?? {}), entering: true, revealed: revealedEdgeIds.has(edge.id) } }
        : edge
    })
  }, [edges, enteringEdgeIds, revealedEdgeIds])

  useEffect(() => {
    if (nodes.length === 0 && seenNodeIds.current === null) return
    const nextIds = new Set(nodes.map((node) => node.id))
    const previousIds = seenNodeIds.current

    if (previousIds) {
      const addedIds = [...nextIds].filter((id) => !previousIds.has(id))
      if (addedIds.length) {
        setEnteringNodeIds((current) => new Set([...current, ...addedIds]))
        setRevealedNodeIds((current) => {
          const next = new Set(current)
          addedIds.forEach((id) => next.delete(id))
          return next
        })
        addedIds.forEach((id) => {
          const existing = nodeEnterTimers.current.get(id)
          if (existing) clearTimeout(existing)
          const existingFrame = nodeRevealFrames.current.get(id)
          if (existingFrame) cancelAnimationFrame(existingFrame)
          const frame = requestAnimationFrame(() => {
            nodeRevealFrames.current.delete(id)
            setRevealedNodeIds((current) => new Set([...current, id]))
          })
          nodeRevealFrames.current.set(id, frame)
          const timer = setTimeout(() => {
            nodeEnterTimers.current.delete(id)
            setEnteringNodeIds((current) => {
              const next = new Set(current)
              next.delete(id)
              return next
            })
            setRevealedNodeIds((current) => {
              const next = new Set(current)
              next.delete(id)
              return next
            })
          }, ENTER_ANIMATION_MS)
          nodeEnterTimers.current.set(id, timer)
        })
      }
    }

    seenNodeIds.current = nextIds
  }, [nodes])

  useEffect(() => {
    const nextIds = new Set(edges.map((edge) => edge.id))
    const previousIds = seenEdgeIds.current

    if (previousIds) {
      const addedIds = [...nextIds].filter((id) => !previousIds.has(id))
      if (addedIds.length) {
        setEnteringEdgeIds((current) => new Set([...current, ...addedIds]))
        setRevealedEdgeIds((current) => {
          const next = new Set(current)
          addedIds.forEach((id) => next.delete(id))
          return next
        })
        addedIds.forEach((id) => {
          const existing = edgeEnterTimers.current.get(id)
          if (existing) clearTimeout(existing)
          const existingFrame = edgeRevealFrames.current.get(id)
          if (existingFrame) cancelAnimationFrame(existingFrame)
          const frame = requestAnimationFrame(() => {
            edgeRevealFrames.current.delete(id)
            setRevealedEdgeIds((current) => new Set([...current, id]))
          })
          edgeRevealFrames.current.set(id, frame)
          const timer = setTimeout(() => {
            edgeEnterTimers.current.delete(id)
            setEnteringEdgeIds((current) => {
              const next = new Set(current)
              next.delete(id)
              return next
            })
            setRevealedEdgeIds((current) => {
              const next = new Set(current)
              next.delete(id)
              return next
            })
          }, ENTER_ANIMATION_MS)
          edgeEnterTimers.current.set(id, timer)
        })
      }
    }

    seenEdgeIds.current = nextIds
  }, [edges])

  useEffect(() => {
    return () => {
      nodeEnterTimers.current.forEach((timer) => clearTimeout(timer))
      edgeEnterTimers.current.forEach((timer) => clearTimeout(timer))
      nodeRevealFrames.current.forEach((frame) => cancelAnimationFrame(frame))
      edgeRevealFrames.current.forEach((frame) => cancelAnimationFrame(frame))
      if (fitFrame.current) cancelAnimationFrame(fitFrame.current)
      if (fitTimer.current) clearTimeout(fitTimer.current)
      nodeEnterTimers.current.clear()
      edgeEnterTimers.current.clear()
      nodeRevealFrames.current.clear()
      edgeRevealFrames.current.clear()
      fitFrame.current = null
      fitTimer.current = null
    }
  }, [])

  const centerRenderedNodes = useCallback((duration: number) => {
    const root = flowRootRef.current
    const flowBounds = root?.querySelector('.react-flow')?.getBoundingClientRect()
    const nodeBounds = Array.from(root?.querySelectorAll('.react-flow__node') ?? []).map((node) => node.getBoundingClientRect())
    if (!flowBounds || nodeBounds.length === 0) return

    const left = Math.min(...nodeBounds.map((bounds) => bounds.left))
    const right = Math.max(...nodeBounds.map((bounds) => bounds.right))
    const top = Math.min(...nodeBounds.map((bounds) => bounds.top))
    const bottom = Math.max(...nodeBounds.map((bounds) => bounds.bottom))
    const deltaX = (left + right) / 2 - (flowBounds.left + flowBounds.right) / 2
    const deltaY = (top + bottom) / 2 - (flowBounds.top + flowBounds.bottom) / 2
    if (Math.abs(deltaX) < 1 && Math.abs(deltaY) < 1) return

    const viewport = getViewport()
    setViewport(
      {
        ...viewport,
        x: viewport.x - deltaX,
        y: viewport.y - deltaY,
      },
      { duration: Math.min(duration, 220) },
    )
  }, [getViewport, setViewport])

  const fitCanvas = useCallback((duration: number) => {
    if (fitFrame.current) cancelAnimationFrame(fitFrame.current)
    if (fitTimer.current) clearTimeout(fitTimer.current)
    fitTimer.current = setTimeout(() => {
      fitTimer.current = null
      fitFrame.current = requestAnimationFrame(() => {
        fitFrame.current = null
        void fitView({ padding: fitPadding, maxZoom: fitMaxZoom, duration }).then(() => {
          requestAnimationFrame(() => centerRenderedNodes(duration))
        })
      })
    }, 50)
  }, [fitView, fitPadding, fitMaxZoom, centerRenderedNodes])

  useEffect(() => {
    if (!flowReady || nodes.length === 0) return

    const deepestLayer = Math.max(...nodes.map((node) => node.position.y))
    const fitSignature = `${nodes.length}:${deepestLayer}`
    if (lastFitSignature.current === fitSignature) return

    const isInitialFit = lastFitSignature.current === null
    lastFitSignature.current = fitSignature
    fitCanvas(isInitialFit ? 220 : 200)
  }, [nodes, flowReady, fitCanvas])

  return (
    <div ref={flowRootRef} className="h-full w-full">
      <ReactFlow
        nodes={animatedNodes}
        edges={animatedEdges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        onNodeClick={onNodeClick}
        onInit={() => setFlowReady(true)}
        minZoom={0.2}
        maxZoom={1.6}
        proOptions={{ hideAttribution: true }}
        nodesDraggable
        nodesConnectable={false}
        elementsSelectable
      >
        <Background variant={BackgroundVariant.Dots} gap={26} size={1} color="var(--ds-neutral-200)" />
      </ReactFlow>
    </div>
  )
}

export function RunCanvas({
  nodes,
  edges,
  onNodeClick,
  fitPadding = 0.2,
  fitMaxZoom = DEFAULT_FIT_MAX_ZOOM,
}: {
  nodes: Node[]
  edges: Edge[]
  onNodeClick?: NodeMouseHandler
  fitPadding?: number
  fitMaxZoom?: number
}) {
  return (
    <ReactFlowProvider>
      <div className="relative h-full w-full">
        <ZoomBar />
        <FlowInner nodes={nodes} edges={edges} onNodeClick={onNodeClick} fitPadding={fitPadding} fitMaxZoom={fitMaxZoom} />
      </div>
    </ReactFlowProvider>
  )
}
