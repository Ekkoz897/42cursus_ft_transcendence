import { Player, Paddle, Ball, ScoreBoard, GameField } from './SinglePongComponents.js';


export class SinglePongStartMenu {
	constructor(parent, onStartCall) {
		this.parent = parent;
		this.onStartCall = onStartCall;
	}

	render() {
		const menuDiv = document.createElement('div');
		const startVersus = document.createElement('button');
		const startAi = document.createElement('button');

		menuDiv.classList.add('pong-menu');
		startVersus.textContent = "Start Versus";
		startAi.textContent = "Start AI";

		[startVersus, startAi].forEach(button => {
			button.classList.add('pong-menu-button');
			menuDiv.appendChild(button);
		});	

		startVersus.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			this.onStartCall('vs');
		});

		startAi.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			this.onStartCall('ai');
		});
		
		this.parent.appendChild(menuDiv);
	}
}

export class SinglePongPage extends BaseComponent {
	constructor() {
		super('static/html/singlepong.html');
	}

	async onIni() {
		const element = this.getElementById("game-container");
		if (element) {
			const menu = new SinglePongStartMenu(element, this.startGame.bind(this));
			menu.render();
		}
	}

	async startGame(mode = 'vs') {
		this.socket = new WebSocket(`ws://${window.location.host}/ws/pong/`); // request diferent game types ?
		this.socket.onopen = (event) => {
			console.log(event);
			this.socket.send(JSON.stringify({
				action: "connect",
				mode: mode
			}));

			this.gameField = GameField.createElement(this.getElementById("game-container"));
			this.scoreBoard = new ScoreBoard(this.getElementById("score-board"));
			this.ball = new Ball(this.getElementById("ball"));
			this.paddleLeft = new Paddle(this.getElementById("paddle-left"));
			this.paddleRight = new Paddle(this.getElementById("paddle-right"));
		};

		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			const state = data.state;
			
			if (data.event === "game_state") {
				this.paddleLeft.update(state.l_paddle_y);
				this.paddleRight.update(state.r_paddle_y);
				this.ball.update(state.ball_x, state.ball_y);
			}
			else if (data.event === "score_update") {
				console.log(state);
				this.scoreBoard.update(state.player1_score, state.player2_score, state.player1_sets, state.player2_sets); 
			}
			else if (data.event === "game_start") {
				// initialize game components
				this.gameField.update(state.field_width, state.field_height);
				this.paddleLeft.update(state.l_paddle_y, state.l_paddle_x, state.paddle_width, state.paddle_height);
				this.paddleRight.update(state.r_paddle_y, state.r_paddle_x, state.paddle_width, state.paddle_height);
				this.scoreBoard.update(state.player1_score, state.player2_score, state.player1_sets, state.player2_sets, state.player1_id, state.player2_id);
				this.ball.update(state.ball_x, state.ball_y, state.ball_size, state.ball_size);
				//initialize players
				this.player1 = new Player(state.player1_id, this.paddleLeft, this.socket, "left"); // use id given by server
				this.player1.inputManager('w', 's'); 
				this.player2 = new Player(state.player2_id, this.paddleRight, this.socket, "right"); // use id given by server
				if (mode === 'vs') {
					this.player2.inputManager('ArrowUp', 'ArrowDown'); 
				}
			}

			else if (data.event === "game_end") {
				console.log(state);
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
	}
}

customElements.define('singlepong-page', SinglePongPage);
