from django.contrib import admin
from django.db import models
from .models import GameSessionStats, UserStats, MatchHistory

@admin.register(GameSessionStats)
class GameSessionStatAdmin(admin.ModelAdmin):
	def __init__(self, model, admin_site):
		super().__init__(model, admin_site)
		self.list_display = [field.name for field in model._meta.fields]
		# self.list_filter = ('player1_sets', 'player2_sets')  # Replace with actual fields
		self.search_fields = [
			field.name for field in model._meta.fields
			if isinstance(field, models.CharField)
		]

@admin.register(UserStats)
class UserStatAdmin(admin.ModelAdmin):
	def __init__(self, model, admin_site):
		super().__init__(model, admin_site)
		self.list_display = [field.name for field in model._meta.fields]
		# self.list_filter = ('most_touches', 'most_wins', 'longest_win_streak', 'time_played',)
		self.search_fields = [
			field.name for field in model._meta.fields
			if isinstance(field, models.CharField)
		]

@admin.register(MatchHistory)
class MatchHistoryAdmin(admin.ModelAdmin):
	def __init__(self, model, admin_site):
		super().__init__(model, admin_site)
		self.list_display = [field.name for field in model._meta.fields]
		# self.list_filter = ('player2_username', 'outcome')  # Replace with actual fields
		self.search_fields = [
			field.name for field in model._meta.fields
			if isinstance(field, models.CharField)
		]
