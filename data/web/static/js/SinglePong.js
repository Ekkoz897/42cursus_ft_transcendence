class Paddle {
	constructor(element) {
		this.element = element;
		this.y = 0;
	}

	update(y, w, h) {
		this.y = y;
		this.element.style.top = `${this.y}px`;
		this.element.style.width = `${w}px`;
		this.element.style.height = `${h}px`;
	}
}


class Ball {
	constructor(element) {
		this.element = element;
		this.x = 0;
		this.y = 0;
		// element is null 
		
	}

	update(x, y, w, h) {
		// element is null 
		this.x = x;
		this.y = y;
		this.element.style.left = `${this.x}px`;
		this.element.style.top = `${this.y}px`;
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
		this.score = 0;
	}

	update(score) {
		this.score = score;
		this.element.innerText = this.score;
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
			this.scoreBoard = new ScoreBoard(this.getElementById("score"));
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
					this.scoreBoard.update(state.field_score);
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
