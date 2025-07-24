# 🔄 Car Finder Update Workflow Guide

## 🎯 **Quick Reference:**

| **What Changed** | **Best Script** | **Time** | **When to Use** |
|------------------|----------------|----------|-----------------|
| 🐍 **Python only** | `./quick-backend-fix.sh` | 3 min | Backend logic, API changes |
| 🎨 **Frontend only** | `./rebuild-with-frontend.sh` | 5 min | React components, styles |
| 🔧 **Config/Env only** | `./restart.sh` | 30 sec | Environment variables |
| 💥 **Both/Major changes** | `./final-rebuild.sh` | 8 min | Complete features |
| 🧹 **Everything broken** | `./cleanup-and-redeploy.sh` | 10 min | Nuclear option |

---

## 📝 **Detailed Scenarios:**

### 🐍 **Python Backend Changes**
**What counts as backend changes:**
- `src/` folder files (API endpoints, services, models)
- `requirements.txt` dependencies
- Backend configuration

**Best Script:**
```bash
./quick-backend-fix.sh
```
**Why:** Only rebuilds backend container, frontend stays cached ✅

---

### 🎨 **Frontend Changes**
**What counts as frontend changes:**
- `frontend/src/` React components
- `frontend/` styles, assets
- `package.json` dependencies

**Best Script:**
```bash
./rebuild-with-frontend.sh
```
**Why:** Rebuilds frontend first, then updates Docker image ✅

**Alternative (2-step):**
```bash
# Step 1: Build frontend locally
cd frontend && npm run build && cd ..

# Step 2: Update Docker with new build
./quick-backend-fix.sh
```

---

### 🔧 **Configuration Only**
**What counts as config changes:**
- `.env` file changes
- `docker-compose.yml` tweaks
- No code changes

**Best Script:**
```bash
./restart.sh
```
**Why:** Just restarts services with new config ⚡

---

### 💥 **Major Changes (Both Backend + Frontend)**
**What counts as major changes:**
- New features touching both sides
- Database schema changes
- Docker configuration changes

**Best Script:**
```bash
./final-rebuild.sh
```
**Why:** Complete rebuild with Playwright browser fix ✅

---

### 🧹 **When Everything Goes Wrong**
**Use when:**
- Multiple errors
- Containers won't start
- Mysterious issues

**Nuclear Option:**
```bash
./cleanup-and-redeploy.sh
```
**Why:** Stops everything, cleans up, fresh start 🔥

---

## ⚡ **Speed Optimization Tips:**

### 🏃‍♂️ **For Rapid Development:**
1. **Python changes:** Use `./quick-backend-fix.sh` (3 min)
2. **Frontend changes:** Build locally + `./quick-backend-fix.sh` (4 min total)
3. **Config only:** Use `./restart.sh` (30 sec)

### 🧪 **For Testing:**
```bash
# After any update, verify:
curl http://98.81.130.84:8001/health
curl http://98.81.130.84:8001/
```

---

## 🔍 **Troubleshooting:**

### ❌ **If Script Fails:**
1. Check Docker is running: `docker ps`
2. Check logs: `docker-compose logs car-finder-backend`
3. Try nuclear option: `./cleanup-and-redeploy.sh`

### 🕵️ **If Frontend Still Empty:**
1. Hard refresh browser (Cmd+Shift+R)
2. Check if assets load: `curl http://98.81.130.84:8001/assets/`
3. Try incognito/private window

### 🚨 **If Backend Won't Start:**
1. Check containers: `docker-compose ps`
2. Check specific logs: `docker-compose logs car-finder-backend`
3. Rebuild: `./final-rebuild.sh`

---

## 🎯 **Recommended Development Workflow:**

### 🔄 **Daily Development:**
```bash
# 1. Make your changes locally
# 2. Choose the right script based on what changed
# 3. Test the deployment
# 4. If broken, escalate to more comprehensive script
```

### 📋 **Script Escalation Order:**
1. `./restart.sh` (config only)
2. `./quick-backend-fix.sh` (Python changes)
3. `./rebuild-with-frontend.sh` (Frontend changes)
4. `./final-rebuild.sh` (major changes)
5. `./cleanup-and-redeploy.sh` (nuclear option)

---

## 🚀 **Pro Tips:**

✅ **Always start with the fastest script that applies to your changes**
✅ **Keep browser dev tools open to see real-time errors**
✅ **Use incognito windows to avoid cache issues**
✅ **Check `/health` endpoint first to verify backend is up**
✅ **Use `./scripts-guide.sh` to review all available scripts**

---

## 📞 **Quick Commands:**

```bash
# Show all scripts
./scripts-guide.sh

# Check what's running
docker-compose ps

# View logs
docker-compose logs car-finder-backend

# Test health
curl http://98.81.130.84:8001/health

# Test frontend
curl http://98.81.130.84:8001/
```

**Your Car Finder:** 🌐 http://98.81.130.84:8001 