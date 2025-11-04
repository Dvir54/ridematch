# RideMatch - Intelligent Ride Sharing Platform

A microservices-based ride-sharing platform that connects drivers and passengers through intelligent matching algorithms.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Setup

```bash
# Clone and setup
git clone <repository-url>
cd ridematch

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# Run migrations
docker-compose exec auth-service alembic upgrade head

# Start frontend
cd frontend
npm install && npm run dev
```

Visit: http://localhost:3000

## 🏗️ Architecture

**6 Microservices** (FastAPI + PostgreSQL):
- `auth-service` (8001) - Authentication & user profiles
- `rides-service` (8002) - Ride management
- `search-service` (8003) - Intelligent matching algorithm
- `feedback-service` (8004) - Ratings & reviews
- `notifications-service` (8005) - Real-time notifications via WebSocket
- `admin-service` (8006) - Admin panel & monitoring

**Infrastructure**:
- **API Gateway**: Nginx (port 80)
- **Frontend**: React TypeScript PWA (port 3000)
- **Cache/Sessions**: Redis
- **Databases**: PostgreSQL (one per service)

## 📚 Key Features

- **Smart Matching**: Algorithm scores rides based on route, time, price, ratings & preferences (40-100% match)
- **Dual Mode**: Seamless switch between Driver and Passenger roles
- **Real-time**: WebSocket notifications for critical events
- **Reputation System**: Post-ride ratings to build trust
- **Secure**: JWT authentication with refresh tokens

## 🧪 Testing

```bash
# Backend tests
docker-compose exec auth-service pytest

# Frontend tests
cd frontend && npm test
```

## 📖 Documentation

- **API Docs**: http://localhost/api/auth/docs (auto-generated per service)
- **Implementation Plan**: [plan.mdc](./plan.mdc)
- **Detailed Setup**: See sections below

## 🔧 Common Commands

```bash
# View logs
docker-compose logs -f auth-service

# Database migrations
docker-compose exec auth-service alembic revision --autogenerate -m "Description"
docker-compose exec auth-service alembic upgrade head

# Restart services
docker-compose restart

# Rebuild
docker-compose up --build
```

## 📁 Project Structure

```
ridematch/
├── frontend/                    # React TypeScript PWA
├── services/
│   ├── auth-service/           # User authentication
│   ├── rides-service/          # Ride CRUD
│   ├── search-service/         # Matching algorithm
│   ├── feedback-service/       # Ratings system
│   ├── notifications-service/  # Real-time notifications
│   └── admin-service/          # Admin panel
├── nginx/                      # API Gateway config
├── docker-compose.yml
└── plan.mdc                    # Detailed implementation plan
```

## 🐛 Troubleshooting

**Services won't start?**
```bash
docker-compose logs <service-name>
docker-compose down && docker-compose up --build
```

**Port conflicts?**
```bash
# Windows: netstat -ano | findstr :8001
# Linux/Mac: lsof -i :8001
```

**Database issues?**
```bash
docker-compose down -v  # Reset volumes
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Commit changes (`git commit -m 'feat: description'`)
4. Push to branch (`git push origin feature/name`)
5. Open Pull Request

**Code Style**: Python (PEP 8 + Black), TypeScript (Prettier)

## 🎯 Current Status

**Phase 1 - Foundation** (In Progress)
- ✅ Project infrastructure
- ✅ Git repository
- ✅ Documentation
- ⏳ Environment configuration
- ⏳ Auth service implementation

See [plan.mdc](./plan.mdc) for full roadmap.

## 📝 License

MIT License

---

**For detailed architecture, deployment guides, and advanced topics, see [plan.mdc](./plan.mdc)**

