import { Player, Paddle, Ball, ScoreBoard, GameField } from './SinglePongComponents.js';

export class SinglePongPage extends BaseComponent {
	constructor() {
		super('static/html/singlepong.html');
	}

	async onIni() {
		const element = this.getElementById("game-container");
		if (element) {
			
			this.startButton = this.getElementById("start-button");
			this.startButton.addEventListener("click", () => {
				this.startButton.classList.add('hidden');
				this.startGame();
			});
		}
	}

	async startGame() {
		this.gameField = GameField.createElement(this.getElementById("game-container"));
		this.scoreBoard = new ScoreBoard(this.getElementById("score-board"));
		this.ball = new Ball(this.getElementById("ball"));	
		this.paddle = new Paddle(this.getElementById("paddle"));

		this.player = null; // created only on game start event

		this.socket = new WebSocket(`ws://${window.location.host}/ws/pong/`);
		this.socket.onopen = (event) => {
			console.log(event);
			this.socket.send(JSON.stringify({
				action: "connect"
			}));
		};

		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			const state = data.state;
			
			if (data.event === "game_state") {
				this.paddle.update(state.paddle_y);
				this.scoreBoard.update(state.player1_score, state.player2_score); 
				this.ball.update(state.ball_x, state.ball_y);
			}
			else if (data.event === "game_start") {
				// initialize game components
				this.gameField.update(state.field_width, state.field_height);
				this.paddle.update(state.paddle_y, state.paddle_x, state.paddle_width, state.paddle_height, state.paddle_velo);
				this.scoreBoard.update(state.player1_score, state.player2_score, state.player1_id, state.player2_id);
				this.ball.update(state.ball_x, state.ball_y, state.ball_size, state.ball_size);
				//initialize players
				this.player = new Player(state.player1_id, this.paddle, this.socket);
				this.player.inputManager('w', 's'); // atm depends on game_start event to get paddle velocity
				// otherwise could be called next to the component creation
			}
		};

		this.socket.onclose = (event) => {
			console.log(event);
		};

		this.socket.onerror = (error) => {
			console.log(error);
		};
	}

	onDestroy() {
		if (this.socket) {
			this.socket.close();
		}
		this.player.cleanup();
	}
}

customElements.define('singlepong-page', SinglePongPage);
