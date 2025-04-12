import { AuthService } from '../index/AuthService.js';

export class PasswordResetConfirmView extends BaseComponent {
    constructor(params) {
        super('/auth/reset-spa/' + params);
        this.params = params;
    }

    async onIni() {
        await this.contentLoaded;

        const form = this.querySelector('form');
        if (form) {
            form.addEventListener('submit', async (event) => {
                event.preventDefault();

                const password1 = form.querySelector('#id_new_password1').value;
                const password2 = form.querySelector('#id_new_password2').value;
                const errorDiv = this.querySelector('#form-errors');

                // Check if passwords match
                if (password1 !== password2) {
                    if (errorDiv) {
                        errorDiv.textContent = 'Passwords do not match.';
                    }
                    return;
                }

                try {
                    await AuthService.confirmPasswordReset(this.params, password1, password2);
                    // Redirect to the "complete" view
                    window.location.hash = '#/password-reset-complete';
                } catch (error) {
                    if (errorDiv) {
                        errorDiv.textContent = error.message || 'An error occurred. Please try again.';
                    }
                }
            });
        }

        // If link is not valid, provide link to request a new reset
        const resetLink = this.querySelector('.auth-link');
        if (resetLink) {
            resetLink.addEventListener('click', (event) => {
                event.preventDefault();
                window.location.hash = '#/password-reset';
            });
        }
    }
}

customElements.define('password-reset-confirm-view', PasswordResetConfirmView);
