import { CalendarClock, MapPinned, Route, RotateCcw } from 'lucide-react'
import type { TripHistoryItem, TripPlan } from '../../types/trip'

type RecentTripsProps = {
  history: TripHistoryItem[]
  isLoading: boolean
  error: string | null
  onSelect: (plan: TripPlan) => void
}

const dateFormatter = new Intl.DateTimeFormat('en', {
  month: 'short',
  day: 'numeric',
  hour: 'numeric',
  minute: '2-digit',
})

export function RecentTrips({ history, isLoading, error, onSelect }: RecentTripsProps) {
  return (
    <section className="history-panel" id="trip-history">
      <div className="section-heading">
        <div>
          <p>Saved planning history</p>
          <h2>Recent trips</h2>
        </div>
        <span>{history.length} saved</span>
      </div>

      {error ? <p className="history-error">{error}</p> : null}
      {isLoading ? <p className="history-empty">Loading saved trips...</p> : null}
      {!isLoading && history.length === 0 ? <p className="history-empty">No saved trips yet. Generated plans will appear here.</p> : null}

      <div className="history-list">
        {history.map((trip) => (
          <article className="history-card" key={trip.id}>
            <div className="history-route-icon"><Route /></div>
            <div>
              <h3>{trip.pickupLocation} to {trip.dropoffLocation}</h3>
              <p><MapPinned /> Start: {trip.currentLocation}</p>
              <div className="history-meta">
                <span><CalendarClock /> {dateFormatter.format(new Date(trip.createdAt))}</span>
                <span>{trip.totalMiles.toLocaleString()} mi</span>
                <span>{trip.daysRequired} days</span>
              </div>
            </div>
            <button type="button" onClick={() => onSelect(trip.plan)}>
              <RotateCcw /> View
            </button>
          </article>
        ))}
      </div>
    </section>
  )
}
