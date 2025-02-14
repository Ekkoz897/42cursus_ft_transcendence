import { AuthService } from '../login/AuthService.js';

export class NavMenu extends BaseComponent {
	constructor() {
		super('static/html/nav-menu.html');
	}

	async onIni() {
		const menu = this.querySelector('.nav-menu'); // use base component getElementById
		if (!menu) return;

		// Add menu button class
		menu.classList.add('nav-menu-button');

		// Create navigation buttons container
		const buttonContainer = document.createElement('div');
		buttonContainer.classList.add('nav-buttons');

		// Create navigation buttons
		const homeButton = this.createNavButton('HOME', '#/home');
		const pongButton = this.createNavButton('PONG', '#/pong');
		const loginButton = this.createNavButton('LOGIN', '#/login');
		const logoutButton = this.createNavButton('LOGOUT', '#/home', () => AuthService.logout());

		// Add buttons to container
		buttonContainer.appendChild(homeButton);
		buttonContainer.appendChild(pongButton);

		// Add container to menu
		menu.appendChild(buttonContainer);

		// Toggle menu expansion and assign toggle button based on authentication state
		menu.addEventListener('click', (e) => {
			e.stopPropagation();
			menu.classList.toggle('expanded');

			// Remove existing toggle button if any
			const existingToggleButton = buttonContainer.querySelector('.toggle-button');
			if (existingToggleButton) {
				buttonContainer.removeChild(existingToggleButton);
			}

			// Conditionally assign the toggle button
			const toggleButton = AuthService.isAuthenticated ? logoutButton : loginButton;
			toggleButton.classList.add('toggle-button');
			buttonContainer.appendChild(toggleButton);
		});

		// Close menu when clicking outside
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
			// if (onClick) onClick();
			// const menu = this.querySelector('.nav-menu');
			// if (menu) menu.classList.remove('expanded'); keep menu open after click?
		});
		return button;
	}
}

customElements.define('nav-menu', NavMenu);