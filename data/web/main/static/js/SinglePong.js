export class SinglePongPage extends BaseComponent {
    constructor() {
        super('static/html/singlepong.html');
    }

    async onIni() {
        const element = this.getElementById("game-container");
        if (element) {
            this.paddle = this.getElementById("paddle");
            this.gameField = this.getElementById("game-field");
            this.scoreElement = this.getElementById("score");
            this.currentPaddleY = 250;

			const socket = new WebSocket(`ws://ws/pong/`);
            
			socket.onopen = () => {
				socket.send(JSON.stringify({
					action: "connect"
				}));
			};

            socket.onclose = (event) => {
                
            };

            socket.onerror = (error) => {
                
            };

            socket.onmessage = (event) => {
                console.log('Message received:', event.data);
                const data = JSON.parse(event.data);
                if (data.event === "game_state") {
                    const state = data.state;
                    console.log('Paddle position:', state.paddle_y);
                }
            };
			
			this.socket = socket;
			this.currentPaddleY = 250;
            
			window.addEventListener("keydown", (e) => {
				if (e.key === "ArrowUp") {
					socket.send(JSON.stringify({
						action: "move_paddle",
						paddle_y: Math.max(0, this.currentPaddleY - 10)
					}));
				} else if (e.key === "ArrowDown") {
					socket.send(JSON.stringify({
						action: "move_paddle",
						paddle_y: Math.min(500, this.currentPaddleY + 10)
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