from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.translation import activate
from django.shortcuts import redirect
from backend.models import User, Ladderboard
from backend.forms import UserProfileUpdateForm
from pong.models import OngoingGame
from tournaments.models import Tournament
from backend.signals import profile_updated_signal
from backend.decorators import require_header
from backend.views import custom_activate
from .models import (
    get_user, user_about, user_status, user_stats, user_matches,
	format_matches, user_friends, user_pending_sent,
	user_pending_received, friendship_status
)
import os, json, logging
import time
import re


logger = logging.getLogger('pong')

@require_header
@require_http_methods(["GET"])
def profile_view(request, username=None):
	# activate(request.session.get('django_language', 'en'))
	logger.info(f"Profile view requested by {request.user.username} for {username}")
	custom_activate(request)
	if not request.user.is_authenticated:
		return HttpResponseForbidden('Not authenticated')

	if username is None or not get_user(username):
		target_user = request.user
		is_own_profile = True
		username = request.user.username
	else:
		target_user = get_user(username)
		is_own_profile = (request.user.username == username)

	matches_data = user_matches(username)
	formatted_matches = format_matches(matches_data)

	context = {
		'user': target_user,
		'own_profile': is_own_profile,
		'is_champion': Ladderboard.user_champion(target_user),
		'rank': target_user.rank,
		'status': user_status(target_user),
		'about': user_about(target_user),
		'stats': user_stats(username),
		'matches': formatted_matches,
		'friends': {
			'friendship_status': friendship_status(request.user, target_user),
			'list': user_friends(target_user),
			'pending_sent': user_pending_sent(target_user),
			'pending_received': user_pending_received(target_user)
		},
		'profile_pic': target_user.profile_pic
	}

	if is_own_profile:
		context['account'] = {
			'username': target_user.username,
			'email': target_user.email,
			'profile_pictures': pic_selection(target_user), # should be settings.PPIC_SELECTION
		}
	return render(request, 'views/profile-view.html', context)

def pic_selection(user=None):
	directories = [
		os.path.join(settings.MEDIA_ROOT, 'profile-pics'),
		os.path.join(settings.MEDIA_ROOT, 'users', str(user.uuid)),
	]
	base_url = f"https://{settings.WEB_HOST}{settings.MEDIA_URL}"
	profile_pics = []

	for directory in directories:
		if os.path.exists(directory):
			for pic in sorted(os.listdir(directory)):
				relative_path = os.path.relpath(directory, settings.MEDIA_ROOT)
				pic_url = f"{base_url}{relative_path}/{pic}"
				profile_pics.append(pic_url)

	return profile_pics

@require_header
@login_required
@require_http_methods(["PUT"])
def update_profile(request):
	try:
		data = json.loads(request.body)
		user = request.user
		user_uuid = str(user.uuid)

		# Check if user is in game or tournament
		if OngoingGame.player_in_game(user_uuid):
			return JsonResponse({'error': 'Cannot update profile while in an active game'}, status=400)

		if Tournament.player_in_tournament(user_uuid):
			return JsonResponse({'error': 'Cannot update profile while in a tournament'}, status=400)

		# Initialize form with current user data and new data
		form = UserProfileUpdateForm(data, instance=user, user=user)

		if form.is_valid():
			# Handle profile picture separately as it's not part of the form
			if 'profile_pic' in data:
				profile_pic_path = data['profile_pic']
				user.profile_pic = profile_pic_path

			# Save the form data	
			form.save()

			# Send profile update signal
			profile_updated_signal.send(sender=update_profile, user=user)
			return JsonResponse({'message': 'Profile updated successfully'})
		else:
			# Return the first validation error
			for field, errors in form.errors.items():
				return JsonResponse({'error': errors[0]}, status=400)

	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	except Exception as e:
		logger.error(f"Error updating profile: {str(e)}")
		return JsonResponse({'error': 'An error occurred while updating the profile'}, status=500)

@require_header
@require_http_methods(["GET"])
def find_user(request):
	if not request.user.is_authenticated:
		return HttpResponseForbidden('Not authenticated')
		
	query = request.GET.get('q', '').strip()
	if not query or len(query) < 2:
		return JsonResponse({'results': []})

	matching_users = User.objects.filter(
		username__icontains=query,
		is_active=True
	).values('username', 'profile_pic')[:10]
	
	results = list(matching_users)
	return JsonResponse({'results': results})


def set_language(request):
	lang_code = request.GET.get('lang', 'en')
	if lang_code in dict(settings.LANGUAGES):
		request.session['django_language'] = lang_code
		activate(lang_code)
		user = request.user
		if user.is_authenticated:
			user.language = lang_code
			logger.info(f"User {user.username} changed language to {user.language}")
			user.save()
	return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
@require_header
@require_http_methods(["POST"])
def upload_profile_pic(request):
	try:
		upload_profile_pic = request.FILES.get('profile_pic')
		if not upload_profile_pic:
			return JsonResponse({'error': 'No file uploaded'}, status=400)
		
		max_size_size = 5 * 1024 * 1024
		if upload_profile_pic.size > max_size_size:
			return JsonResponse({'error': 'File size exceeds 5 MB'}, status=400)

		user = request.user
		old_profile_pic = user.profile_pic
		file_name = f"{user.uuid}.png"
		file_path = os.path.join('users', f"{user.uuid}" , file_name)

		user_dir =  os.path.join(settings.MEDIA_ROOT, 'users', f"{user.uuid}")
		if not os.path.exists(user_dir):
			os.makedirs(user_dir)

		if old_profile_pic:
			old_profile_pic_path = os.path.join(settings.MEDIA_ROOT, old_profile_pic.replace(f"https://{settings.WEB_HOST}{settings.MEDIA_URL}", ''))
			if os.path.exists(old_profile_pic_path) and old_profile_pic_path.startswith(user_dir):
				default_storage.delete(old_profile_pic_path)
			file_name = f"{user.uuid}_{int(time.time())}.png"
			file_path = os.path.join('users', f"{user.uuid}", file_name)

		if default_storage.exists(file_path):
			default_storage.delete(file_path)
		default_storage.save(file_path, ContentFile(upload_profile_pic.read()))

		profile_pic_url = f"https://{settings.WEB_HOST}{settings.MEDIA_URL}users/{user.uuid}/{file_name}"
		user.profile_pic = profile_pic_url
		user.save()
		profile_updated_signal.send(sender=upload_profile_pic, user=user)
		return JsonResponse({
			'success': True,
			'message': 'Profile picture uploaded successfully',
			'profile_pic': user.profile_pic
		})
	except Exception as e:
		logger.error(f"Error uploading profile picture: {str(e)}")
		return JsonResponse({'error': 'An error occurred while uploading the profile picture'}, status=500)
	
