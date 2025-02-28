import { AuthService } from '../index/AuthService.js';
import { MultiPongGame, TournamentLobby } from './SinglePongGame.js';

export class TournamentView extends BaseComponent {
	constructor() {
		super('/tournament-view/');
		this.errorDiv = null;
		this.activeGames = new Set();
	}

	async onIni() {
		const element = this.getElementById("tournament-view");
		if (!element) return;

		this.errorDiv = this.getElementById('tournament-errors');
		this.setupEventListeners();
		await this.fetchTournaments();
        this.pollInterval = setInterval(() => this.fetchTournaments(), 5000);
	}


	registerGame(game) {
		this.activeGames.add(game);
	}


	unregisterGame(game) {
		this.activeGames.delete(game);
	}


	onDestroy() {
		for (const game of this.activeGames) {
			game.cleanup();
		}
		this.activeGames.clear();
		clearInterval(this.pollInterval);
	}


	setupEventListeners() {
		const createBtn = this.getElementById("create-tournament");
		const joinBtn = this.getElementById("join-tournament");
		const leaveBtn = this.getElementById("leave-tournament");

		createBtn?.addEventListener('click', () => this.createTournament());
		joinBtn?.addEventListener('click', () => this.joinTournament());
		leaveBtn?.addEventListener('click', () => this.leaveTournament());
	}


	async fetchTournaments() {
		const response = await fetch('/tournament-view/list/', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		const data = await response.json();
		const stateDiv = this.getElementById("tournament-state");
		if (!stateDiv) {
			console.error("Tournament state element not found");
			return;
		}
		
		if (data.in_tournament && data.current_tournament) {
			const t = data.current_tournament;
			
			// create tournament state HTML
			let stateHTML = `
				<div>Tournament ID: ${data.current_tournament_id}</div>
				<div>Status: ${t.status}</div>
				${t.status === 'IN_PROGRESS' ? `<div>Round: ${t.current_round + 1}</div>` : ''}
				<div>Players: ${t.players.join(', ')}</div>
			`;
			
			// add section for current matches if tournament is in progress
			if (t.status === 'IN_PROGRESS' && t.rounds.length > 0 && t.current_round < t.rounds.length) {
				const currentRoundMatches = t.rounds[t.current_round];
				
				stateHTML += `<h3>Current Round Matches</h3>`;
				stateHTML += `<div class="tournament-matches">`;
				
				// display each match in the current round
				currentRoundMatches.forEach(match => {
					let matchHTML = `
						<div class="tournament-match ${match.status.toLowerCase()}">
							<div class="match-players">
								${match.player1 || 'TBD'} vs ${match.player2 || 'TBD'}
							</div>
							<div class="match-status">
								${match.status !== 'PENDING' ? `Status: ${match.status}` : ''}
								${match.winner ? `Winner: ${match.winner}` : ''}
							</div>
					`;
					
					// add join button for player's own matches that are still pending
					if (match.is_player_match && match.status === 'PENDING') {
						matchHTML += `
							<button class="join-match-button tournament-button" 
									data-game-id="${match.game_id}">
								Join Match
							</button>
						`;
					}
					
					matchHTML += `</div>`;
					stateHTML += matchHTML;
				});
				
				stateHTML += `</div>`;
			}
			
			stateDiv.innerHTML = stateHTML;
			
			// add event listeners to join match buttons
			this.getElementById("tournament-state")?.querySelectorAll('.join-match-button').forEach(button => {
				button.addEventListener('click', () => {
					const gameId = button.dataset.gameId;
					console.log(`Join button clicked for game ID: ${gameId}`);
					this.joinTournamentMatch(gameId);
				});
			});
		} else {
			stateDiv.innerHTML = 'Not in tournament';
		}
		
		this.updateTournamentsList(data.tournaments);
	}
	


	updateTournamentsList(tournaments) {
		const container = this.getElementById("tournaments-container");
		if (!container) return;
	
		if (!tournaments || tournaments.length === 0) {
			container.innerHTML = '<div class="no-tournaments">No active tournaments</div>';
			return;
		}
	
		container.innerHTML = tournaments.map(t => `
			<div class="tournament-item" data-tournament-id="${t.tournament_id}">
				<div class="tournament-info">
					<span>ID: ${t.tournament_id}</span>
					<span>Status: ${t.status}</span>
					<span>Players: ${t.player_count}/${t.max_players}</span>
				</div>
			</div>
		`).join('');
	

		container.querySelectorAll('.tournament-item').forEach(item => {
			item.addEventListener('click', () => {
				item.classList.add('selected');
			});
		});
	}


	async createTournament() {
		this.clearError();
		const response = await fetch('tournament-view/create/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': AuthService.getCsrfToken(),
			},
			body: JSON.stringify({
				action: 'create'
			})
		});
		
		if (response.ok) {
			await this.fetchTournaments();
		}

		const data = await response.json();
		if (!this.handleError(response, data)) {
			await this.fetchTournaments();
		}
	}


	async joinTournament() {
		this.clearError();
		const selectedRow = this.getElementById("tournaments-container")?.querySelector('.selected');
		if (!selectedRow) return;
	
		const tournamentId = selectedRow.dataset.tournamentId;
		const response = await fetch('tournament-view/join/', {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': AuthService.getCsrfToken(),
			},
			body: JSON.stringify({
				tournament_id: tournamentId
			})
		});
		
		const data = await response.json();
		if (!this.handleError(response, data)) {
			await this.fetchTournaments();
		}
	}


	async leaveTournament() {
		this.clearError();
		const response = await fetch('tournament-view/leave/', {
			method: 'DELETE',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': AuthService.getCsrfToken(),
			}
		});
		
		const data = await response.json();
		if (!this.handleError(response, data)) {
			await this.fetchTournaments();
		}
	}

	async joinTournamentMatch(gameId) {
		console.log(`Joining tournament match with game ID: ${gameId}`);
		const container = document.querySelector(".tournament-container");
		const tournamentLobby = new TournamentLobby(container, this, gameId);
		tournamentLobby.startLobby();
	}

	clearError() {
		if (this.errorDiv) {
			this.errorDiv.textContent = '';
		}
	}


	handleError(response, data) {
		if (!response.ok && this.errorDiv) {
			this.errorDiv.textContent = data.message;
			return true;
		}
		return false;
	}

}

customElements.define('tournament-view', TournamentView);