export class LoginMenu extends BaseComponent {
    constructor() {
        // Use the login-menu.html template (make sure this file exists in static/html)
        super('static/html/login-menu.html');
    }

    async onIni() {
        const menu = this.querySelector('.login-menu');
        if (!menu) return;

        // Add the same base style as NavMenu
        menu.classList.add('nav-menu-button');

        // Create a container for the buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.classList.add('nav-buttons');

        // Create the new buttons for the login menu
        const profileButton = document.createElement('div');
        const loginButton = document.createElement('div');
        const logoutButton = document.createElement('div');

        // Apply the shared styling
        [profileButton, loginButton, logoutButton].forEach(button => {
            button.classList.add('nav-button');
        });

        // Set button labels
        profileButton.textContent = "PROFILE";
        loginButton.textContent = "LOG IN";
        logoutButton.textContent = "LOG OUT";

        // Add click handlers to update the URL hash and collapse the menu
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
