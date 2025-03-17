import { AuthService } from "../index/AuthService.js";
export class ProfileView extends BaseComponent {
	constructor(username = null) {
		super('/profile-view/');
		this.requestedUsername = username;
	}

	async onIni() {
		await this.contentLoaded;
		const element = this.getElementById("profile-view");
		if (!element) return;
		await this.getProfile(this.requestedUsername);
	}

	async getProfile(username) {
		const endpoint = username 
		? `/profile/${encodeURIComponent(username)}/` 
		: `/profile/${encodeURIComponent(AuthService.currentUser)}/`;

		const response = await fetch(endpoint, {
			method: 'GET',
		});
	
		const data = await response.json();
		if (response.ok) {

			console.log(data);
			
		} else {
			const error = new Error(data.error);
			error.status = response.status;
			throw error;
		}
	}

}

customElements.define('profile-view', ProfileView);
