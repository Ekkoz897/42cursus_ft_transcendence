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
        const homeButton = document.createElement('div');
        const pongButton = document.createElement('div');
		const loginButton = document.createElement('div');
		const logoutButton = document.createElement('div');

        // Set up buttons
        [homeButton, pongButton, loginButton, logoutButton].forEach(button => {
            button.classList.add('nav-button');
        });

        homeButton.textContent = "HOME";
        pongButton.textContent = "PONG";
		loginButton.textContent = "LOGIN";
		logoutButton.textContent = "LOGOUT";

        // Add navigation handlers
        homeButton.addEventListener('click', () => {
            window.location.hash = '#/home';
            menu.classList.remove('expanded');
        });

        pongButton.addEventListener('click', () => {
            window.location.hash = '#/pong';
            menu.classList.remove('expanded');
        });

		loginButton.onclick = () => window.location.hash = '#/login';
		logoutButton.onclick = () => AuthService.logout();

        // Add buttons to container
        buttonContainer.appendChild(homeButton);
        buttonContainer.appendChild(pongButton);
		buttonContainer.appendChild(loginButton);
		buttonContainer.appendChild(logoutButton);

        // Add container to menu
        menu.appendChild(buttonContainer);

        // Toggle menu expansion
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

customElements.define('nav-menu', NavMenu);