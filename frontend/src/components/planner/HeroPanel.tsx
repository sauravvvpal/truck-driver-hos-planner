import { ShieldCheck } from 'lucide-react'

export function HeroPanel() {
  return (
    <div className="hero-copy">
      <div className="eyebrow"><ShieldCheck size={18} /> Compliance command center</div>
      <h1>Plan compliant freight routes before the truck rolls.</h1>
      <p>
        Build a route, forecast required breaks, and create driver-ready daily logs from one dispatch workspace.
      </p>
      <div className="hero-stats" aria-label="Planner capabilities">
        <MiniStat value="70/8" label="Cycle model" />
        <MiniStat value="11 hr" label="Drive cap" />
        <MiniStat value="1,000 mi" label="Fuel interval" />
      </div>
    </div>
  )
}

function MiniStat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  )
}