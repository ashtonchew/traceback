import { Routes, Route, Outlet } from 'react-router-dom'
import { Sidebar } from './components/Sidebar'
import { RunRoot } from './views/RunRoot'
import { RunTree } from './views/RunTree'
import { RunWitness } from './views/RunWitness'
import { PatchView } from './views/PatchView'
import { GateRunning } from './views/GateRunning'
import { GateWitnessFailed } from './views/GateWitnessFailed'
import { GateControlFailed } from './views/GateControlFailed'
import { ReleaseProof } from './views/ReleaseProof'

function AppLayout() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      <Sidebar />
      <main className="flex min-w-0 flex-1 flex-col">
        <Outlet />
      </main>
    </div>
  )
}

function Placeholder({ title }: { title: string }) {
  return (
    <div className="flex flex-1 items-center justify-center">
      <div className="text-center">
        <h1 className="font-display text-3xl tracking-tight text-ink-primary">{title}</h1>
        <p className="mt-2 text-sm text-ink-secondary">This surface is out of scope for the current designs.</p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<RunRoot />} />
        <Route path="/tree" element={<RunTree />} />
        <Route path="/witness" element={<RunWitness mode="branch" />} />
        <Route path="/proofset" element={<RunWitness mode="proofset" />} />
        <Route path="/patch" element={<PatchView />} />
        <Route path="/gate" element={<GateRunning />} />
        <Route path="/gate/witness-failed" element={<GateWitnessFailed />} />
        <Route path="/gate/control-failed" element={<GateControlFailed />} />
        <Route path="/releaseproof" element={<ReleaseProof />} />
        <Route path="/agents" element={<Placeholder title="Agents" />} />
        <Route path="/tools" element={<Placeholder title="Tools" />} />
        <Route path="/memory" element={<Placeholder title="Memory" />} />
        <Route path="/settings" element={<Placeholder title="Settings" />} />
      </Route>
    </Routes>
  )
}
