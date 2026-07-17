from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt
from typing import Any

import requests

MILES_PER_METER = 0.000621371
AVERAGE_TRUCK_SPEED_MPH = 55
MAX_DAILY_DRIVE_HOURS = 11
MAX_DUTY_WINDOW_HOURS = 14
BREAK_AFTER_DRIVE_HOURS = 8
BREAK_DURATION_HOURS = 0.5
REQUIRED_REST_HOURS = 10
MAX_CYCLE_HOURS = 70
FUEL_INTERVAL_MILES = 1000
FUEL_STOP_HOURS = 0.5
SERVICE_STOP_HOURS = 1


class TripPlanningError(Exception):
    pass


@dataclass(frozen=True)
class Location:
    label: str
    lat: float
    lon: float
    display_name: str


FALLBACK_LOCATIONS = {
    'atlanta, ga': (33.7490, -84.3880, 'Atlanta, Georgia'),
    'chicago, il': (41.8781, -87.6298, 'Chicago, Illinois'),
    'columbus, oh': (39.9612, -82.9988, 'Columbus, Ohio'),
    'dallas, tx': (32.7767, -96.7970, 'Dallas, Texas'),
    'denver, co': (39.7392, -104.9903, 'Denver, Colorado'),
    'houston, tx': (29.7604, -95.3698, 'Houston, Texas'),
    'indianapolis, in': (39.7684, -86.1581, 'Indianapolis, Indiana'),
    'los angeles, ca': (34.0522, -118.2437, 'Los Angeles, California'),
    'new york, ny': (40.7128, -74.0060, 'New York, New York'),
    'phoenix, az': (33.4484, -112.0740, 'Phoenix, Arizona'),
}


@dataclass(frozen=True)
class RouteLeg:
    label: str
    distance_miles: float
    duration_hours: float


def build_trip_plan(current_location: str, pickup_location: str, dropoff_location: str, current_cycle_used: float) -> dict[str, Any]:
    locations = [
        geocode_location('Current location', current_location),
        geocode_location('Pickup location', pickup_location),
        geocode_location('Dropoff location', dropoff_location),
    ]
    route = fetch_route(locations)
    legs = [
        RouteLeg('Current to pickup', route['legs'][0]['distance'] * MILES_PER_METER, route['legs'][0]['distance'] * MILES_PER_METER / AVERAGE_TRUCK_SPEED_MPH),
        RouteLeg('Pickup to dropoff', route['legs'][1]['distance'] * MILES_PER_METER, route['legs'][1]['distance'] * MILES_PER_METER / AVERAGE_TRUCK_SPEED_MPH),
    ]

    geometry = [[lat, lon] for lon, lat in route['geometry']['coordinates']]
    events = _build_hos_events(legs, locations, geometry, current_cycle_used)
    log_sheets = _build_log_sheets(events)
    total_miles = sum(leg.distance_miles for leg in legs)

    return {
        'locations': [location.__dict__ for location in locations],
        'route': {
            'geometry': geometry,
            'distanceMiles': round(total_miles, 1),
            'driveHours': round(sum(leg.duration_hours for leg in legs), 2),
        },
        'stops': _build_stops(events, locations, geometry, total_miles),
        'events': events,
        'logSheets': log_sheets,
        'summary': {
            'totalMiles': round(total_miles, 1),
            'estimatedDriveHours': round(sum(leg.duration_hours for leg in legs), 2),
            'totalElapsedHours': round(events[-1]['endHour'], 2) if events else 0,
            'daysRequired': len(log_sheets),
            'fuelStops': len([event for event in events if event['type'] == 'fuel']),
            'restStops': len([event for event in events if event['type'] in {'break', 'daily_rest', 'restart'}]),
            'cycleUsedAtStart': current_cycle_used,
        },
        'assumptions': [
            'Property-carrying driver under 70 hours / 8 days rules',
            '11-hour driving limit and 14-hour on-duty window',
            '30-minute break after 8 cumulative driving hours',
            '10-hour off-duty/sleeper reset between duty periods',
            'Fuel stop inserted at least every 1,000 miles',
            'Pickup and drop-off each take 1 hour on duty',
        ],
    }


def geocode_location(label: str, query: str) -> Location:
    try:
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': query, 'format': 'json', 'limit': 1},
            headers={'User-Agent': 'truck-eld-planner/1.0'},
            timeout=15,
        )
        response.raise_for_status()
        results = response.json()
    except requests.RequestException:
        fallback = _fallback_location(label, query)
        if fallback:
            return fallback
        raise TripPlanningError('The geocoding provider is unavailable. Try a major US city such as Chicago, IL or Atlanta, GA.')

    if not results:
        raise TripPlanningError(f'Could not find {label.lower()}: {query}')
    result = results[0]
    return Location(label=label, lat=float(result['lat']), lon=float(result['lon']), display_name=result['display_name'])


def fetch_route(locations: list[Location]) -> dict[str, Any]:
    coordinates = ';'.join(f'{location.lon},{location.lat}' for location in locations)
    try:
        response = requests.get(
            f'https://router.project-osrm.org/route/v1/driving/{coordinates}',
            params={'overview': 'full', 'geometries': 'geojson', 'steps': 'false'},
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException:
        return _fallback_route(locations)

    if payload.get('code') != 'Ok' or not payload.get('routes'):
        return _fallback_route(locations)
    return payload['routes'][0]


def _fallback_location(label: str, query: str) -> Location | None:
    result = FALLBACK_LOCATIONS.get(query.strip().lower())
    if not result:
        return None

    lat, lon, display_name = result
    return Location(label=label, lat=lat, lon=lon, display_name=display_name)


def _fallback_route(locations: list[Location]) -> dict[str, Any]:
    geometry = [[location.lon, location.lat] for location in locations]
    legs = []
    for start, end in zip(locations, locations[1:]):
        estimated_miles = _distance_between(start.lat, start.lon, end.lat, end.lon) * 1.18
        legs.append({'distance': estimated_miles / MILES_PER_METER})

    return {
        'geometry': {'coordinates': geometry},
        'legs': legs,
    }


def _distance_between(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> float:
    earth_radius_miles = 3958.8
    lat_delta = radians(end_lat - start_lat)
    lon_delta = radians(end_lon - start_lon)
    start_lat_rad = radians(start_lat)
    end_lat_rad = radians(end_lat)
    haversine = sin(lat_delta / 2) ** 2 + cos(start_lat_rad) * cos(end_lat_rad) * sin(lon_delta / 2) ** 2
    return earth_radius_miles * 2 * atan2(sqrt(haversine), sqrt(1 - haversine))


def _build_hos_events(legs: list[RouteLeg], locations: list[Location], geometry: list[list[float]], current_cycle_used: float) -> list[dict[str, Any]]:
    state = {
        'clock': 0.0,
        'daily_drive_left': MAX_DAILY_DRIVE_HOURS,
        'duty_window_left': MAX_DUTY_WINDOW_HOURS,
        'drive_since_break': 0.0,
        'cycle_left': max(0.0, MAX_CYCLE_HOURS - current_cycle_used),
        'miles_from_start': 0.0,
        'miles_since_fuel': 0.0,
    }
    events: list[dict[str, Any]] = []

    _drive_leg(events, state, legs[0], geometry)
    _add_service(events, state, SERVICE_STOP_HOURS, 'onDuty', 'pickup', 'Pickup loading and paperwork', locations[1].display_name)
    _drive_leg(events, state, legs[1], geometry)
    _add_service(events, state, SERVICE_STOP_HOURS, 'onDuty', 'dropoff', 'Drop-off unloading and paperwork', locations[2].display_name)
    return events


def _drive_leg(events: list[dict[str, Any]], state: dict[str, float], leg: RouteLeg, geometry: list[list[float]]) -> None:
    remaining_miles = leg.distance_miles
    while remaining_miles > 0.05:
        _ensure_can_work(events, state, 0.05)

        # Drive blocks stop at the earliest applicable HOS or operational boundary.
        miles_until_break = max(0.0, (BREAK_AFTER_DRIVE_HOURS - state['drive_since_break']) * AVERAGE_TRUCK_SPEED_MPH)
        miles_until_fuel = FUEL_INTERVAL_MILES - state['miles_since_fuel']
        max_drive_miles = min(
            remaining_miles,
            state['daily_drive_left'] * AVERAGE_TRUCK_SPEED_MPH,
            state['duty_window_left'] * AVERAGE_TRUCK_SPEED_MPH,
            state['cycle_left'] * AVERAGE_TRUCK_SPEED_MPH,
            miles_until_break if miles_until_break > 0 else remaining_miles,
            miles_until_fuel if miles_until_fuel > 0 else remaining_miles,
        )

        if max_drive_miles <= 0.05:
            if state['drive_since_break'] >= BREAK_AFTER_DRIVE_HOURS:
                _add_off_duty(events, state, BREAK_DURATION_HOURS, 'break', '30-minute HOS break')
            elif state['daily_drive_left'] <= 0.05 or state['duty_window_left'] <= 0.05:
                _add_off_duty(events, state, REQUIRED_REST_HOURS, 'daily_rest', '10-hour sleeper/off-duty reset')
            else:
                _add_off_duty(events, state, 34, 'restart', '34-hour restart after cycle limit')
                state['cycle_left'] = MAX_CYCLE_HOURS
            continue

        duration = max_drive_miles / AVERAGE_TRUCK_SPEED_MPH
        start_mile = state['miles_from_start']
        state['clock'] += duration
        state['daily_drive_left'] -= duration
        state['duty_window_left'] -= duration
        state['drive_since_break'] += duration
        state['cycle_left'] -= duration
        state['miles_from_start'] += max_drive_miles
        state['miles_since_fuel'] += max_drive_miles
        remaining_miles -= max_drive_miles
        events.append(_event('driving', 'drive', 'Driving', leg.label, state['clock'] - duration, state['clock'], start_mile, state['miles_from_start'], geometry))

        if abs(state['miles_since_fuel'] - FUEL_INTERVAL_MILES) < 0.1 and remaining_miles > 0.05:
            _add_service(events, state, FUEL_STOP_HOURS, 'onDuty', 'fuel', 'Fuel stop', 'En route fuel stop')
            state['miles_since_fuel'] = 0.0
        if state['drive_since_break'] >= BREAK_AFTER_DRIVE_HOURS and remaining_miles > 0.05:
            _add_off_duty(events, state, BREAK_DURATION_HOURS, 'break', '30-minute HOS break')


def _ensure_can_work(events: list[dict[str, Any]], state: dict[str, float], minimum_hours: float) -> None:
    if state['cycle_left'] < minimum_hours:
        _add_off_duty(events, state, 34, 'restart', '34-hour restart after cycle limit')
        state['cycle_left'] = MAX_CYCLE_HOURS
    if state['daily_drive_left'] < minimum_hours or state['duty_window_left'] < minimum_hours:
        _add_off_duty(events, state, REQUIRED_REST_HOURS, 'daily_rest', '10-hour sleeper/off-duty reset')


def _add_service(events: list[dict[str, Any]], state: dict[str, float], duration: float, status: str, event_type: str, title: str, location: str) -> None:
    _ensure_can_work(events, state, duration)
    start = state['clock']
    state['clock'] += duration
    state['duty_window_left'] -= duration
    state['cycle_left'] -= duration
    events.append({
        'status': status,
        'type': event_type,
        'title': title,
        'location': location,
        'startHour': round(start, 2),
        'endHour': round(state['clock'], 2),
        'durationHours': round(duration, 2),
        'mile': round(state['miles_from_start'], 1),
    })


def _add_off_duty(events: list[dict[str, Any]], state: dict[str, float], duration: float, event_type: str, title: str) -> None:
    start = state['clock']
    state['clock'] += duration
    if duration >= REQUIRED_REST_HOURS:
        state['daily_drive_left'] = MAX_DAILY_DRIVE_HOURS
        state['duty_window_left'] = MAX_DUTY_WINDOW_HOURS
    state['drive_since_break'] = 0.0
    events.append({
        'status': 'sleeper' if duration >= REQUIRED_REST_HOURS else 'offDuty',
        'type': event_type,
        'title': title,
        'location': 'Safe legal rest area',
        'startHour': round(start, 2),
        'endHour': round(state['clock'], 2),
        'durationHours': round(duration, 2),
        'mile': round(state['miles_from_start'], 1),
    })


def _event(status: str, event_type: str, title: str, location: str, start: float, end: float, start_mile: float, end_mile: float, geometry: list[list[float]]) -> dict[str, Any]:
    return {
        'status': status,
        'type': event_type,
        'title': title,
        'location': location,
        'startHour': round(start, 2),
        'endHour': round(end, 2),
        'durationHours': round(end - start, 2),
        'startMile': round(start_mile, 1),
        'endMile': round(end_mile, 1),
        'coordinate': _coordinate_at_mile(geometry, end_mile),
    }


def _build_log_sheets(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not events:
        return []
    days = int(events[-1]['endHour'] // 24) + 1
    sheets = []
    for day in range(days):
        day_start = day * 24
        segments = []
        totals = {'offDuty': 0.0, 'sleeper': 0.0, 'driving': 0.0, 'onDuty': 0.0}
        for event in events:
            # Split events that cross midnight so each daily log remains a 24-hour sheet.
            start = max(event['startHour'], day_start)
            end = min(event['endHour'], day_start + 24)
            if end <= start:
                continue
            duration = end - start
            status = event['status']
            totals[status] += duration
            segments.append({
                'status': status,
                'type': event['type'],
                'title': event['title'],
                'location': event['location'],
                'start': round(start - day_start, 2),
                'end': round(end - day_start, 2),
                'durationHours': round(duration, 2),
            })
        sheets.append({
            'day': day + 1,
            'segments': segments,
            'totals': {key: round(value, 2) for key, value in totals.items()},
            'totalHours': round(sum(totals.values()), 2),
        })
    return sheets


def _build_stops(events: list[dict[str, Any]], locations: list[Location], geometry: list[list[float]], total_miles: float) -> list[dict[str, Any]]:
    stops = [
        {'type': 'start', 'title': 'Start', 'location': locations[0].display_name, 'coordinate': [locations[0].lat, locations[0].lon], 'mile': 0},
        {'type': 'pickup', 'title': 'Pickup', 'location': locations[1].display_name, 'coordinate': [locations[1].lat, locations[1].lon], 'mile': None},
        {'type': 'dropoff', 'title': 'Drop-off', 'location': locations[2].display_name, 'coordinate': [locations[2].lat, locations[2].lon], 'mile': round(total_miles, 1)},
    ]
    for event in events:
        if event['type'] in {'fuel', 'break', 'daily_rest', 'restart'}:
            mile = event.get('mile', event.get('endMile', 0))
            stops.append({
                'type': event['type'],
                'title': event['title'],
                'location': event['location'],
                'coordinate': _coordinate_at_mile(geometry, mile),
                'mile': mile,
            })
    return stops


def _coordinate_at_mile(geometry: list[list[float]], target_mile: float) -> list[float]:
    if not geometry:
        return [0, 0]
    if target_mile <= 0:
        return geometry[0]
    traveled = 0.0
    for start, end in zip(geometry, geometry[1:]):
        segment_miles = _haversine_miles(start, end)
        if traveled + segment_miles >= target_mile:
            # Interpolate along the route polyline to place generated stops near their planned mileage.
            ratio = (target_mile - traveled) / segment_miles if segment_miles else 0
            return [start[0] + (end[0] - start[0]) * ratio, start[1] + (end[1] - start[1]) * ratio]
        traveled += segment_miles
    return geometry[-1]


def _haversine_miles(start: list[float], end: list[float]) -> float:
    lat1, lon1 = radians(start[0]), radians(start[1])
    lat2, lon2 = radians(end[0]), radians(end[1])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    value = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 3958.8 * 2 * atan2(sqrt(value), sqrt(1 - value))