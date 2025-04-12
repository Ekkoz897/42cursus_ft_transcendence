export class AuthService {
    static isAuthenticated = false;
    static currentUser = null;
	static currentpfp = null;
	static host = null;

	static async init() {
		try {
			await this.check_auth();
			await this.fetchHost();
		} catch (error) {
			throw error;
		}

	}


	static async login(username, password) {
		const response = await fetch('/auth/login/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken(),
			},
			body: JSON.stringify({ username, password })
		});

		const data = await response.json();
		if (response.ok) {
			this.isAuthenticated = true;
			this.currentUser = data.user;
			//window.location.hash = '#/home';
			window.location.reload();
		} else {
			const error = new Error(data.error);
			error.status = response.status;
			throw error;
		}
	}


	static async login42() {
		const host = this.host;
		const redirectUri = encodeURIComponent(`https://${host}/auth/oauth/callback/`);
		window.location.href = `https://api.intra.42.fr/oauth/authorize?client_id=u-s4t2ud-f8562a1795538b5f2a9185781d374e1152c6466501442d50530025b059fe92ad&redirect_uri=${redirectUri}&response_type=code`;
	}


    static async logout() {
        const response = await fetch('/auth/logout/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken(),
			},
		});

        if (response.ok) {
            this.isAuthenticated = false;
            this.currentUser = null;
        }
		// window.location.hash = '#/home';
		window.location.reload();
    }


    static async register(userData) {
        const response = await fetch('/auth/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken(),
            },
            body: JSON.stringify(userData)
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(Object.values(data).join('\n'));
        }
    }

	static async change_password(oldpsw, newpsw) {
		const response = await fetch('/auth/change-password/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken()
			},
			body: JSON.stringify({
				current_password: oldpsw,
				new_password: newpsw
			})
		});
		return response;
	}

	static async toggle2fa(enabled) {
		const response = await fetch('/auth/2fa/update/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken()
			},
			body: JSON.stringify({ two_factor_enable: enabled })
		});
		return response;
	}

	static async check_auth() {
		const response = await fetch('/auth/status/', {
			method: 'GET',
		});
		const data = await response.json();
		this.isAuthenticated = data.isAuthenticated;
		if (this.isAuthenticated && data.user) {
			this.currentUser = data.user.username;
			this.currentpfp = data.user.profile_pic;
		} else {
			this.currentUser = null;
			this.currentpfp = null;
		}
	}


	static async fetchHost() {
		const response = await fetch('/auth/get-host/', {
			method: 'GET',
		});
		const data = await response.json();
		this.host = data.host;
	}


	static getCsrfToken() {
		return document.cookie
			.split('; ')
			.find(row => row.startsWith('csrftoken='))
			?.split('=')[1];
	}

	// Password reset request (step 1)
	static async requestPasswordReset(email) {
		const formData = new FormData();
		formData.append('email', email);
		formData.append('csrfmiddlewaretoken', this.getCsrfToken());

		const response = await fetch('/auth/password-reset/api/', {
			method: 'POST',
			headers: {
				'X-CSRFToken': this.getCsrfToken(),
			},
			body: formData
		});

		if (!response.ok) {
			const data = await response.json();
			throw new Error(data.error || 'Password reset request failed');
		}

		return true;
	}

	// Password reset confirmation (step 3)
	static async confirmPasswordReset(uidb64_token, password1, password2) {
		const formData = new FormData();
		formData.append('new_password1', password1);
		formData.append('new_password2', password2);
		formData.append('csrfmiddlewaretoken', this.getCsrfToken());

		const response = await fetch(`/auth/reset/${uidb64_token}/api/`, {
			method: 'POST',
			headers: {
				'X-CSRFToken': this.getCsrfToken(),
			},
			body: formData
		});

		if (!response.ok) {
			const data = await response.json();
			throw new Error(data.error || 'Password reset confirmation failed');
		}

		return true;
	}
}
