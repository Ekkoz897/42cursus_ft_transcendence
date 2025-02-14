export class LoginModal extends BaseComponent {
	constructor() {
		super('static/html/login-modal.html');
	}

	async onIni() {
		const modal = this.querySelector(".login-modal");
		const closeButton = this.querySelector(".close-btn");

		if (!modal) return;

		// Show the modal when navigating to /login
		modal.style.display = "flex";

		// Close modal when clicking the close button
		if (closeButton) {
			closeButton.addEventListener("click", () => {
				modal.style.display = "none";
			});
		}

		// Close modal when clicking outside of it
		window.addEventListener("click", (e) => {
			if (e.target === modal) {
				modal.style.display = "none";
			}
		});
	}
}

customElements.define('login-modal', LoginModal);
