export class AuthService {
    static isAuthenticated = false;
    static currentUser = null;

	static async init() {		
		try {
			await this.check_auth();
		} catch (error) {
			console.error('Auth check failed:', error);
		}
	}


	static async login(username, password) {
		const response = await fetch('/login/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-CSRFToken': this.getCsrfToken(), // document.cookie.match(/csrftoken=([\w-]+)/)[1]
			},
			body: JSON.stringify({ username, password })
		});

		const data = await response.json();
		if (response.ok) {
			this.isAuthenticated = true;
			this.currentUser = data.user;
		} else {
			const error = new Error(data.error);
			error.status = response.status;
			throw error;
		}
	}


    static async logout() {
        const response = await fetch('/logout/', {
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
		window.location.hash = '#/home';
		// window.location.reload();
    }


    static async register(userData) {
        const response = await fetch('/register/', {
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

	static async check_auth() {
		const response = await fetch('/check-auth/', {
			method: 'GET',
			credentials: 'include',
			headers: {
				'content-type': 'application/json',
				'X-CSRFToken': this.getCsrfToken()
			}
		});
		const data = await response.json();
		this.isAuthenticated = data.isAuthenticated;
		this.currentUser = data.user;
	}

	static getCsrfToken() {
		return document.cookie
			.split('; ')
			.find(row => row.startsWith('csrftoken='))
			?.split('=')[1];
	}

}