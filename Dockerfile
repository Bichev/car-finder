FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV NODE_VERSION=18

# Set work directory
WORKDIR /app

# Install system dependencies including Node.js and Playwright browser requirements
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        wget \
        ca-certificates \
        gnupg \
        # Node.js installation dependencies
        && curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
        && apt-get install -y nodejs \
        # Playwright browser dependencies
        && apt-get install -y --no-install-recommends \
        libxext6 \
        libxfixes3 \
        libxrandr2 \
        libgbm1 \
        libpango-1.0-0 \
        libcairo2 \
        libasound2 \
        libatspi2.0-0 \
        libdrm2 \
        libxcomposite1 \
        libxdamage1 \
        libxss1 \
        libgconf-2-4 \
        libxkbcommon0 \
        libgtk-3-0 \
        # NSS libraries for browser security
        libnss3 \
        libnspr4 \
        # Additional browser dependencies
        libdbus-1-3 \
        libxcursor1 \
        libxi6 \
        libxtst6 \
        # Additional dependencies for Playwright
        xvfb \
        fonts-liberation \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (before switching to non-root user)
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy and build frontend
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

# Switch back to app directory and copy backend
WORKDIR /app
COPY . .

# Move built frontend to static directory
RUN mkdir -p /app/static && cp -r /app/frontend/dist/* /app/static/

# Create non-root user
RUN adduser --disabled-password --gecos '' --shell /bin/bash user \
    && chown -R user:user /app
USER user

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 