# 🎮 ft_transcendence
**Final project of the 42 School Common Core curriculum.**  
A full-stack web application featuring a real-time Pong game, user authentication, chat functionalities, and more.
![Pong Gameplay](./screenshots/gameplay.gif)
---
## 📚 Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
---
## 🚀 Features
- **Real-Time Multiplayer Pong Game**: Play classic Pong against others with modern visuals and smooth controls.
- **Custom Matchmaking**: Send game invitations and join ongoing matches.
- **User Authentication**: OAuth2 via 42 API with Two-Factor Authentication using Google Authenticator.
- **User Profiles**: Customize usernames and avatars, view match history, and track statistics.
- **Friend System**: Add friends, view their online status, and challenge them to matches.
- **Comprehensive Chat System**: Public, private, and password-protected channels with moderation capabilities.
- **Direct Messaging**: Private conversations between users with persistent message history.
- **Channel Management**: Create channels with ownership and administrator privileges.
- **Blocking System**: Manage unwanted interactions with other users.
- **ELO Ranking System**: Competitive leaderboard based on player performance.
- **Spectator Mode**: Watch ongoing matches in real-time.
- **Responsive Design**: Seamless experience across devices.
---
## 🛠️ Tech Stack
- **Frontend**: Vue.js with TypeScript
- **Backend**: NestJS with TypeScript
- **Database**: PostgreSQL with TypeORM
- **Authentication**: 42 OAuth2, JWT, Passport.js, Google Authenticator
- **Real-Time Communication**: Socket.io
- **Containerization**: Docker & Docker Compose
---
## 💾 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Ekkoz897/42cursus_ft_transcendence.git
   cd 42cursus_ft_transcendence
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration, including OAuth credentials
   ```

3. Build and run with Docker:
   ```bash
   docker-compose up --build
   ```
---
## 🖥️ Usage
1. Access the application:
   ```
   Frontend: http://localhost:8080
   Backend API: http://localhost:3000
   ```

2. Log in using your 42 account and configure your profile.

3. Navigate through the interface to:
   - Challenge other players to Pong matches
   - Join or create chat channels
   - Add friends and send direct messages
   - View leaderboards and match history
   - Watch ongoing games as a spectator
---
