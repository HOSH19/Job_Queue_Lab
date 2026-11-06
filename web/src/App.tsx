/** Dashboard shell: form, table, detail, live updates. */

import { AppHeader } from './components/AppHeader'
import { JobDetail } from './components/JobDetail'
import { JobForm } from './components/JobForm'
import { JobTable } from './components/JobTable'
import { useJobs } from './hooks/useJobs'
import { useLiveUpdates } from './hooks/useLiveUpdates'
import './App.css'

function App() {
  const {
    jobs,
    selected,
    selectedId,
    setSelectedId,
    health,
    loadError,
    refresh,
    onCreated,
    onUpdated,
  } = useJobs()
  const live = useLiveUpdates(refresh)

  return (
    <div className="app">
      <AppHeader live={live} health={health} />
      {loadError && <p className="error banner">{loadError} — is the API running on :8000?</p>}
      <div className="layout">
        <JobForm onCreated={onCreated} />
        <JobTable jobs={jobs} selectedId={selectedId} onSelect={setSelectedId} />
        <JobDetail job={selected} onUpdated={onUpdated} />
      </div>
    </div>
  )
}

export default App
