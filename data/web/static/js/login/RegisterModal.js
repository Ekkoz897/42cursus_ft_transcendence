export class RegisterModal extends BaseComponent {
	constructor() {
		super('static/html/register-modal.html');
	}

	async onIni() {
		const modal = this.querySelector(".register-modal");
		const closeButton = this.querySelector(".close-btn");
		const switchToLogin = this.querySelector("#switch-to-login");

		if (!modal) return;

		// Show modal
		modal.style.display = "flex";

		// Close modal when clicking close button
		if (closeButton) {
			closeButton.addEventListener("click", () => {
				modal.style.display = "none";
			});
		}

		// Switch back to login modal
		if (switchToLogin) {
			switchToLogin.addEventListener("click", (e) => {
				e.preventDefault();
				modal.style.display = "none"; // Hide register modal

				const loginModal = document.createElement('login-modal');
				document.getElementById("profile-view").appendChild(loginModal);
			});
		}
	}
}

customElements.define('register-modal', RegisterModal);
