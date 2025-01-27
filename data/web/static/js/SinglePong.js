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

	update(leftID, leftScore, rightScore,rightID) {
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

			this.gameField = new GameField(this.getElementById("game-field"));
			this.paddle = new Paddle(this.getElementById("paddle"));
			this.scoreBoard = new ScoreBoard(this.getElementById("score-board"));
			this.ball = new Ball(this.getElementById("ball"));

			this.socket = new WebSocket(`ws://${window.location.host}/ws/pong/`);
			this.socket.onopen = () => {
				this.socket.send(JSON.stringify({
					action: "connect"
				}));
			};
			this.socket.onmessage = (event) => {
				const data = JSON.parse(event.data);
				if (data.event === "game_state") {
					const state = data.state;
					this.gameField.update(state.field_width, state.field_height);
					this.paddle.update(state.paddle_y, state.paddle_width, state.paddle_height);
					this.scoreBoard.update(state.player1_id, state.player1_score, "AI", "0");
					this.ball.update(state.ball_x, state.ball_y, state.ball_size, state.ball_size);
				}
			};

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

			// this.socket.onclose = (event) => {
				
			// };

			// this.socket.onerror = (error) => {
				
			// };

		}
	}

	onDestroy() {
		if (this.socket) {
			this.socket.close();
		}
	}
}

customElements.define('singlepong-page', SinglePongPage);
