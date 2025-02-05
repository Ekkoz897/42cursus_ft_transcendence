export class HomeView extends BaseComponent {
	constructor() {
		super('static/html/home-view.html');
	}

	async onIni() {
		const element = this.getElementById("home-view");
		if (element) {
			// Initialize home view
		}
	}
}

customElements.define('home-view', HomeView);