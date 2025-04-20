from django.apps import AppConfig
from django.utils.translation import activate

class BackendConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'backend'

	def ready(self):
		import backend.signals
		# from backend.models import Ladderboard
		# Ladderboard.initialize_all()

def custom_activate(request): 
	user = request.user
	if user.is_authenticated:
		activate(user.language)
	else:
		activate(request.session.get('django_language', 'en'))