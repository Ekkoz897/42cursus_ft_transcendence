import { SinglePongStartMenu } from './PongComponents.js';
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
		const menu = new SinglePongStartMenu(element, this.game);
		menu.render();
	}

	onDestroy() {
		if (this.game) {
			this.game.cleanup();
		}
	}
}

customElements.define('pong-view', PongView);
