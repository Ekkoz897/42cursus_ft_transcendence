import { PongStartMenu, QuickLobby } from './PongComponents.js';
import { SinglePongGame } from './SinglePongGame.js';
export class PongView extends BaseComponent {
	constructor() {
		super('static/html/pong-view.html');
		this.game = null;
	}

	async onIni() {
		const element = this.getElementById("pong-view");
		if (!element) return;

		this.game = new SinglePongGame(element);
		this.lobby = new QuickLobby(element);
		const menu = new PongStartMenu(element, this.game, this.lobby); // game reference could be a return from a start menu method
		menu.render();

	}

	onDestroy() {
		if (this.game) {
			this.game.cleanup();
		}
	}
}

customElements.define('pong-view', PongView);
