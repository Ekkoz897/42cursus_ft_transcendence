from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from backend.models import User
from .models import profile_data, get_user, user_rank, user_status, user_about, user_stats, user_matches, format_matches, user_friends, user_picture
import json, logging
import os

logger = logging.getLogger('pong')

@require_http_methods(["GET"])
def profile_view(request, username=None):
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
		'rank': user_rank(target_user),
		'status': user_status(target_user),
		'about': user_about(target_user),
		'stats': user_stats(username),
		'matches': formatted_matches,
		'friends': user_friends(target_user),
		'profile_pic': user_picture(target_user)
	}
	logger.info(user_friends(target_user))
	return render(request, 'views/profile-view.html', context)


# @login_required
# @require_http_methods(["GET"])
# def profile(request, username):
# 	logger.info(f"User {request.user.username} requested profile for {username}")

# 	if username is None or not get_user(username):
# 		response_data = profile_data(request.user.username)
# 	else:
# 		response_data = profile_data(username)
# 	return JsonResponse(response_data)

@login_required
@require_http_methods(["PUT"])
def update_profile(request):
	try:
		# Parse the JSON data
		data = json.loads(request.body)

		# Get the current user
		user = request.user

		# Update the user information
		if 'username' in data and data['username'] != user.username:
			# Check if username is available
			if User.objects.filter(username=data['username']).exists():
				return JsonResponse({'error': 'Username already taken'}, status=400)
			user.username = data['username']

		if 'email' in data and data['email'] != user.email:
			# Check if email is available
			if User.objects.filter(email=data['email']).exists():
				return JsonResponse({'error': 'Email already registered'}, status=400)
			user.email = data['email']

		if 'about_me' in data:
			user.about_me = data['about_me']

		# Handle profile picture update
		if 'profile_pic' in data:
			# Store the path relative to the media directory
			profile_pic_path = os.path.join('media/profile-pics', data['profile_pic'])
			user.profile_pic = profile_pic_path
			logger.info(f"Updated profile picture to {profile_pic_path}")

		# Save the changes
		user.save()

		return JsonResponse({'message': 'Profile updated successfully'})

	except json.JSONDecodeError:
		return JsonResponse({'error': 'Invalid JSON data'}, status=400)
	except Exception as e:
		logger.error(f"Error updating profile: {str(e)}")
		return JsonResponse({'error': 'An error occurred while updating the profile'}, status=500)


@login_required
@require_http_methods(["POST"])
def change_password(request):
    try:
        # Parse the JSON data
        data = json.loads(request.body)

        # Get the current user
        user = request.user

        # Check if current password is correct
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return JsonResponse({'error': 'Both current and new passwords are required'}, status=400)

        # Verify current password
        if not user.check_password(current_password):
            return JsonResponse({'error': 'Current password is incorrect'}, status=400)

        # Set new password
        user.set_password(new_password)
        user.save()

        # Update session hash to prevent logout
        update_session_auth_hash(request, user)

        # Return success response
        return JsonResponse({'success': True, 'message': 'Password changed successfully'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return JsonResponse({'error': 'An error occurred while changing the password'}, status=500)


