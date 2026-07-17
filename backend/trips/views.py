from requests import RequestException
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TripPlanRecord
from .services import TripPlanningError, build_trip_plan


class TripPlanSerializer(serializers.Serializer):
    currentLocation = serializers.CharField(max_length=180)
    pickupLocation = serializers.CharField(max_length=180)
    dropoffLocation = serializers.CharField(max_length=180)
    currentCycleUsed = serializers.FloatField(min_value=0, max_value=70)


class TripPlanView(APIView):
    def post(self, request):
        serializer = TripPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            plan = build_trip_plan(
                data['currentLocation'],
                data['pickupLocation'],
                data['dropoffLocation'],
                data['currentCycleUsed'],
            )
        except TripPlanningError as error:
            return Response({'detail': str(error)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except RequestException:
            return Response({'detail': 'The route provider is unavailable. Please try again.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        record = TripPlanRecord.objects.create(
            current_location=data['currentLocation'],
            pickup_location=data['pickupLocation'],
            dropoff_location=data['dropoffLocation'],
            current_cycle_used=data['currentCycleUsed'],
            total_miles=plan['summary']['totalMiles'],
            estimated_drive_hours=plan['summary']['estimatedDriveHours'],
            total_elapsed_hours=plan['summary']['totalElapsedHours'],
            days_required=plan['summary']['daysRequired'],
            fuel_stops=plan['summary']['fuelStops'],
            rest_stops=plan['summary']['restStops'],
            plan_data=plan,
        )
        plan['id'] = record.id

        return Response(plan)


class TripHistoryView(APIView):
    def get(self, request):
        records = TripPlanRecord.objects.all()[:10]
        history = [
            {
                'id': record.id,
                'currentLocation': record.current_location,
                'pickupLocation': record.pickup_location,
                'dropoffLocation': record.dropoff_location,
                'totalMiles': float(record.total_miles),
                'daysRequired': record.days_required,
                'createdAt': record.created_at.isoformat(),
                'plan': {**record.plan_data, 'id': record.id},
            }
            for record in records
        ]

        return Response(history)
