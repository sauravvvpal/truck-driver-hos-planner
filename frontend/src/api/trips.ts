import type { TripHistoryItem, TripPlan, TripRequest } from '../types/trip'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api'

export async function createTripPlan(request: TripRequest): Promise<TripPlan> {
  const response = await fetch(`${API_URL}/trips/plan/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  const payload = await response.json()

  if (!response.ok) {
    throw new Error(payload.detail ?? 'Unable to build this trip plan.')
  }

  return payload
}

export async function getTripHistory(): Promise<TripHistoryItem[]> {
  const response = await fetch(`${API_URL}/trips/history/`)
  const payload = await response.json()

  if (!response.ok) {
    throw new Error(payload.detail ?? 'Unable to load saved trip history.')
  }

  return payload
}