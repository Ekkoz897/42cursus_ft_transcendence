export class ProfileView extends BaseComponent {
	constructor() {
		super('static/html/profile-view.html');
	}

	async onIni() {
		const element = this.getElementById("profile-view");
		if (element) {
			// Initialize profile view
		}
	}
}

customElements.define('profile-view', ProfileView);
