import { UserPage } from '../js/UserPage.js'
import { HomePage } from '../js/HomePage.js'
import { ProfilePage } from '../js/ProfilePage.js'
import { SinglePongPage } from '../js/SinglePong.js'

// Register routes
Router.subscribe('home', HomePage)
Router.subscribe('users', UserPage)
Router.subscribe('profile', ProfilePage)
Router.subscribe('pong', SinglePongPage)


Router.init()
