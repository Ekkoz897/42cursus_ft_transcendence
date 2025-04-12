import { AuthService } from '../index/AuthService.js';

export class PasswordResetCompleteView extends BaseComponent {
    constructor() {
        super('/auth/reset-complete-spa/');
    }

    async onIni() {
        await this.contentLoaded;

        // Add link back to login
        const loginLink = this.querySelector('.auth-link');
        if (loginLink) {
            loginLink.addEventListener('click', (event) => {
                event.preventDefault();
                window.location.hash = '#/login';
            });
        }
    }
}

customElements.define('password-reset-complete-view', PasswordResetCompleteView);
