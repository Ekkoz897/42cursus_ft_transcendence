import { AuthService } from '../index/AuthService.js';

export class LoginMenu extends BaseComponent {
    constructor() {
        super('/login-menu/');
    }

    async onIni() {
        const menu = this.querySelector('.login-menu');
		const notificationBadge = document.getElementById('menu-notification-badge');

        if (!menu) return;
        
        menu.addEventListener('click', (e) => {
            e.stopPropagation();
            menu.classList.toggle('expanded');
			notificationBadge && (notificationBadge.style.opacity = menu.classList.contains('expanded') ? '0' : '1');
        });

        document.addEventListener('click', () => {
            menu.classList.remove('expanded');
			if (notificationBadge) {notificationBadge.style.opacity = '1';}
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