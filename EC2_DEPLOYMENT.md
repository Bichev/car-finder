# 🚀 Car Finder - EC2 Docker Deployment Guide

Deploy your AI-powered Car Finder service on **EC2 with complete isolation** using Docker Compose. This setup ensures no conflicts with your other projects.

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────────────────────────┐
│                        EC2 Instance                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                Docker Network                         │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │   MongoDB   │  │  Car Finder │  │ Mongo Admin │   │  │
│  │  │   :27018    │  │    :8001    │  │    :8082    │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📦 **What You Get**

✅ **Complete Isolation** - Own Docker network, no conflicts  
✅ **Custom Ports** - 8001 (app), 27018 (mongo), 8082 (admin)  
✅ **MongoDB Database** - Persistent data storage  
✅ **Admin Interface** - MongoDB management UI  
✅ **Health Checks** - Automatic service monitoring  
✅ **Resource Limits** - Controlled memory/CPU usage  
✅ **Auto-restart** - Services restart on failure  

## 🛠️ **Prerequisites**

### **1. EC2 Instance Requirements**
- **Instance Type:** t3.medium or larger (2GB+ RAM recommended)
- **Storage:** 20GB+ EBS volume
- **Security Group:** Open ports 8001, 8082 (optional: 22 for SSH)
- **OS:** Ubuntu 20.04+ or Amazon Linux 2

### **2. Install Docker & Docker Compose**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again to apply docker group
exit
```

### **3. Clone Your Repository**

```bash
git clone https://github.com/your-username/car-finder.git
cd car-finder
```

## 🚀 **Quick Deployment**

### **1. Configure Environment**

```bash
# Copy environment template
cp env.example .env

# Edit with your settings
nano .env
```

**Required settings in `.env`:**
```bash
PERPLEXITY_API_KEY=your_actual_api_key
EC2_PUBLIC_IP=your.ec2.public.ip  # Your EC2's public IP
```

### **2. Deploy Services**

```bash
# Make scripts executable
chmod +x deploy.sh stop.sh restart.sh

# Deploy (builds and starts everything)
./deploy.sh
```

### **3. Access Your Services**

Once deployed, access your services:

- **🌐 Car Finder App:** `http://your-ec2-ip:8001`
- **📊 MongoDB Admin:** `http://your-ec2-ip:8082`
- **📚 API Docs:** `http://your-ec2-ip:8001/docs`
- **🏥 Health Check:** `http://your-ec2-ip:8001/health`

## 🔧 **Management Commands**

### **Daily Operations**

```bash
# View service status
docker-compose ps

# View logs
docker-compose logs -f car-finder-backend

# Restart services (without rebuilding)
./restart.sh

# Stop services
./stop.sh

# Redeploy (rebuild + restart)
./deploy.sh
```

### **Troubleshooting**

```bash
# Check service health
curl http://localhost:8001/health

# Enter backend container
docker-compose exec car-finder-backend bash

# View MongoDB logs
docker-compose logs car-finder-mongo

# Restart specific service
docker-compose restart car-finder-backend
```

## 🔒 **Security Configuration**

### **1. EC2 Security Group**

**Inbound Rules:**
```
Port 22   - SSH (your IP only)
Port 8001 - Car Finder App (0.0.0.0/0 or specific IPs)
Port 8082 - MongoDB Admin (your IP only - optional)
```

### **2. Update Default Passwords**

**Edit `.env` file:**
```bash
MONGO_ROOT_PASSWORD=your_secure_password_here
MONGO_ADMIN_PASSWORD=your_admin_password_here
```

### **3. Firewall (Optional)**

```bash
# Install UFW
sudo apt install ufw

# Allow SSH
sudo ufw allow 22

# Allow Car Finder
sudo ufw allow 8001

# Enable firewall
sudo ufw enable
```

## 📊 **Monitoring & Maintenance**

### **1. Service Health**

Monitor your services:
```bash
# Health check endpoint
curl http://localhost:8001/health

# Service status
docker-compose ps

# Resource usage
docker stats
```

### **2. Logs Management**

```bash
# View recent logs
docker-compose logs --tail=50 car-finder-backend

# Follow logs
docker-compose logs -f

# Clear old logs (free space)
docker system prune -f
```

### **3. Backup Data**

```bash
# Backup MongoDB data
docker-compose exec car-finder-mongo mongodump --out /backup

# Copy backup from container
docker cp car-finder-mongo:/backup ./mongodb-backup-$(date +%Y%m%d)
```

## 🔄 **Updates & Deployments**

### **1. Update Code**

```bash
# Pull latest changes
git pull origin main

# Redeploy with new code
./deploy.sh
```

### **2. Environment Changes**

```bash
# Edit environment
nano .env

# Restart to apply changes
./restart.sh
```

## 🐛 **Common Issues & Solutions**

### **Port Conflicts**

**Problem:** Port 8001 already in use
```bash
# Check what's using the port
sudo netstat -tulpn | grep 8001

# Kill the process
sudo kill -9 <PID>

# Or change ports in .env and docker-compose.yml
```

### **Memory Issues**

**Problem:** Out of memory errors
```bash
# Check memory usage
free -h
docker stats

# Reduce resource limits in docker-compose.yml
memory: 1G  # Instead of 2G
```

### **Docker Issues**

**Problem:** Docker daemon not running
```bash
# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Check status
sudo systemctl status docker
```

### **Database Connection Issues**

**Problem:** Cannot connect to MongoDB
```bash
# Check MongoDB container
docker-compose logs car-finder-mongo

# Restart MongoDB
docker-compose restart car-finder-mongo

# Verify network
docker network ls
```

## 📈 **Performance Optimization**

### **1. EC2 Instance**

- **Upgrade to t3.large** for better performance
- **Add EBS-optimized** for faster disk I/O
- **Use SSD storage** (gp3) for better IOPS

### **2. Application Settings**

**Optimize in docker-compose.yml:**
```yaml
deploy:
  resources:
    limits:
      memory: 4G      # Increase for more memory
      cpus: '2.0'     # Use more CPU cores
```

### **3. Database Optimization**

```bash
# MongoDB performance settings
# Add to docker-compose.yml under car-finder-mongo:
command: mongod --wiredTigerCacheSizeGB 0.5
```

## 🎯 **Production Checklist**

- [ ] **Environment configured** with real API keys
- [ ] **Security group** properly configured
- [ ] **Passwords changed** from defaults
- [ ] **Health checks** working
- [ ] **Logs** being generated
- [ ] **Backup strategy** in place
- [ ] **Monitoring** set up
- [ ] **Domain name** configured (optional)
- [ ] **SSL certificate** installed (optional)

## 🆘 **Need Help?**

1. **Check logs first:** `docker-compose logs -f`
2. **Verify health:** `curl http://localhost:8001/health`
3. **Restart services:** `./restart.sh`
4. **Full redeploy:** `./deploy.sh`

## 🎉 **Success!**

Your **AI-powered Car Finder** is now running in complete isolation on your EC2 instance! 

🌐 **Access:** `http://your-ec2-ip:8001`  
🚗 **Search cars** with AI-powered market analysis  
📊 **Monitor** via MongoDB Admin interface  
🔒 **Secure** and isolated from other projects  

**Happy car hunting!** 🚗✨ 