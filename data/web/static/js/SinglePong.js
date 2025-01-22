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

class GanmeField {
	constructor(element) {
		this.element = element;
		this.width = 0;
		this.height = 0;
	}

	update(w, h) {
		this.width = w;
		this.height = h;
		this.element.style.width = `${this.width}px`;
		this.element.style.height = `${this.height}px`;
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

			this.paddle = new Paddle(this.getElementById("paddle"));
			this.gameField = new GanmeField(this.getElementById("game-field"));
			this.scoreBoard = new ScoreBoard(this.getElementById("score"));
			
			const socket = new WebSocket(`ws://${window.location.host}/ws/pong/`);
			
			
			socket.onopen = () => {
				socket.send(JSON.stringify({
					action: "connect"
				}));
			};

			socket.onmessage = (event) => {
				console.log('Message received:', event.data);
				const data = JSON.parse(event.data);
				if (data.event === "game_state") {
					const state = data.state;
					this.gameField.update(state.field_width, state.field_height);
					this.paddle.update(state.paddle_y, state.paddle_width, state.paddle_height);
					this.scoreBoard.update(state.field_score);
				}
			};

			// socket.onclose = (event) => {
				
			// };

			// socket.onerror = (error) => {
				
			// };

			window.addEventListener("keydown", (e) => {
				//e.preventDefault();
				if (e.key === "ArrowUp") {
					socket.send(JSON.stringify({
						action: "move_paddle_up",
					}));
	
				} else if (e.key === "ArrowDown") {
					socket.send(JSON.stringify({
						action: "move_paddle_down",
					}));
				}
			});
		}
	}

	onDestroy() {
		if (this.socket) {
			this.socket.close();
		}
	}
}

customElements.define('singlepong-page', SinglePongPage);


// this.heartbeatInterval = setInterval(() => {
// 	if (socket.readyState === WebSocket.OPEN) {
// 		socket.send(JSON.stringify({
// 			action: "heartbeat"
// 		}));
// 	}
// }, 30000); // Send heartbeat every 30 seconds

// socket.onclose = (event) => {
// 	console.log("WebSocket closed:", event);
// 	clearInterval(this.heartbeatInterval);
// };