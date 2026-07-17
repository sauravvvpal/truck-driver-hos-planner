import type { FormEvent, RefObject } from 'react'
import { Loader2, MapPinned, Navigation, Route } from 'lucide-react'
import type { TripRequest } from '../../types/trip'

type TripPlannerFormProps = {
  form: TripRequest
  isLoading: boolean
  error: string | null
  navMessage: string | null
  navMessageRef: RefObject<HTMLParagraphElement | null>
  onChange: (nextForm: TripRequest) => void
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
}

export function TripPlannerForm({ form, isLoading, error, navMessage, navMessageRef, onChange, onSubmit }: TripPlannerFormProps) {
  return (
    <form className="trip-form" onSubmit={onSubmit}>
      <div className="form-heading">
        <span><Route size={20} /></span>
        <div>
          <p>New dispatch plan</p>
          <h2>Trip details</h2>
        </div>
      </div>
      <label>
        Current location
        <input value={form.currentLocation} onChange={(event) => onChange({ ...form, currentLocation: event.target.value })} placeholder="Dallas, TX" required />
      </label>
      <label>
        Pickup location
        <input value={form.pickupLocation} onChange={(event) => onChange({ ...form, pickupLocation: event.target.value })} placeholder="Memphis, TN" required />
      </label>
      <label>
        Drop-off location
        <input value={form.dropoffLocation} onChange={(event) => onChange({ ...form, dropoffLocation: event.target.value })} placeholder="Charlotte, NC" required />
      </label>
      <label>
        Cycle hours already used
        <input type="number" min="0" max="70" step="0.25" value={form.currentCycleUsed} onChange={(event) => onChange({ ...form, currentCycleUsed: Number(event.target.value) })} required />
      </label>
      <button type="submit" disabled={isLoading}>
        {isLoading ? <Loader2 className="spin" size={18} /> : <Navigation size={18} />}
        {isLoading ? 'Optimizing trip...' : 'Generate plan'}
      </button>
      {navMessage && <p className="nav-message" ref={navMessageRef}><MapPinned size={18} /> {navMessage}</p>}
      {error && <p className="form-error">{error}</p>}
    </form>
  )
}