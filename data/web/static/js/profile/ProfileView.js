export class ProfileView extends BaseComponent {
	constructor() {
		super('/profile-view/');
	}

	async onIni() {
		await this.contentLoaded;
		const element = this.getElementById("profile-view");
		if (!element) return;
	}
}

customElements.define('profile-view', ProfileView);
