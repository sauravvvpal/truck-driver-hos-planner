import { useEffect, useRef, useState } from 'react'
import type { FormEvent, MouseEvent } from 'react'
import { flushSync } from 'react-dom'
import 'leaflet/dist/leaflet.css'
import { createTripPlan, getTripHistory } from './api/trips'
import { Header } from './components/layout/Header'
import { HeroPanel } from './components/planner/HeroPanel'
import { MetricsGrid } from './components/planner/MetricsGrid'
import { PrePlan } from './components/planner/PrePlan'
import { TripPlannerForm } from './components/planner/TripPlannerForm'
import { RecentTrips } from './components/results/RecentTrips'
import { TripResults } from './components/results/TripResults'
import type { TripHistoryItem, TripPlan, TripRequest } from './types/trip'
import './App.css'

const initialTrip: TripRequest = {
  currentLocation: 'Chicago, IL',
  pickupLocation: 'Columbus, OH',
  dropoffLocation: 'Atlanta, GA',
  currentCycleUsed: 18,
}

function App() {
  const [form, setForm] = useState<TripRequest>(initialTrip)
  const [plan, setPlan] = useState<TripPlan | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [history, setHistory] = useState<TripHistoryItem[]>([])
  const [isHistoryLoading, setIsHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [navMessage, setNavMessage] = useState<string | null>(null)
  const navMessageRef = useRef<HTMLParagraphElement | null>(null)
  const routeResultsRef = useRef<HTMLElement | null>(null)

  async function loadTripHistory() {
    setIsHistoryLoading(true)
    setHistoryError(null)

    try {
      const savedTrips = await getTripHistory()
      setHistory(savedTrips)
    } catch (caughtError) {
      setHistoryError(caughtError instanceof Error ? caughtError.message : 'Saved trips are unavailable right now.')
    } finally {
      setIsHistoryLoading(false)
    }
  }

  useEffect(() => {
    void loadTripHistory()
  }, [])

  useEffect(() => {
    if (!plan) {
      return
    }

    const frame = window.requestAnimationFrame(() => {
      routeResultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })

    return () => window.cancelAnimationFrame(frame)
  }, [plan])

  function scrollNavMessageToCenter() {
    window.setTimeout(() => {
      const message = navMessageRef.current
      if (!message) {
        return
      }

      const messageTop = message.getBoundingClientRect().top + window.scrollY
      const centeredTop = messageTop - (window.innerHeight - message.offsetHeight) / 2
      const scrollTop = Math.max(0, centeredTop)

      window.scrollTo({ top: scrollTop, behavior: 'auto' })
      document.documentElement.scrollTop = scrollTop
    }, 80)
  }

  function handleProtectedNav(event: MouseEvent<HTMLAnchorElement>, targetId: 'route-results' | 'driver-logs') {
    if (plan) {
      return
    }

    event.preventDefault()
    flushSync(() => {
      setNavMessage(targetId === 'route-results' ? 'Generate a trip plan first to view the route.' : 'Generate a trip plan first to create driver logs.')
    })
    scrollNavMessageToCenter()
  }

  function handlePlannerNav() {
    setNavMessage(null)
  }

  function updateForm(nextForm: TripRequest) {
    setForm(nextForm)
    setNavMessage(null)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const payload = await createTripPlan(form)
      setNavMessage(null)
      setPlan(payload)
      void loadTripHistory()
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : 'Route planning is unavailable right now.')
    } finally {
      setIsLoading(false)
    }
  }

  function handleHistorySelect(savedPlan: TripPlan) {
    setNavMessage(null)
    setPlan(savedPlan)
  }

  return (
    <>
      <Header onPlannerClick={handlePlannerNav} onProtectedNavClick={handleProtectedNav} />

      <main className="app-shell">
        <section className="hero-panel" id="planner">
          <HeroPanel />
          <TripPlannerForm
            form={form}
            isLoading={isLoading}
            error={error}
            navMessage={navMessage}
            navMessageRef={navMessageRef}
            onChange={updateForm}
            onSubmit={handleSubmit}
          />
        </section>

        <MetricsGrid />

        {plan ? <TripResults plan={plan} resultsRef={routeResultsRef} /> : <PrePlan />}

        <RecentTrips history={history} isLoading={isHistoryLoading} error={historyError} onSelect={handleHistorySelect} />
      </main>
    </>
  )
}

export default App