import { NavMenu } from '../js/nav/NavMenu.js';
import { HomeView } from '../js/home/HomeView.js';
import { PongView } from '../js/pong/PongView.js';
import { RegisterView } from '../js/login/RegisterView.js';
import { LoginView } from '../js/login/LoginView.js';
import { AuthService } from '../js/login/AuthService.js';


Router.subscribe('home', HomeView);
Router.subscribe('pong', PongView);
Router.subscribe('register', RegisterView);
Router.subscribe('login', LoginView);


Router.init();
