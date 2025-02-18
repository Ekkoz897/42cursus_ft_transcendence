from django.contrib import admin
from django.db import models
from .models import ActiveGame

@admin.register(ActiveGame)
class ActiveGameAdmin(admin.ModelAdmin):
	def __init__(self, model, admin_site):
		super().__init__(model, admin_site)
		# Get all field names from the model
		self.list_display = [field.name for field in model._meta.fields]
		# Add created_at to list_filter 
		self.list_filter = ('created_at',)
		# Make all CharField fields searchable
		self.search_fields = [
			field.name for field in model._meta.fields 
			if isinstance(field, models.CharField)
		]