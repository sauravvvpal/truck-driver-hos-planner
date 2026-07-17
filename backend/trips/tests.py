from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from .models import TripPlanRecord
from .services import Location


class TripPlanApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	@patch('trips.services.fetch_route')
	@patch('trips.services.geocode_location')
	def test_trip_plan_returns_route_stops_and_log_sheets(self, mock_geocode, mock_fetch_route):
		mock_geocode.side_effect = [
			Location('Current location', 41.8781, -87.6298, 'Chicago, Illinois'),
			Location('Pickup location', 39.9612, -82.9988, 'Columbus, Ohio'),
			Location('Dropoff location', 33.7490, -84.3880, 'Atlanta, Georgia'),
		]
		mock_fetch_route.return_value = {
			'geometry': {
				'coordinates': [
					[-87.6298, 41.8781],
					[-82.9988, 39.9612],
					[-84.3880, 33.7490],
				]
			},
			'legs': [
				{'distance': 450 * 1609.344},
				{'distance': 560 * 1609.344},
			],
		}

		response = self.client.post('/api/trips/plan/', {
			'currentLocation': 'Chicago, IL',
			'pickupLocation': 'Columbus, OH',
			'dropoffLocation': 'Atlanta, GA',
			'currentCycleUsed': 12,
		}, format='json')

		self.assertEqual(response.status_code, 200)
		payload = response.json()
		self.assertEqual(payload['summary']['fuelStops'], 1)
		self.assertGreaterEqual(payload['summary']['daysRequired'], 2)
		self.assertGreaterEqual(len(payload['route']['geometry']), 3)
		self.assertTrue(payload['logSheets'][0]['segments'])
		self.assertEqual(TripPlanRecord.objects.count(), 1)
		record = TripPlanRecord.objects.get()
		self.assertEqual(payload['id'], record.id)
		self.assertEqual(record.current_location, 'Chicago, IL')
		self.assertEqual(record.plan_data['summary']['totalMiles'], payload['summary']['totalMiles'])

		history_response = self.client.get('/api/trips/history/')

		self.assertEqual(history_response.status_code, 200)
		history_payload = history_response.json()
		self.assertEqual(len(history_payload), 1)
		self.assertEqual(history_payload[0]['id'], record.id)
		self.assertEqual(history_payload[0]['plan']['summary']['totalMiles'], payload['summary']['totalMiles'])

	def test_current_cycle_used_must_be_inside_cycle_limit(self):
		response = self.client.post('/api/trips/plan/', {
			'currentLocation': 'Chicago, IL',
			'pickupLocation': 'Columbus, OH',
			'dropoffLocation': 'Atlanta, GA',
			'currentCycleUsed': 72,
		}, format='json')

		self.assertEqual(response.status_code, 400)
		self.assertEqual(TripPlanRecord.objects.count(), 0)
