import { Player, Paddle, Ball, ScoreBoard, GameField } from './PongComponents.js';

export class QuickLobby {
	constructor(parent, view) {
		this.parent = parent;
		this.view = view;
		this.socket = null;
		this.lobbyElement = null;
	}

	createLobbyElement() {
		const lobbyDiv = document.createElement('div');
		const statusText = document.createElement('div');
		const cancelButton = document.createElement('button');

		lobbyDiv.classList.add('pong-menu');
		statusText.classList.add('lobby-status');
		cancelButton.classList.add('pong-menu-button');

		statusText.textContent = "Searching for opponent...";
		cancelButton.textContent = "Cancel";

		lobbyDiv.appendChild(statusText);
		lobbyDiv.appendChild(cancelButton);
		this.lobbyElement = lobbyDiv;
		this.statusText = statusText;
		this.cancelButton = cancelButton; 
		this.parent.appendChild(lobbyDiv);

		cancelButton.addEventListener('click', () => {
			if (this.socket) {
				this.socket.close();
			}
			this.parent.removeChild(lobbyDiv);
			this.refreshView();
		});
		
	}

	startLobby() {
		this.createLobbyElement();
		this.socket = new WebSocket(`wss://${window.location.host}/wss/mpong/`);
		this.setupSocketHandlers();
	}

	setupSocketHandlers() {
		this.socket.onopen = () => {
			this.socket.send(JSON.stringify({
				action: "connect",
			}));
		};
	
		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			switch(data.event) {
				case 'player_count':
					this.statusText.textContent = `Players in queue: ${data.state.player_count}`;
					break;
				case 'match_found':
					this.statusText.textContent = 'Match found! Starting game...';
					this.parent.removeChild(this.lobbyElement);
					const game = new MultiPongGame(this.parent, data.state, this.view);
					game.startGame();
					break;
			}
			console.log("lobby socket data", data);
		};

		this.socket.onclose = () => {
			console.log('Lobby Socket closed');
		};

		this.socket.onerror = (error) => {
			console.log('Socket error', error);
		}
	}

	refreshView() {
		window.location.reload();
	}
}

export class TournamentLobby extends QuickLobby {
    constructor(parent, view, gameId) {
        super(parent, view);
        this.gameId = gameId;
    }
    
	createLobbyElement() {
		super.createLobbyElement();
		this.lobbyElement.removeChild(this.cancelButton);
	}

    startLobby() {
        this.createLobbyElement(); 
        this.socket = new WebSocket(`wss://${window.location.host}/wss/mpong/tournament/${this.gameId}/`);
        this.setupSocketHandlers(); 
    }
}
export class PongGame {
	constructor(container, view) {
		this.container = container;
		this.view = view;
		this.socket = null;
		this.gameField = null;
		this.scoreBoard = null;
		this.ball = null;
		this.paddleLeft = null;
		this.paddleRight = null;
		this.player1 = null;
		this.player2 = null;
		this.view.registerGame(this);
	}

	setupSocketHandlers() {
		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			this.handleGameEvent(data.event, data.state);
		};
		this.socket.onopen = () => console.log("Game socket opened");
		this.socket.onclose = (event) => console.log("Game socket closed");
		this.socket.onerror = (error) => console.log(error);
	}

	createGameElements() {
		this.gameField = GameField.createElement(this.container);
		this.scoreBoard = new ScoreBoard(document.getElementById("score-board"));
		this.ball = new Ball(document.getElementById("ball"));
		this.paddleLeft = new Paddle(document.getElementById("paddle-left"));
		this.paddleRight = new Paddle(document.getElementById("paddle-right"));
	}

	handleGameEvent(event, state) {
		switch(event) {
			case "game_state":
				this.updateGameState(state);
				break;
			case "score_update":
				this.updateScore(state);
				break;
			case "game_start":
				this.handleGameStart(state);
				break;
			case "game_end":
				console.log(state);
				break;
		}
	}

	updateGameState(state) {
		this.paddleLeft.update(state.l_paddle_y);
		this.paddleRight.update(state.r_paddle_y);
		this.ball.update(state.ball_x, state.ball_y);
	}

	updateScore(state) {
		this.scoreBoard.update(
			state.player1_score,
			state.player2_score,
			state.player1_sets,
			state.player2_sets
		);
	}

	handleGameStart(state) {
		this.createGameElements();
		this.gameField.update(state.field_width, state.field_height);
		this.paddleLeft.update(state.l_paddle_y, state.l_paddle_x, state.paddle_width, state.paddle_height);
		this.paddleRight.update(state.r_paddle_y, state.r_paddle_x, state.paddle_width, state.paddle_height);
		this.scoreBoard.update(
			state.player1_score, 
			state.player2_score, 
			state.player1_sets, 
			state.player2_sets,
			state.player1_id,
			state.player2_id
		);
		this.ball.update(state.ball_x, state.ball_y, state.ball_size, state.ball_size);
		this.setupPlayers(state);
		console.log("Game started!");
	}

	setupPlayers(state) {
		throw new Error("Method 'setupPlayers' must be implemented");
	}

	cleanup() {
		if (this.socket) this.socket.close();
		if (this.player1) this.player1.remove();
		if (this.player2) this.player2.remove();
		if (this.gameField) this.gameField.destroy();
		this.view.unregisterGame(this);
	}
}

export class AIPongGame extends PongGame {
	constructor(container, view) {
		super(container, view);
		this.trainingMode = null;  // Will be set from the server
	}

	async startGame() {
		this.socket = new WebSocket(`wss://${window.location.host}/wss/aipong/`);
		this.setupSocketHandlers();
		this.socket.onopen = () => {
			this.socket.send(JSON.stringify({
				action: "connect",
			}));
		};
	}

	setupPlayers(state) {
		this.player1 = new Player(state.player1_id, this.paddleLeft, this.socket, "left");
		this.player2 = new Player(state.player2_id, this.paddleRight, this.socket, "right");

		this.player1.inputManager('w', 's');
	}
}

export class SinglePongGame extends PongGame {
	constructor(container, view) {
		super(container, view);
		this.mode = 'vs';
	}

	async startGame(mode = 'vs') {
		this.mode = mode;
		this.socket = new WebSocket(`wss://${window.location.host}/wss/spong/`);
		this.setupSocketHandlers();
		this.socket.onopen = () => {
			this.socket.send(JSON.stringify({
				action: "connect",
				mode: this.mode
			}));
		};
	}

	setupPlayers(state) {
		this.player1 = new Player(state.player1_id, this.paddleLeft, this.socket, "left");
		this.player2 = new Player(state.player2_id, this.paddleRight, this.socket, "right");
		this.player1.inputManager('w', 's');
		if (this.mode === 'vs') {
			this.player2.inputManager('ArrowUp', 'ArrowDown');
		}
	}
}


export class MultiPongGame extends PongGame {
	constructor(container, matchData, view) {
		super(container, view);
		this.game_id = matchData.game_id;
		this.game_url = matchData.game_url;
		this.player_id = matchData.player1_id;
		console.log("Match data", matchData);
	}

	async startGame() {
		this.socket = new WebSocket(`wss://${window.location.host}/${this.game_url}`);
		this.setupSocketHandlers();
		
		this.socket.onopen = () => {
			this.socket.send(JSON.stringify({
				action: "connect"
			}));
		};
	}

	setupPlayers(state) {
		this.selfKeys = ['w', 's'];
		this.player1 = new Player(state.player1_id, this.paddleLeft, this.socket, "left");
		this.player2 = new Player(state.player2_id, this.paddleRight, this.socket, "right");
		(this.player_id === state.player1_id
			? this.player1.inputManager(this.selfKeys[0], this.selfKeys[1])
			: this.player2.inputManager(this.selfKeys[0], this.selfKeys[1]));
	}
}

