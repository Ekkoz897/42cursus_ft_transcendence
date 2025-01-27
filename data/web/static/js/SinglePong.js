class Paddle {
	constructor(element) {
		this.element = element;
	}

	update(y, w, h) {
		this.element.style.top = `${y}px`;
		this.element.style.width = `${w}px`;
		this.element.style.height = `${h}px`;
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

class GameField {
	constructor(element) {
		this.element = element;

	}

	update(w, h) {
		this.element.style.width = `${w}px`;
		this.element.style.height = `${h}px`;
	}
}

class ScoreBoard {
	constructor(element) {
		this.element = element;
		this.player1Info = element.querySelector("#player1-info");
		this.player2Info = element.querySelector("#player2-info");
		this.leftPlayerID = null;
		this.leftPlayerScore = 0;
		this.rightPlayerID = null;
		this.rightPlayerScore = 0;
	}

	update(leftScore, rightScore, leftID, rightID) {
		this.leftPlayerScore = leftScore;
		this.rightPlayerScore = rightScore;
		this.leftPlayerID = leftID;
		this.rightPlayerID = rightID;

		this.player1Info.textContent = `${this.leftPlayerID} : ${this.leftPlayerScore}`;
		this.player2Info.textContent = `${this.rightPlayerScore} : ${this.rightPlayerID}`;
	}
}

export class SinglePongPage extends BaseComponent {
	constructor() {
		super('static/html/singlepong.html');
	}

	async onIni() {
		const element = this.getElementById("game-container");
		if (element) {
			await this.contentLoaded;

			this.startButton = this.getElementById("start-button");
			
			this.startButton.addEventListener("click", () => {
				this.startButton.classList.add('hidden');
				this.createGameField();
				this.startGame();
			});

		}
	}

	createGameField() {
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
		
		this.getElementById("game-container").appendChild(gameField);
	}

	async startGame() {
		this.gameField = new GameField(this.getElementById("game-field"));
		this.paddle = new Paddle(this.getElementById("paddle"));
		this.scoreBoard = new ScoreBoard(this.getElementById("score-board"));
		this.ball = new Ball(this.getElementById("ball"));
		this.inputManager();

		this.socket = new WebSocket(`ws://${window.location.host}/ws/pong/`);
		this.socket.onopen = (event) => {
			this.socket.send(JSON.stringify({
				action: "connect"
			}));
			console.log("on socket open triggered", event);
		};

		this.socket.onmessage = (event) => {
			const data = JSON.parse(event.data);
			const state = data.state;
			// create separate init and update methods to use in game_state and game_start
			if (data.event === "game_state") {
				this.paddle.update(state.paddle_y);
				this.scoreBoard.update(state.player1_score, state.player2_score, this.scoreBoard.leftPlayerID, this.scoreBoard.rightPlayerID); 
				this.ball.update(state.ball_x, state.ball_y);
			}
			else if (data.event === "game_start") {
				this.gameField.update(state.field_width, state.field_height);
				this.paddle.update(state.paddle_y, state.paddle_width, state.paddle_height);
				this.scoreBoard.update(state.player1_score, state.player2_score, state.player1_id, state.player2_id);
				this.ball.update(state.ball_x, state.ball_y, state.ball_size, state.ball_size);
			}
		};

		this.socket.onclose = (event) => {
			console.log("on socket close triggered", event);
		};

		this.socket.onerror = (error) => {
			console.log("on socket error triggered", error);
		};
	}

	inputManager() {
		window.addEventListener("keydown", (e) => {
			//e.preventDefault();
			if (e.key === "ArrowUp") {
				this.socket.send(JSON.stringify({
					action: "move_paddle_up",
				}));

			} else if (e.key === "ArrowDown") {
				this.socket.send(JSON.stringify({
					action: "move_paddle_down",
				}));
			}
		});
	}

	onDestroy() {
		if (this.socket) {
			this.socket.close();
			console.log("on destroy called socket.close()");
		}
	}
}

customElements.define('singlepong-page', SinglePongPage);
