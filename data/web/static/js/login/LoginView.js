import { AuthService } from '../index/AuthService.js';

export class LoginView extends BaseComponent {
	constructor() {
		super('/login-view/');
	}

	async onIni() {
		await this.contentLoaded;

		const form = this.getElementById('login-form');
		const errorDiv = this.getElementById('form-errors');
		const login42Button = this.getElementById('login_42');

		form?.addEventListener('submit', async (e) => {
			e.preventDefault();
			errorDiv.textContent = '';

			try {
				const formData = new FormData(form);
				await AuthService.login(
					formData.get('username'),
					formData.get('password'),
				);
			} catch (error) {
				errorDiv.textContent = error.message;
			}
		});

		login42Button?.addEventListener('click', async () => {
			AuthService.login42();
		});

		// Convert password reset link to use SPA routing
		const passwordResetLink = this.querySelector('a[href="/auth/password-reset/"]');
		if (passwordResetLink) {
			passwordResetLink.setAttribute('href', '#/password-reset');
		}
	}
}

customElements.define('login-view', LoginView);
