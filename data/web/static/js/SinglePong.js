class Paddle {
	constructor(element) {
		this.element = element;
	}

	init(y, w, h) {
		this.element.style.top = `${y}px`;
		this.element.style.width = `${w}px`;
		this.element.style.height = `${h}px`;
	}

	update(y) {
		this.element.style.top = `${y}px`;
	}

	static createElement(id, parent, stateY, width, height) {
		const element = document.createElement("div");
		element.id = id;
		element.classList.add("paddle");
		parent.appendChild(element);
		const paddle = new Paddle(element);
		paddle.init(stateY, width, height);
		return paddle;
	}
}

class Ball {
	constructor(element) {
		this.element = element;
	}

	init(x, y, s) {
		this.element.style.left = `${x}px`;
		this.element.style.top = `${y}px`;
		this.element.style.width = `${s}px`;
		this.element.style.height = `${s}px`;
	}

	update(x, y) {
		this.element.style.left = `${x}px`;
		this.element.style.top = `${y}px`;
	}

	static createElement(parent, stateX, stateY, size) {
		const element = document.createElement("div");
		element.id = "ball";
		element.style.borderRadius = "50%";
		element.style.position = "absolute";
		parent.appendChild(element);
		const ball = new Ball(element);
		ball.init(stateX, stateY, size);
		return ball;
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

	static createElement(parent, width, height) {
		const element = document.createElement("div");
		element.id = "game-field";
		element.style.position = "relative";
		element.style.border = "1px solid black";
		parent.appendChild(element);
		const gameField = new GameField(element);
		gameField.update(width, height);
		return gameField;
	}
}

class ScoreBoard {
	constructor(element) {
		this.element = element;
	}

	update(score) {
		this.element.innerText = score;
	}

	static createElement(parent, score) {
		const element = document.createElement("div");
		element.id = "score";
		element.style.position = "absolute";
		element.style.top = "10px";
		element.style.left = "50%";
		element.style.transform = "translateX(-50%)";
		element.style.fontSize = "24px";
		parent.appendChild(element);
		const scoreBoard = new ScoreBoard(element);
		scoreBoard.update(score);
		return scoreBoard;
	}
}


export class SinglePongPage extends BaseComponent {
		constructor() {
			super("static/html/singlepong.html");
		}

		initGameElements(state) {
			// Create the main game container
			const container = document.getElementById("game-container");

			this.gameField = GameField.createElement(container, state.field_width, state.field_height);
			this.left_paddle = Paddle.createElement(this.gameField.element, "left_paddle", state.left_paddle_y, state.paddle_width, state.paddle_height);
			this.right_paddle = Paddle.createElement(this.gameField.element, "right_paddle", state.right_paddle_y, state.paddle_width, state.paddle_height);
			this.ball = Ball.createElement(this.gameField.element, state.ball_x, state.ball_y, state.ball_size);
			this.scoreBoard = ScoreBoard.createElement(this.gameField.element, state.field_score);

			// Append the entire container to the document body
			document.body.appendChild(container);
		}

	async onIni() {
		const element = this.getElementById("game-container");
		if (element)
		{
			await this.contentLoaded;

			// Set up WebSocket
			this.socket = new WebSocket(`ws://${window.location.host}/ws/pong/`);
			this.socket.onopen = () => {
				this.socket.send(JSON.stringify({ action: "connect" }));
			};

			this.socket.onmessage = (event) => {
					const data = JSON.parse(event.data);
					const state = data.state;

					if (data.event === "init_game")
						this.initGameElements(state);
					else if (data.event === "game_state")
					{
						if (this.left_paddle && this.right_paddle && this.ball && this.scoreBoard)
						{
							this.left_paddle.update(state.left_paddle_y);
							this.right_paddle.update(state.right_paddle_y);
							this.ball.update(state.ball_x, state.ball_y);
							this.scoreBoard.update(state.field_score);
						}
						else
							console.error("Game elements are not properly initialized!");
					}
			};

			// Set up keydown event listener
			window.addEventListener("keydown", (e) => {
				e.preventDefault(); // Prevent default browser actions
				if (e.key === "W")
					this.socket.send(JSON.stringify({ action: "move_left_paddle_up" }));
				else if (e.key === "S")
					this.socket.send(JSON.stringify({ action: "move_left_paddle_down" }));

				if (e.key === "ArrowUp")
					this.socket.send(JSON.stringify({ action: "move_right_paddle_up" }));
				else if (e.key === "ArrowDown")
					this.socket.send(JSON.stringify({ action: "move_right_paddle_down" }));
			});
		}
	}

	onDestroy() {
		if (this.socket) {
			this.socket.close();
		}
	}
}

customElements.define("singlepong-page", SinglePongPage);
