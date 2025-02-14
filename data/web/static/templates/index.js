import { NavMenu } from '../js/nav/NavMenu.js';
import { LoginMenu } from '../js/login/LoginMenu.js';
import { HomeView } from '../js/home/HomeView.js';
import { PongView } from '../js/pong/PongView.js';
import { ProfileView } from '../js/profile/ProfileView.js';
import { LoginModal } from '../js/login/LoginModal.js';

//Router.subscribe('', NavMenu);
//customElements.define('nav-menu', NavMenu);
Router.subscribe('home', HomeView);
Router.subscribe('pong', PongView);
Router.subscribe('profile', ProfileView);
Router.subscribe('login', LoginModal);

Router.init();
