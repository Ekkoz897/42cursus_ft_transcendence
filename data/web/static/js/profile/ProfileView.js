import { AuthService } from "../index/AuthService.js";
export class ProfileView extends BaseComponent {
	constructor(username = null) {
		super(username ? `/profile-view/${encodeURIComponent(username)}/` : '/profile-view/');
		this.requestedUsername = username;
		this.originalFormData = {};
	}

	async onIni() {
		await this.contentLoaded;
		const element = this.getElementById("profile-view");
		if (!element) return;

		this.setupButtons();
		this.saveOriginalFormData();
	}

	saveOriginalFormData() {
		this.originalFormData = {
			username: this.getElementById('username').value,
			email: this.getElementById('email').value,
			about: this.getElementById('about').value
		};
	}

	setupButtons() {
		// Set up button event listeners with a more concise approach
		this.setupButton('edit-profile-btn', () => this.enableEditMode());
		this.setupButton('save-profile-btn', () => this.saveProfile());
		this.setupButton('cancel-edit-btn', () => this.cancelEdit());
		this.setupButton('change-picture-btn', () => this.toggleElement('profile-pic-options'));
		this.setupButton('change-password-btn', () => this.showChangePasswordFields());
		this.setupButton('confirm-password-btn', () => this.changePassword());
		this.setupButton('cancel-password-btn', () => this.hideChangePasswordFields());

		// Security button requires special handling
		this.setupSecurityButton();
	}

	setupButton(id, callback) {
		const button = this.getElementById(id);
		if (button) {
			button.addEventListener('click', callback);
		}
	}

	setupSecurityButton() {
		const securityBtn = this.getElementById('security-btn');
		if (securityBtn) {
			securityBtn.addEventListener('click', () => this.toggleSecurityOptions());

			// Setup 2FA toggle
			const twoFactorToggle = this.getElementById('twoFactorToggle');
			if (twoFactorToggle) {
				twoFactorToggle.addEventListener('change', (e) => this.toggle2FA(e.target.checked));
			}
		}
	}

	toggleElement(elementId) {
		const element = this.getElementById(elementId);
		if (element) {
			element.classList.toggle('d-none');
		}
	}

	toggleSecurityOptions() {
		const securityOptions = this.getElementById('security-options');
		const securityBtn = this.getElementById('security-btn');
		const caretIcon = securityBtn.querySelector('i');

		if (securityOptions.classList.contains('d-none')) {
			// Show options
			securityOptions.classList.remove('d-none');
			caretIcon.classList.replace('fa-caret-down', 'fa-caret-up');
			securityBtn.classList.add('active');

			// Animation
			securityOptions.style.opacity = '0';
			securityOptions.style.transform = 'translateY(-10px)';
			securityOptions.style.transition = 'opacity 0.3s, transform 0.3s';
			securityOptions.offsetHeight; // Trigger repaint
			securityOptions.style.opacity = '1';
			securityOptions.style.transform = 'translateY(0)';
		} else {
			// Hide with animation
			securityOptions.style.opacity = '0';
			securityOptions.style.transform = 'translateY(-10px)';
			securityBtn.classList.remove('active');
			caretIcon.classList.replace('fa-caret-up', 'fa-caret-down');

			setTimeout(() => securityOptions.classList.add('d-none'), 300);
		}
	}

	async toggle2FA(enabled) {
		// Get UI elements
		const toggle = this.getElementById('twoFactorToggle');
		const badge = toggle.nextElementSibling.querySelector('.badge');
		const originalState = !enabled;

		// Show loading state
		badge.textContent = '...';
		badge.classList.add('bg-secondary');
		badge.classList.remove('bg-success');

		try {
			const response = await fetch('/profile/update-2fa/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': this.getCookie('csrftoken')
				},
				body: JSON.stringify({ two_factor_enable: enabled })
			});

			const data = await response.json();

			if (response.ok && data.success) {
				// Update UI on success
				badge.textContent = enabled ? 'ON' : 'OFF';
				badge.classList.toggle('bg-secondary', !enabled);
				badge.classList.toggle('bg-success', enabled);

				this.showMessage('success', data.message || `Two-factor authentication ${enabled ? 'enabled' : 'disabled'}`);
			} else {
				// Revert toggle on error
				toggle.checked = originalState;
				this.showMessage('error', data.error || 'Failed to update two-factor authentication setting');
			}
		} catch (error) {
			// Revert toggle on error
			toggle.checked = originalState;
			console.error('Error updating 2FA setting:', error);
			this.showMessage('error', 'An error occurred while updating two-factor authentication');
		}
	}

	showChangePasswordFields() {
		const changePasswordBtn = this.getElementById('change-password-btn');
		const passwordFields = this.getElementById('password-fields');
		const securityCards = this.querySelectorAll('#security-options .card .card-body');

		// Make cards equal height
		securityCards.forEach(card => card.style.minHeight = '240px');

		changePasswordBtn.classList.add('d-none');
		passwordFields.classList.remove('d-none');

		// Focus on first field
		this.getElementById('current-password').focus();
	}

	hideChangePasswordFields() {
		const securityCards = this.querySelectorAll('#security-options .card .card-body');

		// Reset height
		securityCards.forEach(card => card.style.minHeight = '');

		// Clear inputs
		this.getElementById('current-password').value = '';
		this.getElementById('new-password').value = '';

		this.getElementById('change-password-btn').classList.remove('d-none');
		this.getElementById('password-fields').classList.add('d-none');
	}

	async changePassword() {
		const currentPassword = this.getElementById('current-password').value;
		const newPassword = this.getElementById('new-password').value;

		// Validation
		if (!currentPassword || !newPassword) {
			return this.showMessage('error', 'Both password fields are required');
		}

		if (newPassword.length < 8) {
			return this.showMessage('error', 'New password must be at least 8 characters long');
		}

		try {
			// Show loading state
			const confirmButton = this.getElementById('confirm-password-btn');
			const originalText = confirmButton.textContent;
			confirmButton.disabled = true;
			confirmButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Verifying...';

			const response = await fetch('/profile/change-password/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': this.getCookie('csrftoken')
				},
				body: JSON.stringify({
					current_password: currentPassword,
					new_password: newPassword
				})
			});

			const data = await response.json();

			// Reset button state
			confirmButton.disabled = false;
			confirmButton.textContent = originalText;

			if (response.ok && data.success) {
				this.showMessage('success', 'Password changed successfully');
				this.hideChangePasswordFields();
			} else {
				this.showMessage('error', data.error || 'Failed to change password');
			}
		} catch (error) {
			console.error('Error changing password:', error);
			this.showMessage('error', 'An error occurred while changing your password');
		}
	}

	enableEditMode() {
		// Toggle button visibility
		this.getElementById('edit-profile-btn').classList.add('d-none');
		this.getElementById('save-profile-btn').classList.remove('d-none');
		this.getElementById('cancel-edit-btn').classList.remove('d-none');

		// Enable form fields
		this.querySelectorAll('.profile-field').forEach(field => field.disabled = false);

		// Show profile picture section
		this.getElementById('profile-pic-section').classList.remove('d-none');

		// Hide security elements
		const securityBtn = this.getElementById('security-btn');
		if (securityBtn) securityBtn.classList.add('d-none');

		const securityOptions = this.getElementById('security-options');
		if (securityOptions && !securityOptions.classList.contains('d-none')) {
			securityOptions.classList.add('d-none');
		}
	}

	async saveProfile() {
		try {
			// Collect form data
			const formData = {
				username: this.getElementById('username').value,
				email: this.getElementById('email').value,
				about_me: this.getElementById('about').value
			};

			// Get selected profile picture
			const selectedPic = this.querySelector('input[name="profile-pic"]:checked');
			if (selectedPic) {
				formData.profile_pic = selectedPic.value;
			}

			const response = await fetch('/profile/update/', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': this.getCookie('csrftoken')
				},
				body: JSON.stringify(formData)
			});

			const data = await response.json();

			if (response.ok) {
				this.showMessage('success', 'Profile updated successfully!');

				// Update displayed username
				const usernameDisplay = this.querySelector('.profile-info h2');
				if (usernameDisplay) {
					usernameDisplay.textContent = formData.username;
				}

				// Update page title
				const aboutTabTitle = this.querySelector('#about-tab');
				if (aboutTabTitle) {
					const aboutHeading = this.querySelector('#about h4');
					if (aboutHeading) {
						aboutHeading.textContent = `About ${formData.username}`;
					}
				}

				this.saveOriginalFormData();
				this.disableEditMode();
			} else {
				this.showMessage('error', data.error || 'Failed to update profile');
			}
		} catch (error) {
			console.error('Error updating profile:', error);
			this.showMessage('error', 'An error occurred while updating your profile');
		}
	}

	cancelEdit() {
		// Restore original values
		this.getElementById('username').value = this.originalFormData.username;
		this.getElementById('email').value = this.originalFormData.email;
		this.getElementById('about').value = this.originalFormData.about;

		// Hide profile pic options
		this.getElementById('profile-pic-options').classList.add('d-none');

		this.disableEditMode();
	}

	disableEditMode() {
		// Toggle button visibility
		this.getElementById('edit-profile-btn').classList.remove('d-none');
		this.getElementById('save-profile-btn').classList.add('d-none');
		this.getElementById('cancel-edit-btn').classList.add('d-none');

		// Disable form fields
		this.querySelectorAll('.profile-field').forEach(field => field.disabled = true);

		// Hide profile picture elements
		this.getElementById('profile-pic-section').classList.add('d-none');
		this.getElementById('profile-pic-options').classList.add('d-none');

		// Show security button
		const securityBtn = this.getElementById('security-btn');
		if (securityBtn) securityBtn.classList.remove('d-none');
	}

	showMessage(type, message) {
		// Limit to max 2 messages
		const existingAlerts = this.querySelectorAll('.alert');
		if (existingAlerts.length >= 2) {
			existingAlerts[existingAlerts.length - 1].remove();
		}

		// Create alert
		const alertDiv = document.createElement('div');
		alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
		alertDiv.role = 'alert';
		alertDiv.innerHTML = `
			${message}
			<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
		`;

		// Add to DOM
		const form = this.getElementById('profile-form');
		form.insertBefore(alertDiv, form.firstChild);

		// Auto-dismiss
		setTimeout(() => {
			alertDiv.classList.remove('show');
			setTimeout(() => alertDiv.remove(), 300);
		}, 5000);
	}

	getCookie(name) {
		if (document.cookie && document.cookie !== '') {
			const cookies = document.cookie.split(';');
			for (let cookie of cookies) {
				cookie = cookie.trim();
				if (cookie.substring(0, name.length + 1) === (name + '=')) {
					return decodeURIComponent(cookie.substring(name.length + 1));
				}
			}
		}
		return null;
	}
}

customElements.define('profile-view', ProfileView);
