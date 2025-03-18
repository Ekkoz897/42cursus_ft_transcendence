import { AuthService } from '../index/AuthService.js';

export class LoginMenu extends BaseComponent {
	constructor() {
		super('static/html/login-menu.html');
		this.buttons = {};
	}

	async onIni() {
		const menu = this.querySelector('.login-menu');
		if (!menu) return;

		menu.classList.add('menu-button');

		const buttonContainer = document.createElement('div');
		buttonContainer.classList.add('menu-buttons');

		this.buttons.profileButton = this.createNavButton('PROFILE', '#/profile');
		this.buttons.loginButton = this.createNavButton('LOG IN', '#/login');
		this.buttons.logoutButton = this.createNavButton('LOG OUT', '#/home', async () => {
			await AuthService.logout();
			await this.updateUI(menu, userName, loginIcon, userIcon);
		});
		
		this.buttons.loginButton.style.display = 'none';
		this.buttons.logoutButton.style.display = 'none';

		buttonContainer.appendChild(this.buttons.profileButton);
		buttonContainer.appendChild(this.buttons.loginButton);
		buttonContainer.appendChild(this.buttons.logoutButton);
		
		const userName = document.createElement('div');
		userName.classList.add('menu-user');
		menu.appendChild(userName);

		menu.appendChild(buttonContainer);

		const loginIcon = menu.querySelector('#login-icon');
        const userIcon = menu.querySelector('#user-icon');

		await this.updateUI(menu, userName, loginIcon, userIcon);

		menu.addEventListener('click', async (e) => {
			e.stopPropagation();
			menu.classList.toggle('expanded');
			
			await this.updateUI(menu, userName, loginIcon, userIcon);
		});

		document.addEventListener('click', () => {
			menu.classList.remove('expanded');
		});
	}

	async updateUI(menu, userName, loginIcon, userIcon) {
        await AuthService.check_auth();
        userName.textContent = AuthService.currentUser ? AuthService.currentUser : '';
        if (AuthService.isAuthenticated) {
            this.buttons.loginButton.style.display = 'none';
            this.buttons.logoutButton.style.display = 'block';
            loginIcon.style.display = 'none';
            userIcon.style.display = 'block';
            userIcon.src = AuthService.currentpfp;
        } else {
            this.buttons.loginButton.style.display = 'block';
            this.buttons.logoutButton.style.display = 'none';
            loginIcon.style.display = 'block';
            userIcon.style.display = 'none';
        }
    }

	createNavButton(text, hash, onClick) {
		const button = document.createElement('div');
		button.classList.add('nav-button');
		button.textContent = text;
		button.addEventListener('click', () => {
			window.location.hash = hash;
			if (onClick) onClick();
		});
		return button;
	}
}


customElements.define('login-menu', LoginMenu);