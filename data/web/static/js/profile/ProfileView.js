import { AuthService } from "../index/AuthService.js";
export class ProfileView extends BaseComponent {
	constructor(username = null) {
		if (username) 
			super(`/profile-view/${encodeURIComponent(username)}/`);
		else
			super('/profile-view/');
		this.requestedUsername = username;
	}

	async onIni() {
		await this.contentLoaded;
		const element = this.getElementById("profile-view");
		if (!element) return;

		// const friendButton = this.querySelector('#friend-button');
		// if (friendButton) {
		// 	friendButton.addEventListener('click', async () => {
				
		// 		const response = await fetch('/friend-request/', {
		// 			method: 'PUT',
		// 			headers: {
		// 				'Content-Type': 'application/json',
		// 				'X-CSRFToken': AuthService.getCsrfToken(),
		// 			},
		// 			body: JSON.stringify({Data_1: "friend", Data_2: "request"}),
		// 		});

		// 	});
		// }


	}
}

customElements.define('profile-view', ProfileView);
