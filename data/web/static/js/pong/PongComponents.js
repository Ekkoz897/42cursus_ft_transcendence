import * as THREE from 'three';
export class Player {
	constructor(id, paddle, socket, side) {
		this.id = id;
		this.socket = socket;
		this.paddle = paddle;
		this.intervalID = null;
		this.side = side; // redundant for mp
		this.keydownListener = null;
		this.keyupListener = null;
	}

	inputManager(upKey, downKey) {
		let lastPressed = null;
		const keys = {
			[upKey]: false,
			[downKey]: false
		};
	
		this.keydownListener = (e) => {
			if (e.key in keys && !keys[e.key]) {
				keys[e.key] = true;
				lastPressed = e.key;
				this.socket.send(JSON.stringify({
					action: "paddle_move_start",
					direction: e.key === upKey ? "up" : "down",
					side: this.side
				}));
			}
		};

		this.keyupListener = (e) => {
			if (e.key in keys) {
				keys[e.key] = false;
				if (e.key === lastPressed) {
					lastPressed = keys[upKey] ? upKey : keys[downKey] ? downKey : null;
				}
				this.socket.send(JSON.stringify({
					action: keys[upKey] || keys[downKey] ? "paddle_move_start" : "paddle_move_stop",
					direction: lastPressed === upKey ? "up" : lastPressed === downKey ? "down" : e.key === upKey ? "up" : "down",
					side: this.side
				}));
			}
		};

        window.addEventListener("keydown", this.keydownListener);
        window.addEventListener("keyup", this.keyupListener);
    }

	remove() {
		if (this.keydownListener) {
			window.removeEventListener("keydown", this.keydownListener);
		}
		if (this.keyupListener) {
			window.removeEventListener("keyup", this.keyupListener);
		}
	}
	
}

export class AiOpponent extends Player {
	constructor(id, paddle, socket, side) {
		super(id, paddle, socket, side);
		this.intervalID = null;
	}

	inputManager() {
		//pass
	}

	removeInputManager() {
		//pass
	}
}

export class Paddle {
	constructor(element) {
		this.element = element;
	}

	update(y, x, w, h) {
		this.element.style.top = `${y}px`;
		this.element.style.left = `${x}px`;
		this.element.style.width = `${w}px`;
		this.element.style.height = `${h}px`;
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
	
	update(leftScore, rightScore, leftSets, rightSets, leftID = this.playerID.left, rightID = this.playerID.right) {
		this.playerID.left = leftID;
		this.playerID.right = rightID;
		this.player1Info.textContent = `${leftID} : ${leftSets} : ${leftScore}`;
		this.player2Info.textContent = `${rightScore} : ${rightSets} : ${rightID}`;
	}
}

export class GameField {
    constructor(element) {
        this.field = element;
        // this.field.classList.add('hidden');
    }

    update(w, h) {
        this.field.style.width = `${w}px`;
        this.field.style.height = `${h}px`;

        // if (this.field.classList.contains('hidden')) {
        //     this.field.style.display = 'block';
        //     void this.field.offsetHeight;
        //     this.field.classList.remove('hidden');
        //     this.field.style.opacity = 1;
        // }
    }
}
