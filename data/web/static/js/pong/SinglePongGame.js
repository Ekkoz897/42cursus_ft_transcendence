import { Player, Paddle, Ball, ScoreBoard, GameField } from './PongComponents.js';

export class SinglePongGame {
	constructor(container) {
		this.container = container;
		this.socket = null;
		this.gameField = null;
		this.scoreBoard = null;
		this.ball = null;
		this.paddleLeft = null;
		this.paddleRight = null;
		this.player1 = null;
		this.player2 = null;
	}

	async startGame(mode = 'vs') {
		this.mode = mode;
		this.socket = new WebSocket(`ws://${window.location.host}/ws/pong/`);
		this.setupSocketHandlers();
	}

	setupSocketHandlers() {
		this.socket.onopen = (event) => {
			console.log(event);
			this.socket.send(JSON.stringify({
				action: "connect",
				mode: this.mode
			}));
			this.createGameElements();
		};
		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			const state = data.state;
			this.handleGameEvent(data.event, state);
		};
		this.socket.onclose = (event) => console.log(event);
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
		this.gameField.update(state.field_width, state.field_height);
		this.paddleLeft.update(state.l_paddle_y, state.l_paddle_x, state.paddle_width, state.paddle_height);
		this.paddleRight.update(state.r_paddle_y, state.r_paddle_x, state.paddle_width, state.paddle_height);
		this.scoreBoard.update(state.player1_score, state.player2_score, state.player1_sets, state.player2_sets,
			state.player1_id,
			state.player2_id
		);
		this.ball.update(state.ball_x, state.ball_y, state.ball_size, state.ball_size);
		this.player1 = new Player(state.player1_id, this.paddleLeft, this.socket, "left");
		this.player1.inputManager('w', 's');
		this.player2 = new Player(state.player2_id, this.paddleRight, this.socket, "right");
		if (this.mode === 'vs') {
			this.player2.inputManager('ArrowUp', 'ArrowDown');
		}
	}

	cleanup() {
		if (this.socket) this.socket.close();
		if (this.player1) this.player1.remove();
		if (this.player2) this.player2.remove();
	}
}