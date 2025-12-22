# Deployment Guide

This guide covers deploying the AI Financial Analyst application to production.

## Prerequisites

- Python 3.10+
- Node.js 18+
- Google Gemini API Key
- Domain name (optional)
- SSL certificate (recommended for production)

## Backend Deployment

### Option 1: Deploy to a VPS (Ubuntu/Debian)

#### 1. Prepare the Server

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.10 python3.10-venv python3-pip nginx -y

# Install supervisor for process management
sudo apt install supervisor -y
```

#### 2. Setup Application

```bash
# Create application directory
sudo mkdir -p /var/www/financial-analyst
cd /var/www/financial-analyst

# Clone repository (or upload files)
git clone <your-repo-url> .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

#### 3. Configure Environment

```bash
# Create .env file
nano .env
```

Add the following:
```env
GOOGLE_API_KEY=your_actual_api_key_here
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

#### 4. Setup Supervisor

Create supervisor configuration:

```bash
sudo nano /etc/supervisor/conf.d/financial-analyst.conf
```

Add:
```ini
[program:financial-analyst]
directory=/var/www/financial-analyst/backend
command=/var/www/financial-analyst/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/financial-analyst.err.log
stdout_logfile=/var/log/financial-analyst.out.log
```

Start the service:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start financial-analyst
```

#### 5. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/financial-analyst
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/financial-analyst /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. Setup SSL (Optional but Recommended)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Option 2: Deploy to Railway/Render

#### Railway

1. Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. Add environment variables in Railway dashboard:
   - `GOOGLE_API_KEY`
   - `PORT` (automatically set by Railway)

3. Deploy via GitHub integration

#### Render

1. Create `render.yaml`:
```yaml
services:
  - type: web
    name: financial-analyst-api
    env: python
    buildCommand: "cd backend && pip install -r requirements.txt"
    startCommand: "cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: GOOGLE_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.10.0
```

2. Connect repository and deploy

## Frontend Deployment

### Option 1: Deploy to Vercel

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
cd frontend
vercel --prod
```

3. Configure environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL=https://your-api-domain.com`

### Option 2: Deploy to Netlify

1. Build the application:
```bash
cd frontend
npm run build
```

2. Deploy via Netlify CLI:
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=.next
```

### Option 3: Self-host with PM2

1. Install PM2:
```bash
npm install -g pm2
```

2. Build and start:
```bash
cd frontend
npm run build
pm2 start npm --name "financial-analyst-frontend" -- start
pm2 save
pm2 startup
```

## Docker Deployment

### Backend Dockerfile

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - HOST=0.0.0.0
      - PORT=8000
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
```

Deploy:
```bash
docker-compose up -d
```

## Environment Variables

### Backend
- `GOOGLE_API_KEY`: Your Google Gemini API key (required)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: false)

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Monitoring

### Setup Logging

1. Configure log rotation:
```bash
sudo nano /etc/logrotate.d/financial-analyst
```

Add:
```
/var/log/financial-analyst*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### Health Checks

Monitor the API health endpoint:
```bash
curl http://your-domain.com/health
```

Setup automated monitoring with services like:
- UptimeRobot
- Pingdom
- StatusCake

## Performance Optimization

1. **Enable caching**: Already implemented in the code
2. **Use CDN**: For frontend static assets
3. **Database**: Consider adding Redis for caching if scaling
4. **Load balancing**: Use Nginx or cloud load balancers for multiple instances

## Security Checklist

- [ ] Use HTTPS in production
- [ ] Set secure environment variables
- [ ] Enable CORS only for trusted domains
- [ ] Implement rate limiting (TODO)
- [ ] Regular security updates
- [ ] Monitor API usage
- [ ] Backup configuration and data

## Troubleshooting

### Backend not starting
- Check logs: `sudo supervisorctl tail -f financial-analyst stderr`
- Verify Python version: `python3 --version`
- Check environment variables: `cat .env`

### Frontend build fails
- Clear cache: `rm -rf .next node_modules && npm install`
- Check Node version: `node --version`

### API requests failing
- Check CORS settings in `main.py`
- Verify API URL in frontend environment variables
- Check network connectivity

## Scaling

For high traffic:
1. Use multiple backend workers
2. Implement Redis for caching
3. Use a CDN for frontend
4. Consider serverless functions for specific endpoints
5. Database for storing analysis results

## Backup

Regular backups should include:
- Environment configuration files
- Application code (via Git)
- Logs (if needed for compliance)

## Support

For issues:
1. Check logs first
2. Review API documentation
3. Test endpoints with curl
4. Check GitHub issues
