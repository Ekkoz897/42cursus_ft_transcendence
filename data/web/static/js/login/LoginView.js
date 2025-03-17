import { AuthService } from '../index/AuthService.js';

export class LoginView extends BaseComponent {
	constructor() {
		super('/login-view/');
		this.host = null;
	}

	async onIni() {
		// if (AuthService.isAuthenticated) {
		// 	window.location.hash = '#/home';
		// 	return;
		// }
		
		const form = this.getElementById('login-form');
		const errorDiv = this.getElementById('form-errors');
		const login42Button = this.getElementById('login_42');

		await this.fetchHost();

		form?.addEventListener('submit', async (e) => {
			e.preventDefault();
			errorDiv.textContent = '';
			
			try {
				const formData = new FormData(form);
				await AuthService.login(
					formData.get('username'),
					formData.get('password'),
				);
				window.location.hash = '#/home';
			} catch (error) {
				errorDiv.textContent = error.message;			
			}
		});

		login42Button?.addEventListener('click', async () => {
			// Use the same host but with explicit port if it's localhost
			// const host = `10.12.5.6:4443`;
			const host = this.host;
			const redirectUri = encodeURIComponent(`https://${host}/oauth/callback/`);
			//console.log("Using redirect URI:", `https://${host}/oauth/callback/`);
			window.location.href = `https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-f8562a1795538b5f2a9185781d374e1152c6466501442d50530025b059fe92ad&redirect_uri=${redirectUri}&response_type=code`;
		});
	}


	async fetchHost() {
		const response = await fetch('/get-host/', {
			method: 'GET',
		});
		const data = await response.json();
		this.host = data.host;
	}
}

customElements.define('login-view', LoginView);
