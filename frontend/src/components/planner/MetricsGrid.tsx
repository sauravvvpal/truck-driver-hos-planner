import type { ReactNode } from 'react'
import { ClipboardList, Clock3, Fuel, Gauge } from 'lucide-react'

export function MetricsGrid() {
  return (
    <section className="summary-grid" aria-label="Planning safeguards">
      <Metric icon={<Gauge />} label="Planning mode" value="HOS compliant" />
      <Metric icon={<Fuel />} label="Fuel policy" value="Auto inserted" />
      <Metric icon={<Clock3 />} label="Rest logic" value="Breaks + resets" />
      <Metric icon={<ClipboardList />} label="Output" value="Daily logs" />
    </section>
  )
}

function Metric({ icon, label, value }: { icon: ReactNode; label: string; value: string }) {
  return (
    <div className="metric-card">
      <span>{icon}</span>
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
      </div>
    </div>
  )
}