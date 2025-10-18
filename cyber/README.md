# Cyber Intelligence Platform

A modern threat monitoring and analysis platform built with Next.js and Flask SQLAlchemy backend.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- PostgreSQL (for production)

### Setup

1. **Clone and Install Frontend**
   ```bash
   git clone <your-repo>
   cd cyber
   npm install
   ```

2. **Set up Flask Backend**
   ```bash
   cd flask_backend
   pip install -r requirements.txt
   python app.py
   ```

3. **Environment Variables**
   Create `.env.local` in cyber directory:
   ```env
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

4. **Run Development Servers**
   ```bash
   # Terminal 1: Backend
   cd flask_backend && python app.py
   
   # Terminal 2: Frontend  
   cd cyber && npm run dev
   ```

## 🏗️ Tech Stack

- **Frontend**: Next.js 15, React 18, TypeScript
- **Backend**: Flask, SQLAlchemy, JWT Authentication
- **Database**: SQLite (development), PostgreSQL (production)
- **UI**: Tailwind CSS, Radix UI
- **Authentication**: Flask-JWT-Extended

## 📁 Project Structure

```
project/
├── cyber/              # Next.js frontend
│   ├── src/
│   │   ├── app/        # Next.js app router
│   │   ├── components/ # React components
│   │   ├── contexts/   # React contexts
│   │   └── lib/        # Utilities and configs
│   └── public/         # Static assets
└── flask_backend/      # Flask API backend
    ├── models/         # SQLAlchemy models
    ├── routes/         # API endpoints
    ├── migrations/     # Database migrations
    └── app.py          # Main application
```

## 🔒 Authentication

The app uses Flask-JWT-Extended with:
- JWT tokens for session management
- Role-based access control (Admin, Analyst)
- Google OAuth integration
- Secure password hashing

## 🗄️ Database

Using SQLAlchemy ORM with the following main tables:
- `system_users` - Admins and analysts with authentication
- `users` - Monitored users from various platforms  
- `sources` - Data sources (Telegram, Discord, etc.)
- `content` - Analyzed content with risk scores
- `cases` - Investigation cases
- `keywords` - Threat keywords and weights

## 🚀 Deployment

### Option 1: Railway (Recommended)
```bash
railway login
railway init
railway add postgresql
railway deploy
```

### Option 2: Heroku
```bash
heroku create your-app
heroku addons:create heroku-postgresql:mini
git push heroku main
```

### Frontend Deployment
1. Deploy to Vercel/Netlify
2. Set `NEXT_PUBLIC_API_URL` to your backend URL
3. Build and deploy

## 📝 License

MIT License
