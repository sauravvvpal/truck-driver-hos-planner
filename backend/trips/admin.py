from django.contrib import admin

from .models import TripPlanRecord


@admin.register(TripPlanRecord)
class TripPlanRecordAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'current_location',
		'pickup_location',
		'dropoff_location',
		'total_miles',
		'days_required',
		'created_at',
	)
	list_filter = ('days_required', 'created_at')
	search_fields = ('current_location', 'pickup_location', 'dropoff_location')
	readonly_fields = ('created_at', 'plan_data')
