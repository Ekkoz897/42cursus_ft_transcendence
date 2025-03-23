import { AuthService } from '../index/AuthService.js';

export class LoginMenu extends BaseComponent {
    constructor() {
        super('/login-menu/');
    }

    async onIni() {
        const menu = this.querySelector('.login-menu');
        if (!menu) return;
        
        menu.addEventListener('click', (e) => {
            e.stopPropagation();
            menu.classList.toggle('expanded');
        });

        document.addEventListener('click', () => {
            menu.classList.remove('expanded');
        });
        
        const logoutButton = this.querySelector('#logout-button');
        if (logoutButton) {
            logoutButton.addEventListener('click', async () => {
                await AuthService.logout();
            });
        }
    }
}

customElements.define('login-menu', LoginMenu);