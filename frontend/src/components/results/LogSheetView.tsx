import type { DutyStatus, LogSheet } from '../../types/trip'
import { formatClock } from '../../utils/time'

type LogSheetViewProps = {
  sheet: LogSheet
}

const dutyRows: { key: DutyStatus; label: string }[] = [
  { key: 'offDuty', label: '1. Off duty' },
  { key: 'sleeper', label: '2. Sleeper berth' },
  { key: 'driving', label: '3. Driving' },
  { key: 'onDuty', label: '4. On duty' },
]

export function LogSheetView({ sheet }: LogSheetViewProps) {
  return (
    <article className="log-sheet">
      <header>
        <div>
          <p>Driver's Daily Log</p>
          <h3>Day {sheet.day}</h3>
        </div>
        <div className="log-total">24 hour period</div>
      </header>
      <div className="log-grid">
        <div className="hour-header">
          {Array.from({ length: 25 }, (_, hour) => <span key={hour}>{hour === 0 || hour === 24 ? 'Mid' : hour}</span>)}
        </div>
        {dutyRows.map((row) => (
          <div className="duty-row" key={row.key}>
            <span className="row-label">{row.label}</span>
            <div className="row-track">
              {Array.from({ length: 24 }, (_, hour) => <i key={hour} />)}
              {sheet.segments.filter((segment) => segment.status === row.key).map((segment, index) => (
                <span
                  className={`duty-segment status-${segment.status}`}
                  key={`${segment.title}-${index}`}
                  style={{ left: `${(segment.start / 24) * 100}%`, width: `${((segment.end - segment.start) / 24) * 100}%` }}
                  title={`${segment.title}: ${segment.durationHours} hrs`}
                />
              ))}
            </div>
            <strong>{sheet.totals[row.key].toFixed(2)}</strong>
          </div>
        ))}
      </div>
      <footer>
        <div>
          <strong>Remarks</strong>
          <p>{sheet.segments.map((segment) => `${formatClock(segment.start)} ${segment.title}`).join(' | ') || 'No duty changes recorded.'}</p>
        </div>
        <div className="recap">
          <span>Driving {sheet.totals.driving.toFixed(2)}</span>
          <span>On duty {sheet.totals.onDuty.toFixed(2)}</span>
          <span>Off/Sleeper {(sheet.totals.offDuty + sheet.totals.sleeper).toFixed(2)}</span>
        </div>
      </footer>
    </article>
  )
}