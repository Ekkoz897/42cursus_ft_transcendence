import { AuthService } from '../index/AuthService.js';

export class PasswordResetView extends BaseComponent {
    constructor() {
        super('/auth/password-reset-spa/');
    }

    async onIni() {
        await this.contentLoaded;

        const form = this.querySelector('form');
        if (form) {
            form.addEventListener('submit', async (event) => {
                event.preventDefault();

                const email = form.querySelector('#id_email').value;
                const errorDiv = this.querySelector('#form-errors');

                try {
                    await AuthService.requestPasswordReset(email);
                    // Redirect to the "done" view
                    window.location.hash = '#/password-reset-done';
                } catch (error) {
                    if (errorDiv) {
                        errorDiv.textContent = error.message || 'An error occurred. Please try again.';
                    }
                }
            });
        }
    }
}

customElements.define('password-reset-view', PasswordResetView);
