import type { ReactNode, RefObject } from 'react'
import { CalendarClock, CheckCircle2, Fuel, MapPinned } from 'lucide-react'
import type { TripPlan } from '../../types/trip'
import { RouteMap } from './RouteMap'
import { Timeline } from './Timeline'
import { LogSheetView } from './LogSheetView'

type TripResultsProps = {
  plan: TripPlan
  resultsRef: RefObject<HTMLElement | null>
}

export function TripResults({ plan, resultsRef }: TripResultsProps) {
  const routePositions = plan.route.geometry

  return (
    <section className="results-layout" id="route-results" ref={resultsRef}>
      <div className="results-summary">
        <Insight icon={<MapPinned />} value={`${plan.summary.totalMiles.toLocaleString()} mi`} label="Planned distance" />
        <Insight icon={<CalendarClock />} value={`${plan.summary.daysRequired}`} label="Log days" />
        <Insight icon={<Fuel />} value={`${plan.summary.fuelStops}`} label="Fuel stops" />
        <Insight icon={<CheckCircle2 />} value={`${plan.summary.restStops}`} label="Rest events" />
      </div>

      <div className="map-card">
        <div className="section-heading">
          <div>
            <p>Route command center</p>
            <h2>{plan.summary.totalMiles.toLocaleString()} miles with compliant stops</h2>
          </div>
          <span>{plan.summary.estimatedDriveHours} drive hrs</span>
        </div>
        <RouteMap routePositions={routePositions} stops={plan.stops} />
      </div>

      <Timeline events={plan.events} />

      <section className="logs-panel" id="driver-logs">
        <div className="section-heading">
          <div>
            <p>Driver log output</p>
            <h2>Daily ELD graph</h2>
          </div>
          <span>{plan.summary.totalElapsedHours} elapsed hrs</span>
        </div>
        <div className="log-stack">
          {plan.logSheets.map((sheet) => <LogSheetView key={sheet.day} sheet={sheet} />)}
        </div>
      </section>
    </section>
  )
}

function Insight({ icon, value, label }: { icon: ReactNode; value: string; label: string }) {
  return (
    <div className="insight-card">
      <span>{icon}</span>
      <strong>{value}</strong>
      <p>{label}</p>
    </div>
  )
}