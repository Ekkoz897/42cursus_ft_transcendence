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

	destroy() {
		// oposite transition used in update()
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
		
		const leftPaddle = document.createElement('div');
		leftPaddle.id = 'paddle-left';
		
		const rightPaddle = document.createElement('div');
		rightPaddle.id = 'paddle-right';
		
		const ball = document.createElement('div');
		ball.id = 'ball';
		
		gameField.appendChild(scoreBoard);
		gameField.appendChild(leftPaddle);
		gameField.appendChild(rightPaddle);
		gameField.appendChild(ball);
		
		parent.appendChild(gameField);
		return new GameField(gameField);
	}
}

export class PongStartMenu {
	constructor(parent, game, lobby) {
		this.parent = parent;
		this.game = game;
		this.lobby = lobby;
	}

	render() {
		const menuDiv = document.createElement('div');
		const startVersus = document.createElement('button');
		const startAi = document.createElement('button');
		const startQuick = document.createElement('button');
		const startChallenge = document.createElement('button');
		const startTournament = document.createElement('button');

		menuDiv.classList.add('pong-menu');
		startVersus.textContent = "Start Versus";
		startAi.textContent = "Start AI";
		startQuick.textContent = "Quick Match";
		startChallenge.textContent = "Challenge";
		startTournament.textContent = "Tournament";

		[startVersus, startAi, startQuick, startChallenge, startTournament].forEach(button => {
			button.classList.add('pong-menu-button');
			menuDiv.appendChild(button);
		}); 

		startVersus.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			this.game.startGame('vs');
		});

		startAi.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			this.game.startGame('ai');
		});

		startQuick.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			this.lobby.startLobby();
		});

		startChallenge.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			//
		});

		startTournament.addEventListener('click', () => {
			this.parent.removeChild(menuDiv);
			//
		});
		
		this.parent.appendChild(menuDiv);
	}
}

	export class QuickLobby {
		constructor(parent) {
			this.parent = parent;

			this.socket = null;
			this.lobbyElement = null;
		}

		createLobbyElement() {
			const lobbyDiv = document.createElement('div');
			const statusText = document.createElement('div');
			const cancelButton = document.createElement('button');

			lobbyDiv.classList.add('pong-menu');
			statusText.classList.add('lobby-status');
			cancelButton.classList.add('pong-menu-button');

			statusText.textContent = "Searching for opponent...";
			cancelButton.textContent = "Cancel";

			lobbyDiv.appendChild(statusText);
			lobbyDiv.appendChild(cancelButton);
			this.lobbyElement = lobbyDiv;
			this.statusText = statusText;
			this.cancelButton = cancelButton; 
			this.parent.appendChild(lobbyDiv);

			cancelButton.addEventListener('click', () => {
				if (this.socket) {
					this.socket.close();
				}
				this.parent.removeChild(lobbyDiv);

			});
		}

		replaceButton() {
			const readyButton = document.createElement('button');
			readyButton.classList.add('pong-menu-button');
			readyButton.textContent = "Ready!";
			
			this.lobbyElement.removeChild(this.cancelButton);
			this.lobbyElement.appendChild(readyButton);
	
			setTimeout(() => {
				if (this.socket) {
					this.socket.close();
				}
				this.parent.removeChild(this.lobbyElement);
			}, 3000); // 3 seconds delay
		}

		startLobby() {
			this.createLobbyElement();
			this.socket = new WebSocket(`ws://${window.location.host}/ws/mpong/`);
			this.setupSocketHandlers();
		}

		setupSocketHandlers() {
			this.socket.onopen = () => {
				this.socket.send(JSON.stringify({
					action: "connect",
					mode: "quick"
				}));
			};
		
			this.socket.onmessage = (event) => {
				const data = JSON.parse(event.data);
				switch(data.event) {
					case 'player_count':
						this.statusText.textContent = `Players in queue: ${data.state.player_count}`;
						break;
					case 'match_found':
						this.statusText.textContent = 'Match found! Starting game...';
						this.replaceButton();
						break;
				}
				console.log(data);
			};

			this.socket.onclose = () => {
				console.log('Socket closed');
			};

			this.socket.onerror = (error) => {
				console.log('Socket error', error);
			}
		}
	}