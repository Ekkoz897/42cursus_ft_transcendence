export class LoginMenu extends BaseComponent {
	constructor() {
		super('static/html/login-menu.html'); // Ensure this file exists
	}

	async onIni() {
		const menu = this.querySelector('.login-menu');
		if (!menu) return;

		// Add icon styling
		menu.classList.add('login-menu');

		// Create a container for buttons
		const buttonContainer = document.createElement('div');
		buttonContainer.classList.add('login-buttons');

		// Create buttons
		const profileButton = document.createElement('div');
		const loginButton = document.createElement('div');
		const logoutButton = document.createElement('div');

		// Apply styles to buttons
		[profileButton, loginButton, logoutButton].forEach(button => {
			button.classList.add('login-button');
		});

		// Set button labels
		profileButton.textContent = "PROFILE";
		loginButton.textContent = "LOG IN";
		logoutButton.textContent = "LOG OUT";

		// Add click handlers
		profileButton.addEventListener('click', () => {
			window.location.hash = '#/profile';
			menu.classList.remove('expanded');
		});

		loginButton.addEventListener('click', () => {
			window.location.hash = '#/login';
			menu.classList.remove('expanded');
		});

		logoutButton.addEventListener('click', () => {
			window.location.hash = '#/logout';
			menu.classList.remove('expanded');
		});

		// Append buttons to the container
		buttonContainer.appendChild(profileButton);
		buttonContainer.appendChild(loginButton);
		buttonContainer.appendChild(logoutButton);

		// Append the container to the menu
		menu.appendChild(buttonContainer);

		// Toggle menu expansion on click
		menu.addEventListener('click', (e) => {
			e.stopPropagation();
			menu.classList.toggle('expanded');
		});

		// Close menu when clicking outside
		document.addEventListener('click', () => {
			menu.classList.remove('expanded');
		});
	}
}

customElements.define('login-menu', LoginMenu);
