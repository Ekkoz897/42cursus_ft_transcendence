export class LoginModal extends BaseComponent {
	constructor() {
		super('static/html/login-modal.html');
	}

	async onIni() {
		const modal = this.querySelector(".login-modal");
		const closeButton = this.querySelector(".close-btn");
		const createAccount = this.querySelector("#create-account");

		if (!modal) return;

		// Show modal
		modal.style.display = "flex";

		// Close modal when clicking close button
		if (closeButton) {
			closeButton.addEventListener("click", () => {
				modal.style.display = "none";
			});
		}

		// Switch to Register Modal
		if (createAccount) {
			createAccount.addEventListener("click", (e) => {
				e.preventDefault();
				modal.style.display = "none"; // Hide login modal

				const registerModal = document.createElement('register-modal');
				document.getElementById("profile-view").appendChild(registerModal);
			});
		}
	}
}

customElements.define('login-modal', LoginModal);

