export class Player {
	constructor(id, paddle, socket) {
		this.id = id;
		this.socket = socket;
		this.paddle = paddle;
		this.intervalID = null;
	}

	inputManager(upKey, downKey) {
		let lastPressed = null;
		const keys = {
			[upKey]: false,
			[downKey]: false
		};
		
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
					lastPressed = keys[upKey] ? upKey : keys[downKey] ? downKey : null;
	
				}
			}
		});
	
		this.intervalID = setInterval(() => {
			if (lastPressed === upKey) {
					this.socket.send(JSON.stringify({
					action: "move_paddle_up"
				}));
			}
			if (lastPressed === downKey) {
					this.socket.send(JSON.stringify({
					action: "move_paddle_down"
				}));
			}
		}, this.paddle.velocity); // this value comes from the server but could be tampered with by the client ->
		// solution 1: limit the times move paddle messages are listened to on the server side / 
		// solution 2: create a paddle speed conig/slider so that ALL clients can configure they paddle speed
	}

	cleanup() {
		if (this.intervalID) {
			clearInterval(this.intervalID);
		}
	}
}

export class Paddle {
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
export class Ball {
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

export class ScoreBoard {
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

export class GameField {
	constructor(element) {
		this.element = element;
		this.element.classList.add('hidden');
	}

	update(w, h) {
		this.element.style.width = `${w}px`;
		this.element.style.height = `${h}px`;

		// lame fade in animation :)
		if (this.element.classList.contains('hidden')) {
			this.element.style.display = 'block';
			void this.element.offsetHeight;
			this.element.classList.remove('hidden');
			this.element.style.opacity = 1;
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