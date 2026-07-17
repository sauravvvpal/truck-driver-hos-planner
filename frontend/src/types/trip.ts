export type TripRequest = {
  currentLocation: string
  pickupLocation: string
  dropoffLocation: string
  currentCycleUsed: number
}

export type DutyStatus = 'offDuty' | 'sleeper' | 'driving' | 'onDuty'

export type Stop = {
  type: string
  title: string
  location: string
  coordinate: [number, number]
  mile: number | null
}

export type TripEvent = {
  status: DutyStatus
  type: string
  title: string
  location: string
  startHour: number
  endHour: number
  durationHours: number
}

export type LogSegment = {
  status: DutyStatus
  type: string
  title: string
  location: string
  start: number
  end: number
  durationHours: number
}

export type LogSheet = {
  day: number
  segments: LogSegment[]
  totals: Record<DutyStatus, number>
}

export type TripPlan = {
  id?: number
  route: {
    geometry: [number, number][]
    distanceMiles: number
    driveHours: number
  }
  stops: Stop[]
  events: TripEvent[]
  logSheets: LogSheet[]
  summary: {
    totalMiles: number
    estimatedDriveHours: number
    totalElapsedHours: number
    daysRequired: number
    fuelStops: number
    restStops: number
  }
}

export type TripHistoryItem = {
  id: number
  currentLocation: string
  pickupLocation: string
  dropoffLocation: string
  totalMiles: number
  daysRequired: number
  createdAt: string
  plan: TripPlan
}