from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Tournament
import json, time, secrets

def generate_tournament_id() -> str:
	timestamp = int(time.time())
	token = secrets.token_hex(4)
	return f"t:{timestamp}:{token}"


@login_required
@require_http_methods(["POST"])
def tournament_create(request):
	if Tournament.player_in_tournament(request.user.username):
		return JsonResponse({
			'status': 'error',
			'message': 'You are already in a tournament'
		}, status=400)

	tournament_id = generate_tournament_id()
	tournament = Tournament.create_tournament(
		tournament_id=tournament_id,
		players=[request.user.username]
	)
	
	return JsonResponse({
		'status': 'created',
		'tournament_id': tournament_id
	})


@login_required
@require_http_methods(["DELETE"])
def tournament_leave(request):
	tournament = Tournament.objects.filter(
		players__contains=[request.user.username],
		status__in=['REGISTERING', 'IN_PROGRESS']
	).first()

	if tournament and tournament.status == 'IN_PROGRESS':
		return JsonResponse({
			'status': 'error',
			'message': 'You cannot leave a tournament in progress'
		}, status=400)

	if not tournament:
		return JsonResponse({
			'status': 'error',
			'message': 'You are not in a tournament'
		}, status=400)

	tournament.players = [p for p in tournament.players if p != request.user.username]
	
	if not tournament.players:
		tournament.delete()
		return JsonResponse({'status': 'tournament_deleted'})
	
	tournament.save()
	return JsonResponse({'status': 'left'})


@login_required
@require_http_methods(["PUT"])
def tournament_join(request):
	data = json.loads(request.body)
	tournament_id = data.get('tournament_id')

	if Tournament.player_in_tournament(request.user.username):
		return JsonResponse({
			'status': 'error',
			'message': 'You are already in a tournament'
		}, status=400)

	tournament = Tournament.objects.filter(tournament_id=tournament_id).first()
	if not tournament:
		return JsonResponse({
			'status': 'error',
			'message': 'Tournament not found'
		}, status=404)
		
	if tournament.status != 'REGISTERING':
		return JsonResponse({
			'status': 'error',
			'message': 'Tournament not accepting players'
		}, status=400)


	tournament.players = tournament.players + [request.user.username]
	
	if len(tournament.players) >= tournament.max_players:
		tournament.start_tournament()
	else:
		tournament.save()
	
	return JsonResponse({
		'status': 'joined',
		'tournament_id': tournament_id,
	})


@login_required
@require_http_methods(["GET"])
def tournament_list(request):
	user_tournament = Tournament.objects.filter(
		players__contains=[request.user.username],
		status__in=['REGISTERING', 'IN_PROGRESS']
	).first()

	tournaments = Tournament.objects.filter(
		status__in=['REGISTERING', 'IN_PROGRESS']
	).order_by('-created_at')

	return JsonResponse({
		'in_tournament': bool(user_tournament),
		'current_tournament_id': user_tournament.tournament_id if user_tournament else None,
		'current_tournament': {
			'players': user_tournament.players if user_tournament else [],
			'current_round': user_tournament.current_round if user_tournament else None,
			'rounds': user_tournament.rounds if user_tournament else [],
			'status': user_tournament.status if user_tournament else None
		} if user_tournament else None,
		'tournaments': [{
			'tournament_id': t.tournament_id,
			'status': t.status,
			'player_count': len(t.players),
			'max_players': t.max_players
		} for t in tournaments]
	})
