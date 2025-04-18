export class LanguageView extends BaseComponent {
	constructor() {
		super('/language-menu/');
	}

	async onIni() {
		const menu = this.querySelector('.language-menu');
		if (!menu) return;
		menu.addEventListener('click', (event) => {
			const target = event.target;
			if (target.classList.contains('language-menu__link')) {
				event.preventDefault();
				const selectedLang = target.getAttribute('data-lang');
				this.changeLanguage(selectedLang);
			}
		});
	}

	async changeLanguage(lang) {
		try {
			const response = await fetch(`/set-language/?lang=${lang}`, {
				method: 'GET',
				'X-Template-Only': 'true',
			});

			if (response.ok) {
				const hash = window.location.hash.substring(2);
				Router.go(hash);
			} else {
				console.error('Failed to change language');
			}
		} catch (error) {
			console.error('Error changing language:', error);
		}
	}
}

customElements.define('language-menu', LanguageView);