from django.apps import AppConfig
import sys, threading, asyncio, logging

logger = logging.getLogger('pong')
class TournamentsConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'tournaments'

	def ready(self):
		if 'runserver' not in sys.argv:
			return
		
		from .tournaments import TournamentManager
		def start_manager():
			loop = asyncio.new_event_loop()
			asyncio.set_event_loop(loop)
			manager = TournamentManager()
			manager.start(loop)
			try:
				loop.run_forever()
			except Exception as e:
				logger.error(f"Error in tournament manager loop: {str(e)}")
			finally:
				loop.close()
				logger.info("Tournament manager loop closed")		
			
		
		thread = threading.Thread(target=start_manager, daemon=True)
		thread.start()