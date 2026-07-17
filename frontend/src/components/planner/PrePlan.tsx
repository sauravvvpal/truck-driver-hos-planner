import { BarChart3, MapPin, PackageCheck } from 'lucide-react'

export function PrePlan() {
  return (
    <section className="pre-plan">
      <div className="capability-card primary">
        <span><BarChart3 /></span>
        <h2>Route intelligence</h2>
        <p>See mileage, drive time, fuel points, and rest requirements before dispatch accepts the load.</p>
      </div>
      <div className="capability-card">
        <span><PackageCheck /></span>
        <h2>Pickup to delivery</h2>
        <p>Account for loading, unloading, and en-route duty changes in the same plan.</p>
      </div>
      <div className="capability-card">
        <span><MapPin /></span>
        <h2>Driver-ready logs</h2>
        <p>Turn route events into daily log graphs that are easy for operations teams to review.</p>
      </div>
    </section>
  )
}