from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal
from backend.models import FriendshipRequest, User
from .consumers import LoginMenuConsumer
import logging, asyncio
from asgiref.sync import async_to_sync

logger = logging.getLogger('pong')

@receiver(post_delete, sender=FriendshipRequest)
@receiver(post_save, sender=FriendshipRequest)
def friendship_updated(sender, instance, **kwargs):

	if instance:
		receiver = instance.receiver
		receiver_id = receiver.id
	
		for consumer in LoginMenuConsumer.instances:
			if consumer.user.id == receiver_id:
				async_to_sync(consumer.broadcast_notification)()
				logger.debug(f"Sent friend update notification to {receiver.username}")
				break

		for consumer in LoginMenuConsumer.instances:
			if consumer.user.id == instance.sender.id:
				async_to_sync(consumer.broadcast_notification)()
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


