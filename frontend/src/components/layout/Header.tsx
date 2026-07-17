import type { MouseEvent } from 'react'

type HeaderProps = {
  onPlannerClick: () => void
  onProtectedNavClick: (event: MouseEvent<HTMLAnchorElement>, targetId: 'route-results' | 'driver-logs') => void
}

export function Header({ onPlannerClick, onProtectedNavClick }: HeaderProps) {
  return (
    <header className="top-nav">
      <a className="brand" href="#planner" aria-label="FreightPilot home" onClick={onPlannerClick}>
        <span className="brand-dots"><i /><i /><i /></span>
        <strong>FreightPilot</strong>
      </a>
      <nav aria-label="Primary navigation">
        <a href="#planner" onClick={onPlannerClick}>Planner</a>
        <a href="#route-results" onClick={(event) => onProtectedNavClick(event, 'route-results')}>Route</a>
        <a href="#driver-logs" onClick={(event) => onProtectedNavClick(event, 'driver-logs')}>Logs</a>
        <a href="#trip-history">Recent Trips</a>
      </nav>
      <a className="nav-action" href="#planner" onClick={onPlannerClick}>Plan Route</a>
    </header>
  )
}