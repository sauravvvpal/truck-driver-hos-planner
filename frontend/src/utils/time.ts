export function formatHour(value: number) {
  const day = Math.floor(value / 24) + 1
  return `Day ${day}, ${formatClock(value % 24)}`
}

export function formatClock(value: number) {
  const hours = Math.floor(value)
  const minutes = Math.round((value - hours) * 60)
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`
}