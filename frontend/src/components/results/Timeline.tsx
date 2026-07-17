import type { TripEvent } from '../../types/trip'
import { formatHour } from '../../utils/time'

type TimelineProps = {
  events: TripEvent[]
}

export function Timeline({ events }: TimelineProps) {
  return (
    <aside className="timeline-panel">
      <div className="section-heading compact">
        <div>
          <p>Driver timeline</p>
          <h2>Duty changes</h2>
        </div>
      </div>
      <div className="timeline">
        {events.map((event, index) => (
          <article className={`timeline-item event-${event.type}`} key={`${event.type}-${event.startHour}-${index}`}>
            <span className="timeline-dot" />
            <div>
              <strong>{event.title}</strong>
              <p>{formatHour(event.startHour)} - {formatHour(event.endHour)} | {event.durationHours} hrs</p>
              <small>{event.location}</small>
            </div>
          </article>
        ))}
      </div>
    </aside>
  )
}