# Development Environment Setup

This guide explains how to set up the development environment with **hot reload** for instant frontend updates.

## 🚀 Quick Start

### Development Mode (Hot Reload)
```bash
./start-dev.sh
```

This will start:
- **Frontend**: http://localhost:8001 (with hot reload)
- **Backend**: http://localhost:8000 
- **MongoDB Admin**: http://localhost:8082

### Stop Development Mode
```bash
./stop-dev.sh
```

### Production Mode
```bash
./start.sh  # Your existing production setup
```

## 🔥 Hot Reload Features

When running in development mode:

✅ **Instant Updates**: Edit `frontend/src/App.jsx` and see changes immediately  
✅ **No Rebuild**: No need to rebuild Docker containers  
✅ **Auto Refresh**: Browser automatically refreshes on file changes  
✅ **Live CSS**: Tailwind CSS changes update instantly  
✅ **Component Hot Swap**: React components update without losing state  

## 📁 Watched Files

The following files trigger automatic reload when changed:
- `frontend/src/**/*` - All React components, styles, and JS files
- `frontend/index.html` - Main HTML template
- `frontend/vite.config.js` - Vite configuration
- `frontend/tailwind.config.js` - Tailwind CSS config

## 🛠️ Backend Hot Reload

The backend also includes auto-reload for Python files:
- Edit any file in `src/` and the FastAPI server will restart automatically
- API changes are reflected immediately without container rebuild

## 📋 Environment Setup

Make sure you have a `.env` file with:
```env
PERPLEXITY_API_KEY=your_perplexity_key
FIRECRAWL_API_KEY=your_firecrawl_key
```

## 🔧 Troubleshooting

### Frontend not updating?
1. Check if the container is running: `docker ps`
2. Check frontend logs: `docker logs car-finder-frontend-dev`
3. Try refreshing the browser manually

### API calls failing?
- The frontend proxies `/api` calls to the backend automatically
- Backend should be accessible at `http://localhost:8000`

### Port conflicts?
- Development uses different ports than production
- Frontend: 8001 (dev) vs 8001 (prod - static build)
- Backend: 8000 (dev) vs 8000 (prod)

## 🏗️ Architecture

**Development Mode:**
```
Browser → localhost:8001 (Vite Dev Server) → localhost:8000 (FastAPI)
```

**Production Mode:**
```
Browser → localhost:8001 (FastAPI serves static build)
```

## 📝 Development Workflow

1. Start development mode: `./start-dev.sh`
2. Open http://localhost:8001 in your browser
3. Edit `frontend/src/App.jsx` or any React component
4. Watch the browser update automatically! 🎉
5. Make backend changes in `src/` - server restarts automatically
6. When done: `./stop-dev.sh`

For production deployment, use your existing `./start.sh` script. 