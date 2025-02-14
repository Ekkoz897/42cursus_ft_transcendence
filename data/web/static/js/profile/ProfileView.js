export class ProfileView extends BaseComponent {
	constructor() {
		super('static/html/profile-view.html'); // Keep the correct file name
	}

	async onIni() {
		console.log("Profile Page Loaded");

		// Ensure only the login modal is added (not the login menu)
		const content = document.getElementById("profile-view");
		if (content && !content.querySelector("login-modal")) {
			const loginModal = document.createElement('login-modal');
			content.appendChild(loginModal);
		}
	}
}

customElements.define('profile-view', ProfileView);
