# 🎮 ft_transcendence
**Final project of the 42 School Common Core curriculum.**  
A full-stack web application featuring a real-time Pong game, user authentication, chat functionalities, and more.
![Pong Gameplay](./screenshots/gameplay.gif)
---
## 🚀 Features
- **Real-Time Multiplayer Pong Game**: Play classic Pong against others with modern visuals and smooth controls.
- **User Authentication**: OAuth2 via 42 API with Two-Factor Authentication using Google Authenticator.
- **User Profiles**: Customize usernames and avatars, view match history, and track statistics.
- **Friend System**: Add friends, view their online status, and challenge them to matches.
- **ELO Ranking System**: Competitive leaderboard based on player performance.
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

2. Log in using your 42 account and configure your profile or register a new profile.
