from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal
from backend.models import FriendshipRequest, User
# from tournaments.models import Tournament
from .consumers import LoginMenuConsumer
import logging, asyncio
from channels.db import database_sync_to_async

logger = logging.getLogger('pong')

@receiver(post_delete, sender=FriendshipRequest)
@receiver(post_save, sender=FriendshipRequest)
async def friendship_updated(sender, instance, **kwargs):

	if instance:
		receiver = instance.receiver
		receiver_id = receiver.id
	
		for consumer in LoginMenuConsumer.instances:
			if consumer.user.id == receiver_id:
				await consumer.broadcast_notification()
				logger.debug(f"Sent friend update notification to {receiver.username}")
				break

		for consumer in LoginMenuConsumer.instances:
			if consumer.user.id == instance.sender.id:
				await consumer.broadcast_notification()
				logger.debug(f"Sent friend update notification to {instance.sender.username}")
				break

profile_updated_signal = Signal()

@receiver(profile_updated_signal)
async def profile_updated(sender, **kwargs):
	user : User = kwargs.get('user')
	for consumer in LoginMenuConsumer.instances:
		if consumer.user == user:
			await consumer.broadcast_notification()
			logger.debug(f"Sent profile update notification to {user.username}")
			break

tournament_started_signal = Signal()
tournament_updated_signal = Signal()

@receiver(tournament_started_signal)
@receiver(tournament_updated_signal)
async def tournament_updated(sender, instance, **kwargs):
	if instance: 
		users = [await database_sync_to_async(User.objects.get)(username=username) for username in instance.players]
		for user in users:
			for consumer in LoginMenuConsumer.instances:
				if consumer.user == user:
					await consumer.broadcast({'event': 'tournament',})
					logger.debug(f"Sent tournament update notification to {user.username}")
					break