# 🚀 Deployment Guide - Render.com

This guide walks you through deploying your Car Finder service to Render.com for **free hosting**.

## 📋 Prerequisites

1. **GitHub Account** - Your code should be pushed to GitHub
2. **Render Account** - Sign up at [render.com](https://render.com)
3. **Perplexity API Key** - From [perplexity.ai](https://www.perplexity.ai/)

## 🛠️ Step 1: Prepare Your Repository

Make sure your code is pushed to GitHub:

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

## 🎯 Step 2: Deploy to Render

### Option A: Automatic Deployment (Recommended)

1. **Connect GitHub to Render:**
   - Go to [render.com](https://render.com) and sign in
   - Click "New +" → "Web Service"
   - Select "Build and deploy from a Git repository"
   - Connect your GitHub account
   - Select your `car-finder` repository

2. **Configure the Service:**
   ```
   Name: car-finder
   Environment: Docker
   Branch: main
   Dockerfile Path: ./Dockerfile
   ```

3. **Set Environment Variables:**
   - Click "Advanced" → "Add Environment Variable"
   - Add: `PERPLEXITY_API_KEY` = `your_api_key_here`
   - Add: `PORT` = `8000`
   - Add: `PYTHONPATH` = `/app`

4. **Deploy:**
   - Click "Create Web Service"
   - Wait 10-15 minutes for the build to complete

### Option B: Using render.yaml (Alternative)

The included `render.yaml` file will automatically configure your service:

1. Just connect your GitHub repo to Render
2. Render will automatically detect the `render.yaml` file
3. Set your `PERPLEXITY_API_KEY` in the dashboard

## 🔧 Step 3: Set Environment Variables

In your Render dashboard:

1. Go to your service → "Environment"
2. Add these variables:
   ```
   PERPLEXITY_API_KEY = your_actual_api_key
   PORT = 8000
   PYTHONPATH = /app
   ENVIRONMENT = production
   ```

## ✅ Step 4: Verify Deployment

Once deployed, your service will be available at:
```
https://your-service-name.onrender.com
```

**Test the endpoints:**
- **Frontend:** `https://your-service-name.onrender.com`
- **API Docs:** `https://your-service-name.onrender.com/docs`
- **Health Check:** `https://your-service-name.onrender.com/health`

## 🎨 Features Included

✅ **Full-Stack Hosting** - React frontend + FastAPI backend  
✅ **Playwright Support** - Browser automation works in production  
✅ **Free Tier** - 750 hours/month included  
✅ **Custom Domain** - Add your own domain (optional)  
✅ **HTTPS** - Automatic SSL certificates  
✅ **Auto-deploys** - Deploys on every git push  

## 🐛 Troubleshooting

### Build Failures

**Problem:** Node.js build fails
```bash
# Check if package.json exists in frontend/
# Verify build script in frontend/package.json
```

**Problem:** Playwright browser installation fails
```bash
# The Dockerfile includes proper Playwright setup
# Check logs for specific browser dependency issues
```

**Problem:** Static files not serving
```bash
# Verify the build copied files to /app/static/
# Check FastAPI logs for static mount errors
```

### Runtime Issues

**Problem:** API calls fail from frontend
```bash
# Frontend uses relative URLs in production
# Check browser console for 404 errors
```

**Problem:** Environment variables not working
```bash
# Verify PERPLEXITY_API_KEY is set in Render dashboard
# Check service logs for missing environment variables
```

## 📱 Local Testing

Test the production build locally:

```bash
# Build everything
chmod +x build.sh
./build.sh

# Run production server
python -m src.main

# Visit: http://localhost:8000
```

## 🎯 Next Steps

1. **Custom Domain:** Add your own domain in Render dashboard
2. **Monitoring:** Set up health check alerts
3. **Analytics:** Add usage tracking
4. **Scale:** Upgrade to paid plan for better performance

## 🆘 Need Help?

- **Render Docs:** [render.com/docs](https://render.com/docs)
- **FastAPI + React:** Check included configuration files
- **Playwright Issues:** Verify browser dependencies in logs

🎉 **Congratulations!** Your AI-powered car finder is now live! 