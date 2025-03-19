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

	togglePicOptions() {
		const picOptions = this.getElementById('profile-pic-options');
		if (picOptions.classList.contains('d-none')) {
			picOptions.classList.remove('d-none');
		} else {
			picOptions.classList.add('d-none');
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
	}

	showMessage(type, message) {
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
