import { AuthService } from '../index/AuthService.js';

export class PassResetConfirmView extends BaseComponent {
	constructor() {
		super('/pass-reset-confirm-view/');
	}

	async onIni() {
		if (AuthService.isAuthenticated) {
			window.location.hash = '#/home';
			return;
		}
		console.log('Initializing PassResetConfirmView');
		this.form = this.getElementById('pass-reset-confirm-form');
		this.doneMessage = this.getElementById('pass-reset-confirm-done');
		
		this.uidb64 = this.getUrlParameter('uidb64');
		this.token = this.getUrlParameter('token');

		if (!this.uidb64 || !this.token) {
			console.log('Invalid or missing reset link');
            this.displayErrors({ general: ['Invalid or missing reset link.'] });
            this.form.hidden = true;
            return;
        }
		try {
			const response = await fetch(`/auth/reset/${this.uidb64}/${this.token}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': AuthService.getCsrfToken(),
                },
                body: JSON.stringify({ new_password1: password, new_password2: confirmPassword }),
            });
		} catch (error) {
			this.displayErrors({ general: ['An unexpected error occurred. Please try again later.'] });
		}
		this.form.addEventListener('submit', (event) => this.handleFormSubmit(event));
	}

	displayErrors(errors) {
		const errorContainer = this.form.querySelector('#form-errors');
		errorContainer.innerHTML = '';


		for (const [field, messages] of Object.entries(errors)) {	
			messages.forEach((message) => {
				const errorElement = document.createElement('div');
				errorElement.textContent = message;
				errorContainer.appendChild(errorElement);
			});
		}
	}

	getUrlParameter(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    }
}

customElements.define('pass-reset-confirm-view', PassResetConfirmView);
