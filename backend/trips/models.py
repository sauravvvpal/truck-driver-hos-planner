from django.db import models


class TripPlanRecord(models.Model):
	current_location = models.CharField(max_length=180)
	pickup_location = models.CharField(max_length=180)
	dropoff_location = models.CharField(max_length=180)
	current_cycle_used = models.DecimalField(max_digits=5, decimal_places=2)
	total_miles = models.DecimalField(max_digits=8, decimal_places=1)
	estimated_drive_hours = models.DecimalField(max_digits=6, decimal_places=2)
	total_elapsed_hours = models.DecimalField(max_digits=6, decimal_places=2)
	days_required = models.PositiveSmallIntegerField()
	fuel_stops = models.PositiveSmallIntegerField()
	rest_stops = models.PositiveSmallIntegerField()
	plan_data = models.JSONField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.current_location} to {self.dropoff_location} ({self.total_miles} mi)'
