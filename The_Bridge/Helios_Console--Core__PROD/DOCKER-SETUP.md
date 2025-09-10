# 🐳 Docker Setup - Helios Console

## Quick Start

### Step 1: Enable Docker WSL Integration

1. **Open Docker Desktop** on Windows
2. **Go to Settings** → **Resources** → **WSL Integration**
3. **Enable integration** with your Ubuntu/WSL distro
4. **Apply & Restart** Docker Desktop

### Step 2: Run the Application

```bash
# Simple one-command start
./docker-start.sh
```

**Or manually:**

```bash
# Development mode (hot reload) - Port 3000
docker-compose up --build helios-console-dev

# Production mode - Port 3001  
docker-compose --profile production up --build helios-console-prod
```

## 🎯 What You'll Get

### **Development Mode** (Port 3000)
- ✅ Hot reloading for code changes
- ✅ Demo mode with realistic data
- ✅ All 4 pages functional
- ✅ Fast development workflow

### **Production Mode** (Port 3001)
- ✅ Optimized production build
- ✅ Smaller container size
- ✅ Production-ready configuration

## 🌟 Features Available

Once running, visit **http://localhost:3000** to see:

### **Operations Dashboard** (`/ops`)
- Real-time operational metrics
- Throughput: 2.1 t/h, Efficiency: 94.5%
- Cost tracking and system health

### **Trace Events** (`/trace`)  
- Supply chain event stream
- Harvest → Processing → Logistics → Blockchain
- Real-time updates with detailed payloads

### **Farm Management** (`/admin/farms`)
- 5 demo farms across Kenya
- Status tracking and hectare information
- Geographic locations and management

### **Agent Monitoring** (`/agents`)
- 8 AI agents with different roles
- Live status: Online/Degraded/Offline
- T1/T2/T3 tier classifications

## 🔄 Environment Switching

The Docker setup supports both demo and real API modes:

### **Demo Mode** (Default)
```yaml
NEXT_PUBLIC_DEMO_MODE=true
```
- Uses local demo data
- No external API calls
- Perfect for development and demos

### **Real API Mode** (After Backend Deployment)
```yaml
NEXT_PUBLIC_DEMO_MODE=false
NEXT_PUBLIC_API_BASE_URL=https://cn-dev-api.greenstemglobal.com
```

Update the environment variables in `docker-compose.yml` to switch modes.

## 🛠️ Development Workflow

### **Code Changes**
- Edit files in your local directory
- Changes are automatically reflected (hot reload)
- No need to rebuild container for code changes

### **Dependency Changes**
```bash
# Rebuild if you modify package.json
docker-compose down
docker-compose up --build helios-console-dev
```

### **Environment Changes**
```bash
# Edit docker-compose.yml environment variables
# Restart container
docker-compose restart helios-console-dev
```

## 🐛 Troubleshooting

### **Docker not found in WSL**
```bash
# Enable WSL integration in Docker Desktop:
# Settings > Resources > WSL Integration > Enable your distro
```

### **Port already in use**
```bash
# Stop any running containers
docker-compose down

# Or use different ports in docker-compose.yml
```

### **Build failures**
```bash
# Clean everything and rebuild
docker-compose down --volumes
docker system prune -f
docker-compose up --build
```

### **Slow build times**
- First build takes 5-10 minutes (downloading dependencies)
- Subsequent builds are much faster (cached layers)
- Use `docker system prune` occasionally to clean up

## 📁 Docker Files Created

```
├── Dockerfile              # Multi-stage build for dev/prod
├── docker-compose.yml      # Service orchestration  
├── .dockerignore           # Optimized build context
├── docker-start.sh         # Easy start script
└── DOCKER-SETUP.md         # This guide
```

## 🎉 Benefits of Docker Setup

✅ **Consistent Environment**: Same Node.js version everywhere  
✅ **No npm Issues**: Fresh container every time  
✅ **Easy Sharing**: Works on any machine with Docker  
✅ **Production Ready**: Same container for dev and prod  
✅ **Hot Reloading**: Fast development experience  
✅ **Clean Isolation**: No conflicts with system packages  

---

**Ready to go! Run `./docker-start.sh` and your Helios Console will be available at http://localhost:3000** 🚀