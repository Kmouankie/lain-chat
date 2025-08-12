#  Serial Experiments Lain Chat

> *"Present day, present time... Let's all love Lain"*

A real-time chat application inspired by the iconic anime Serial Experiments Lain, featuring temporal message corruption, authentic CRT terminal aesthetics, and anonymous communication in the Wired.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Django](https://img.shields.io/badge/django-v4.2.7-green.svg)
![WebSocket](https://img.shields.io/badge/websocket-real--time-orange.svg)
![Status](https://img.shields.io/badge/status-production--ready-success.svg)

##  Features

###  Core Functionality
- **Real-time WebSocket communication** with automatic reconnection
- **8 themed chat rooms** with unique personalities and corruption timers
- **Temporal message corruption** - messages disappear after room-specific intervals
- **Interactive countdown timers** showing message corruption in real-time
- **Lain-style commands** for enhanced interaction (`/help`, `/cyberia`, `/corrupt`, etc.)

###  Authentication System
- **Email/password authentication** for registered users
- **Anonymous quick-connect** for temporary access
- **Automatic Lain-style pseudonym generation**
- **Secure session management** with anonymized hashing

###  Interface Design
- **Authentic CRT terminal aesthetics** inspired by Serial Experiments Lain
- **Glitch effects and animations** (corruption, phantom, spectral)
- **Room-specific visual themes** with dynamic colors and borders
- **Responsive design** with scan lines and CRT effects
- **Google Fonts integration** (JetBrains Mono, Share Tech Mono)

###  Security Features
- **4-layer custom middleware** security system
- **Content Security Policy (CSP)** configuration
- **Complete request anonymization**
- **Token bucket rate limiting**
- **Input validation and sanitization**
- **Advanced security headers**

##  Chat Rooms

Each room has its own personality and message corruption timer:

| Room | Corruption Time | Theme |
|------|----------------|-------|
| **General** | ∞ (Permanent) | Open discussion |
| **Cyberia** | 30 seconds | Nightclub atmosphere |
| **Protocol7** | 20 seconds | Technical discussions |
| **Knights** | 15 seconds | Gaming community |
| **Wired** | 10 seconds | Network discussions |
| **Navi** | 8 seconds | AI and technology |
| **Phantom** | 6 seconds | Mystery and secrets |
| **Masami** | 4 seconds | Ultra-fast ephemeral chat |

##  Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd lain_chat_project
```

2. **Create virtual environment**
```bash
python -m venv lain_env
# Windows
lain_env\Scripts\Activate.ps1
# Linux/Mac
source lain_env/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
Create a `.env` file with:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=lain_chat
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379
```

5. **Database setup**
```bash
cd lain_chat
python manage.py makemigrations
python manage.py migrate
```

6. **Run the server**
```bash
python -m daphne -b 127.0.0.1 -p 8000 lain_chat.asgi:application
```

Visit `http://localhost:8000` to start chatting in the Wired!

##  Available Commands

Type these commands in any chat room:

- `/help` - Show available commands
- `/present_day` - Display the iconic Lain quote
- `/god_knows` - Mystery command
- `/nobody` - Anonymity reminder
- `/corrupt [seconds]` - Custom corruption timer
- `/cyberia` - Enter Cyberia mode
- `/knights` - Gaming mode activation
- `/masami` - Ultra-fast chat mode
- `/navi` - AI assistant mode
- `/protocol` - Technical mode
- `/wired` - Network mode
- `/glitch` - Visual glitch effect
- `/spectral` - Spectral animation
- `/phantom` - Phantom mode

##  Architecture

### Tech Stack
- **Backend**: Django 4.2.7 + Django Channels + WebSockets + Daphne
- **Frontend**: Vanilla JavaScript + CSS3 animations
- **Database**: PostgreSQL + Redis
- **Security**: Custom middleware stack + CSP
- **Deployment**: Railway/Render ready

### Project Structure
```
lain_chat_project/
├── lain_chat/           # Main Django project
├── chat/                # Chat application logic
├── security/            # Security middleware
├── anonymization/       # User anonymization system
├── auth/                # Authentication system
├── static/              # CSS, JS, and assets
└── templates/           # HTML templates
```

### Key URLs
- `/` - Home page
- `/auth/login/` - User login
- `/auth/register/` - User registration
- `/auth/quick-connect/` - Anonymous access
- `/chat/` - Room selection
- `/chat/<room>/` - Individual chat rooms
- `/ws/chat/<room>/` - WebSocket endpoints

##  Deployment

### Railway (Recommended)
1. Connect your GitHub repository
2. Add environment variables
3. Deploy automatically with included `Procfile`

### Render
1. Create new Web Service
2. Connect repository
3. Add environment variables
4. Deploy with provided configuration

### Environment Variables for Production
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DB_NAME=production_db_name
DB_USER=production_db_user
DB_PASSWORD=production_db_password
DB_HOST=production_db_host
DB_PORT=5432
REDIS_URL=redis://production-redis-url
```

##  Testing

Test the application features:

1. **Anonymous Connection**
   - Visit `/auth/quick-connect/`
   - Get auto-generated Lain-style username
   - Join any chat room

2. **Message Corruption**
   - Send messages in different rooms
   - Watch countdown timers
   - Observe corruption animations

3. **Commands**
   - Try `/help` for command list
   - Test `/cyberia` for room effects
   - Use `/corrupt 10` for custom timers

4. **Multiple Users**
   - Open multiple browser tabs
   - Test real-time synchronization
   - Verify message corruption timing

##  Customization

### Adding New Rooms
1. Update `ROOMS` dictionary in `consumers.py`
2. Add corruption timer in `CORRUPTION_TIMES`
3. Create room-specific CSS styles
4. Add URL pattern in `urls.py`

### Modifying Visual Effects
- Edit `static/css/lain-effects.css` for animations
- Customize `static/css/terminal.css` for terminal styling
- Modify `static/js/lain-terminal.js` for interactions

### Security Configuration
- Adjust middleware in `security/middleware.py`
- Update CSP headers in `settings.py`
- Configure rate limiting parameters

##  Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- Inspired by **Serial Experiments Lain** anime series
- Terminal aesthetics influenced by retro computing
- Built with love for the Wired community

##  Known Issues

- WebSocket reconnection may take a few seconds on network changes
- Some browsers may require HTTPS for full WebSocket functionality in production
- CRT effects may impact performance on older devices

##  Future Enhancements

- Private room creation
- Message history persistence
- Mobile app development
- Voice chat integration
- Advanced moderation tools
- Friend system (anonymous)
- Push notifications

---

*"No matter where you go, everyone's connected."* - Lain Iwakura


