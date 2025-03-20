import { AuthService } from "../index/AuthService.js";
export class ProfileView extends BaseComponent {
	constructor(username = null) {
		if (username)
			super(`/profile-view/${encodeURIComponent(username)}/`);
		else
			super('/profile-view/');
		this.requestedUsername = username;
		this.originalFormData = {};
	}

	async onIni() {
		await this.contentLoaded;
		const element = this.getElementById("profile-view");
		if (!element) return;
		this.setupEditProfileButton();
		this.setupChangePictureButton();
		this.setupSecurityButton();
		this.setupChangePasswordButton();
		this.saveOriginalFormData();
	}

	saveOriginalFormData() {
		// Save original data for cancel functionality
		this.originalFormData = {
			username: this.getElementById('username').value,
			email: this.getElementById('email').value,
			about: this.getElementById('about').value
		};
	}

	setupEditProfileButton() {
		const editProfileBtn = this.getElementById('edit-profile-btn');
		const saveProfileBtn = this.getElementById('save-profile-btn');
		const cancelEditBtn = this.getElementById('cancel-edit-btn');

		if (editProfileBtn) {
			editProfileBtn.addEventListener('click', () => this.enableEditMode());
		}

		if (saveProfileBtn) {
			saveProfileBtn.addEventListener('click', () => this.saveProfile());
		}

		if (cancelEditBtn) {
			cancelEditBtn.addEventListener('click', () => this.cancelEdit());
		}
	}

	setupChangePictureButton() {
		const changePictureBtn = this.getElementById('change-picture-btn');
		if (changePictureBtn) {
			changePictureBtn.addEventListener('click', () => this.togglePicOptions());
		}
	}

	setupSecurityButton() {
		const securityBtn = this.getElementById('security-btn');
		if (securityBtn) {
			securityBtn.addEventListener('click', () => this.toggleSecurityOptions());
			// Add event listener for 2FA toggle
			const twoFactorToggle = this.getElementById('twoFactorToggle');
			if (twoFactorToggle) {
				twoFactorToggle.addEventListener('change', (e) => this.toggle2FA(e.target.checked));
			}
		}
	}

	togglePicOptions() {
		const picOptions = this.getElementById('profile-pic-options');
		if (picOptions.classList.contains('d-none')) {
			picOptions.classList.remove('d-none');
		} else {
			picOptions.classList.add('d-none');
		}
	}

	toggleSecurityOptions() {
		const securityOptions = this.getElementById('security-options');
		const securityBtn = this.getElementById('security-btn');
		const caretIcon = securityBtn.querySelector('i');

		if (securityOptions.classList.contains('d-none')) {
			// Show the options
			securityOptions.classList.remove('d-none');

			// Change icon to up caret with animation
			caretIcon.classList.remove('fa-caret-down');
			caretIcon.classList.add('fa-caret-up');

			// Add visual feedback
			securityBtn.classList.add('active');

			// Add subtle animation
			securityOptions.style.opacity = '0';
			securityOptions.style.transform = 'translateY(-10px)';
			securityOptions.style.transition = 'opacity 0.3s, transform 0.3s';

			// Trigger repaint
			securityOptions.offsetHeight;

			// Animate in
			securityOptions.style.opacity = '1';
			securityOptions.style.transform = 'translateY(0)';
		} else {
			// Hide with animation
			securityOptions.style.opacity = '0';
			securityOptions.style.transform = 'translateY(-10px)';

			// Remove active state
			securityBtn.classList.remove('active');

			// Change icon back to down caret
			caretIcon.classList.remove('fa-caret-up');
			caretIcon.classList.add('fa-caret-down');

			// Hide after animation completes
			setTimeout(() => {
				securityOptions.classList.add('d-none');
			}, 300);
		}
	}

	toggle2FA(enabled) {
		// This function would update the two_factor_enable setting
		console.log(`Two-factor authentication ${enabled ? 'enabled' : 'disabled'}`);

		// Update UI immediately for better user experience
		const toggle = this.getElementById('twoFactorToggle');
		const badge = toggle.nextElementSibling.querySelector('.badge');

		// Update badge appearance
		if (enabled) {
			badge.textContent = 'ON';
			badge.classList.remove('bg-secondary');
			badge.classList.add('bg-success');
		} else {
			badge.textContent = 'OFF';
			badge.classList.remove('bg-success');
			badge.classList.add('bg-secondary');
			}

		// TEMPORARY TO SEE IF BOOLEAN WORKS, WILL REMOVE AND REPLACE WITH FETCH REQUEST
		this.showMessage('success', `Two-factor authentication would be ${enabled ? 'enabled' : 'disabled'}`);
	}

	setupChangePasswordButton() {
		const changePasswordBtn = this.getElementById('change-password-btn');
		const confirmPasswordBtn = this.getElementById('confirm-password-btn');
		const cancelPasswordBtn = this.getElementById('cancel-password-btn');

		if (changePasswordBtn) {
			changePasswordBtn.addEventListener('click', () => this.showChangePasswordFields());
		}

		if (confirmPasswordBtn) {
			confirmPasswordBtn.addEventListener('click', () => this.changePassword());
		}

		if (cancelPasswordBtn) {
			cancelPasswordBtn.addEventListener('click', () => this.hideChangePasswordFields());
		}
	}

	showChangePasswordFields() {
		const changePasswordBtn = this.getElementById('change-password-btn');
		const passwordFields = this.getElementById('password-fields');
		const securityCards = this.querySelectorAll('#security-options .card .card-body');

		// Make both cards equal in height for better alignment
		securityCards.forEach(card => {
			card.style.minHeight = '240px';
		});

		changePasswordBtn.classList.add('d-none');
		passwordFields.classList.remove('d-none');

		// Focus on the first input field
		this.getElementById('current-password').focus();
	}

	hideChangePasswordFields() {
		const changePasswordBtn = this.getElementById('change-password-btn');
		const passwordFields = this.getElementById('password-fields');
		const securityCards = this.querySelectorAll('#security-options .card .card-body');

		// Reset the fixed height
		securityCards.forEach(card => {
			card.style.minHeight = '';
		});

		// Clear input fields
		this.getElementById('current-password').value = '';
		this.getElementById('new-password').value = '';

		changePasswordBtn.classList.remove('d-none');
		passwordFields.classList.add('d-none');
	}

	async changePassword() {
		const currentPassword = this.getElementById('current-password').value;
		const newPassword = this.getElementById('new-password').value;

		// Basic validation
		if (!currentPassword || !newPassword) {
			this.showMessage('error', 'Both password fields are required');
			return;
		}

		// Basic new password validation
		if (newPassword.length < 8) {
			this.showMessage('error', 'New password must be at least 8 characters long');
			return;
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
		// Hide edit button, show save and cancel buttons
		this.getElementById('edit-profile-btn').classList.add('d-none');
		this.getElementById('save-profile-btn').classList.remove('d-none');
		this.getElementById('cancel-edit-btn').classList.remove('d-none');

		// Enable all form fields
		const profileFields = this.querySelectorAll('.profile-field');
		profileFields.forEach(field => {
			field.disabled = false;
		});

		// Show profile picture section
		this.getElementById('profile-pic-section').classList.remove('d-none');

		// Hide security settings button
		const securityBtn = this.getElementById('security-btn');
		if (securityBtn) {
			securityBtn.classList.add('d-none');
		}

		// Hide security options if they are currently visible
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

			// Get selected profile picture if any
			const selectedPic = this.querySelector('input[name="profile-pic"]:checked');
			if (selectedPic) {
				// Just send the filename, the backend will construct the full path
				formData.profile_pic = selectedPic.value;
			}

			// Get CSRF token from cookie
			const csrftoken = this.getCookie('csrftoken');

			// Send PUT request to update profile
			const response = await fetch('/profile/update/', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': csrftoken
				},
				body: JSON.stringify(formData)
			});

			const data = await response.json();

			if (response.ok) {
				// Success: update UI and disable edit mode
				this.showMessage('success', 'Profile updated successfully!');

				// Update the displayed username in the profile area
				const usernameDisplay = this.querySelector('.profile-info h2');
				if (usernameDisplay) {
					usernameDisplay.textContent = formData.username;
				}

				// Update page title with new username if changed
				const aboutTabTitle = this.querySelector('#about-tab');
				if (aboutTabTitle) {
					const aboutHeading = this.querySelector('#about h4');
					if (aboutHeading) {
						aboutHeading.textContent = `About ${formData.username}`;
					}
				}

				this.saveOriginalFormData(); // Update the stored original data
				this.disableEditMode();
			} else {
				// Error: show error message but keep edit mode
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

		// Disable edit mode
		this.disableEditMode();
	}

	disableEditMode() {
		// Show edit button, hide save and cancel buttons
		this.getElementById('edit-profile-btn').classList.remove('d-none');
		this.getElementById('save-profile-btn').classList.add('d-none');
		this.getElementById('cancel-edit-btn').classList.add('d-none');

		// Disable all form fields
		const profileFields = this.querySelectorAll('.profile-field');
		profileFields.forEach(field => {
			field.disabled = true;
		});

		// Hide profile picture section and options
		this.getElementById('profile-pic-section').classList.add('d-none');
		this.getElementById('profile-pic-options').classList.add('d-none');

		// Show security settings button
		const securityBtn = this.getElementById('security-btn');
		if (securityBtn) {
			securityBtn.classList.remove('d-none');
		}
	}

	showMessage(type, message) {
		// Check for existing messages and limit to max 2
		const existingAlerts = this.querySelectorAll('.alert');
		if (existingAlerts.length >= 2) {
			// Remove the oldest message (the last one in DOM order)
			existingAlerts[existingAlerts.length - 1].remove();
		}

		// Create alert element
		const alertDiv = document.createElement('div');
		alertDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
		alertDiv.role = 'alert';
		alertDiv.innerHTML = `
			${message}
			<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
		`;

		// Insert at the top of the form
		const form = this.getElementById('profile-form');
		form.insertBefore(alertDiv, form.firstChild);

		// Auto-dismiss after 5 seconds
		setTimeout(() => {
			alertDiv.classList.remove('show');
			setTimeout(() => alertDiv.remove(), 300); // Remove after fade animation
		}, 5000);
	}

	getCookie(name) {
		let cookieValue = null;
		if (document.cookie && document.cookie !== '') {
			const cookies = document.cookie.split(';');
			for (let i = 0; i < cookies.length; i++) {
				const cookie = cookies[i].trim();
				// Does this cookie string begin with the name we want?
				if (cookie.substring(0, name.length + 1) === (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}
}

customElements.define('profile-view', ProfileView);
