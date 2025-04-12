import { NavMenu } from '../nav/NavMenu.js';
import { LoginMenu } from '../login/LoginMenu.js';

import { HomeView } from '../home/HomeView.js';
import { PongView } from '../pong/PongView.js';
import { TournamentView } from '../pong/TournamentView.js';
import { ProfileView } from '../profile/ProfileView.js';
import { RegisterView } from '../login/RegisterView.js';
import { LoginView } from '../login/LoginView.js';
import { PasswordResetView } from '../login/PasswordResetView.js';
import { PasswordResetDoneView } from '../login/PasswordResetDoneView.js';
import { PasswordResetConfirmView } from '../login/PasswordResetConfirmView.js';
import { PasswordResetCompleteView } from '../login/PasswordResetCompleteView.js';
import { AuthService } from '../index/AuthService.js';


Router.subscribe('home', HomeView);
Router.subscribe('profile', ProfileView);
Router.subscribe('pong', PongView);
Router.subscribe('tournament', TournamentView);
Router.subscribe('register', RegisterView);
Router.subscribe('login', LoginView);
Router.subscribe('password-reset', PasswordResetView);
Router.subscribe('password-reset-done', PasswordResetDoneView);
Router.subscribe('password-reset-confirm', PasswordResetConfirmView);
Router.subscribe('password-reset-complete', PasswordResetCompleteView);


await AuthService.init();
Router.init();
