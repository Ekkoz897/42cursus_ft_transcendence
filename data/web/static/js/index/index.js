import { NavMenu } from '../nav/NavMenu.js';
import { HomeView } from '../home/HomeView.js';
import { PongView } from '../pong/PongView.js';
import { RegisterView } from '../login/RegisterView.js';
import { LoginView } from '../login/LoginView.js';
import { AuthService } from '../login/AuthService.js';


Router.subscribe('home', HomeView);
Router.subscribe('pong', PongView);
Router.subscribe('register', RegisterView);
Router.subscribe('login', LoginView);


Router.init();
