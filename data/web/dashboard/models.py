from django.db import models
from django.db.models import Q, Count
from backend.models import User
from pong.models import Game, OngoingGame, CompletedGame
from tournaments.models import Tournament
from django.utils import timezone

def get_user(username):
	try:
		user = User.objects.get(username=username)
		return user
	except User.DoesNotExist:
		return None
	
def profile_data(username):
	"""Get all profile data for a user"""
	user = get_user(username)
	if not user:
		return None
	
	matches = user_matches(username)

	profile_data = {
		"username": username,
		"rank": user_rank(user),
		"status": user_status(user),
		"about": user_about(user),
		"stats": user_stats(username),
	        "matches": {
            "history": {
                "p1_games": matches["p1_games"],
                "p2_games": matches["p2_games"]
            }
        },
		"friends": user_friends(user),
        "profile_pic": user_picture(user)
	}

	return profile_data


def user_rank(user):
    return user.rank if user else 0

def user_status(user):
    if not user:
        return "offline"
    return "online" if user.status else "offline"

def user_about(user):
    if not user:
        return {"first_joined": "", "last_seen": ""}
    
    return {
        "first_joined": user.date_joined.strftime("%Y-%m-%d %H:%M:%S") if user.date_joined else "",
        "last_seen": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else ""
    }

def user_stats(username):
    if not username:
        return {"total": 0, "total_w": 0, "total_l": 0}
    
    total_games = CompletedGame.objects.filter(
        Q(player1_username=username) | Q(player2_username=username)
    ).count()
    
    wins = CompletedGame.objects.filter(winner_username=username).count()
    
    return {
        "total": total_games,
        "total_w": wins,
        "total_l": total_games - wins
    }

def user_matches(username, limit=10):
    if not username:
        return {"p1_games": [], "p2_games": []}
    
    p1_games = CompletedGame.objects.filter(
        player1_username=username
    ).order_by('-completed_at')[:limit]
    
    p2_games = CompletedGame.objects.filter(
        player2_username=username
    ).order_by('-completed_at')[:limit]
    
    player1_history = []
    for game in p1_games:
        player1_history.append({
            "game_id": game.game_id,
            "opponent": game.player2_username,
            "result": "win" if game.winner_username == username else "loss",
            "score": f"{game.player1_sets}-{game.player2_sets}",
            "date": game.completed_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    player2_history = []
    for game in p2_games:
        player2_history.append({
            "game_id": game.game_id,
            "opponent": game.player1_username,
            "result": "win" if game.winner_username == username else "loss",
            "score": f"{game.player2_sets}-{game.player1_sets}",
            "date": game.completed_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    player1_history = sorted(player1_history, key=lambda x: x["date"], reverse=True)[:limit]
    player2_history = sorted(player2_history, key=lambda x: x["date"], reverse=True)[:limit]
    
    return {
        "p1_games": player1_history,
        "p2_games": player2_history
    }

def user_friends(user):
    if not user:
        return {"list": []}
    
    friends_list = []
    for friend_username in user.friends:
        friend = get_user(friend_username)
        if friend:
            friends_list.append({
                "username": friend_username,
                "status": "online" if friend.status else "offline"
            })
    
    return {"list": friends_list}

def user_picture(user):
	if not user:
		return None
	return user.profile_pic