import { AuthService } from '../index/AuthService.js';

export class LoginMenu extends BaseComponent {
	constructor() {
		super('static/html/login-menu.html'); 
	}

	async onIni() {
		const menu = this.querySelector('.login-menu');
		if (!menu) return;

		menu.classList.add('menu-button');

		const buttonContainer = document.createElement('div');
		buttonContainer.classList.add('menu-buttons');

		const profileButton = this.createNavButton('PROFILE', '#/profile');
		const loginButton = this.createNavButton('LOG IN', '#/login');
		const logoutButton = this.createNavButton('LOG OUT', '#/home', () => AuthService.logout());

		buttonContainer.appendChild(profileButton);

		menu.appendChild(buttonContainer);

		menu.addEventListener('click', (e) => {
			e.stopPropagation();
			menu.classList.toggle('expanded');

			const existingToggleButton = buttonContainer.querySelector('.toggle-button');
			if (existingToggleButton) {
				buttonContainer.removeChild(existingToggleButton);
			}

			AuthService.check_auth();
			const toggleButton = AuthService.isAuthenticated ? logoutButton : loginButton;
			toggleButton.classList.add('toggle-button');
			buttonContainer.appendChild(toggleButton);
		});

		document.addEventListener('click', () => {
			menu.classList.remove('expanded');
		});
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