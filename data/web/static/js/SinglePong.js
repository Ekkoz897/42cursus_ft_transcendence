class Paddle {
	constructor(element) {
		this.element = element;
		this.velocity = 0;
	}

	update(y, x, w, h, v = this.velocity) {
		this.element.style.top = `${y}px`;
		this.element.style.left = `${x}px`;
		this.element.style.width = `${w}px`;
		this.element.style.height = `${h}px`;
		this.velocity = v;
	}
}
class Ball {
	constructor(element) {
		this.element = element;	
	}

	update(x, y, w, h) {
		this.element.style.left = `${x}px`;
		this.element.style.top = `${y}px`;
		this.element.style.width = `${w}px`;
		this.element.style.height = `${h}px`;
	}
}

class ScoreBoard {
	constructor(element) {
		this.player1Info = element.querySelector("#player1-info");
		this.player2Info = element.querySelector("#player2-info");
		this.playerID = { left: null, right: null };
	}
	
	update(leftScore, rightScore, leftID = this.playerID.left, rightID = this.playerID.right) {
		this.playerID.left = leftID;
		this.playerID.right = rightID;
		this.player1Info.textContent = `${leftID} : ${leftScore}`;
		this.player2Info.textContent = `${rightScore} : ${rightID}`;
	}
}

class GameField {
	constructor(element) {
		this.element = element;
		this.element.classList.add('hidden');
	}

	update(w, h) {
		this.element.style.width = `${w}px`;
		this.element.style.height = `${h}px`;
		
		if (this.element.classList.contains('hidden')) {
			this.element.style.display = 'block';
			void this.element.offsetHeight;
			requestAnimationFrame(() => {
				this.element.classList.remove('hidden');
				this.element.style.opacity = 1;
			});
		}
	}

	static createElement(parent) {
		const gameField = document.createElement('div');
		gameField.id = 'game-field';
		
		const scoreBoard = document.createElement('div');
		scoreBoard.id = 'score-board';
		scoreBoard.innerHTML = `
			<span id="player1-info"></span>
			<span id="separator"> | </span>
			<span id="player2-info"></span>`;
		
		const paddle = document.createElement('div');
		paddle.id = 'paddle';
		
		const ball = document.createElement('div');
		ball.id = 'ball';
		
		gameField.appendChild(scoreBoard);
		gameField.appendChild(paddle);
		gameField.appendChild(ball);
		
		parent.appendChild(gameField);
		return new GameField(gameField);
	}
}

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
		this.paddle = new Paddle(this.getElementById("paddle"));
		this.scoreBoard = new ScoreBoard(this.getElementById("score-board"));
		this.ball = new Ball(this.getElementById("ball"));
		

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
				this.gameField.update(state.field_width, state.field_height);
				this.paddle.update(state.paddle_y, state.paddle_x, state.paddle_width, state.paddle_height, state.paddle_velo);
				this.scoreBoard.update(state.player1_score, state.player2_score, state.player1_id, state.player2_id);
				this.ball.update(state.ball_x, state.ball_y, state.ball_size, state.ball_size);

				this.inputManager(); // depends on game_start event to get paddle velocity
			}
		};

		this.socket.onclose = (event) => {
			console.log(event);
		};

		this.socket.onerror = (error) => {
			console.log(error);
		};
	}

	inputManager() {
		const keys = {
			ArrowUp: false,
			ArrowDown: false
		};
		
		let lastPressed = null;
	
		window.addEventListener("keydown", (e) => {
			if (e.key in keys) {
				keys[e.key] = true;
				lastPressed = e.key;
			}
		});
	
		window.addEventListener("keyup", (e) => {
			if (e.key in keys) {
				keys[e.key] = false;
				if (e.key === lastPressed) {
					lastPressed = keys.ArrowUp ? "ArrowUp" : keys.ArrowDown ? "ArrowDown" : null;
				}
			}
		});
	
		setInterval(() => {
			if (lastPressed === "ArrowUp") {
				this.socket.send(JSON.stringify({
					action: "move_paddle_up"
				}));
			}
			if (lastPressed === "ArrowDown") {
				this.socket.send(JSON.stringify({
					action: "move_paddle_down"
				}));
			}
		}, this.paddle.velocity);
	}

	onDestroy() {
		if (this.socket) {
			this.socket.close();
		}
	}
}

customElements.define('singlepong-page', SinglePongPage);
