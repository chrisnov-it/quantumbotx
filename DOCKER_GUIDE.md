# 🐳 Docker Guide for QuantumBotX

## Quick Start

### First Time Setup

1. **Make sure Docker is running** on your machine

   - Windows: Docker Desktop should be running (check system tray)
   - You can verify with: `docker --version`

2. **Navigate to your project directory**

   ```bash
   cd d:\dev\quantumbotx
   ```

3. **Start the application**

   ```bash
   docker-compose up -d
   ```

   - This will build the image (first time only) and start the container
   - `-d` runs it in detached mode (background)

4. **Check if it's running**

   ```bash
   docker ps
   ```

   You should see `quantumbotx-quantumbotx-1` in the list

5. **Access your application**
   - Main app: `http://localhost:5000`
   - Health check: `http://localhost:5000/api/health`

---

## 📋 Essential Commands

### Starting & Stopping

```bash
# Start the app (builds if needed)
docker-compose up -d

# Stop the app
docker-compose down

# Restart the app
docker-compose restart

# Stop and remove everything (including volumes)
docker-compose down -v
```

### Viewing Logs

```bash
# View all logs
docker logs quantumbotx-quantumbotx-1

# Follow logs in real-time (like tail -f)
docker logs -f quantumbotx-quantumbotx-1

# View last 50 lines
docker logs --tail 50 quantumbotx-quantumbotx-1

# View logs with timestamps
docker logs -t quantumbotx-quantumbotx-1
```

### Rebuilding After Changes

```bash
# Rebuild and restart (after code changes)
docker-compose up --build -d

# Force rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Accessing the Container

```bash
# Open a shell inside the running container
docker exec -it quantumbotx-quantumbotx-1 /bin/bash

# Run a single command
docker exec quantumbotx-quantumbotx-1 python --version

# Check if Flask is installed
docker exec quantumbotx-quantumbotx-1 pip list | grep Flask

# Test CCXT connection
docker exec quantumbotx-quantumbotx-1 python test_ccxt.py
```

### Troubleshooting

```bash
# Check container status
docker ps -a

# View detailed container info
docker inspect quantumbotx-quantumbotx-1

# Remove orphaned containers
docker-compose down --remove-orphans

# Clean up all stopped containers
docker container prune

# Clean up unused images
docker image prune -a

# Nuclear option: clean everything Docker (use with caution!)
docker system prune -a --volumes
```

---

## 🔧 Configuration

### Environment Variables

Your app reads configuration from:

1. `.env` file (for local development)
2. `docker-compose.yml` (environment section for Docker)

**Important environment variables:**

- `BROKER_TYPE`: Set to `CCXT` for crypto trading (default in Docker)
- `EXCHANGE_ID`: Exchange to use (e.g., `binance`, `bybit`)
- `FLASK_HOST`: Host to bind to (default: `0.0.0.0` in Docker)
- `FLASK_PORT`: Port to bind to (default: `5000`)

### Volumes (Data Persistence)

Your `docker-compose.yml` mounts these directories:

- `./data:/app/data` - Database and persistent data
- `./logs:/app/logs` - Application logs

**What this means:** Even if you delete the container, your data and logs are safe on your host machine!

---

## 🎯 Common Workflows

### Development Workflow

1. **Make code changes** on your Windows machine
2. **Rebuild the container**:

   ```bash
   docker-compose up --build -d
   ```

3. **Check logs** to see if it worked:

   ```bash
   docker logs -f quantumbotx-quantumbotx-1
   ```

4. **Test your changes** at `http://localhost:5000`

### Debugging Workflow

1. **Check if container is running**:

   ```bash
   docker ps
   ```

2. **If it's restarting**, check the logs:

   ```bash
   docker logs quantumbotx-quantumbotx-1
   ```

3. **If you see errors**, you can:
   - Fix the code
   - Rebuild: `docker-compose up --build -d`
   - Or enter the container to debug: `docker exec -it quantumbotx-quantumbotx-1 /bin/bash`

4. **Test inside the container**:

   ```bash
   docker exec -it quantumbotx-quantumbotx-1 /bin/bash
   # Now you're inside the container
   python test_ccxt.py
   pip list
   ls -la
   exit  # to leave the container
   ```

### Production Deployment

When you're ready to deploy to a server:

1. **Copy your project** to the server
2. **Make sure `.env` is configured** with production credentials
3. **Start with**:

   ```bash
   docker-compose up -d
   ```

4. **Set up auto-restart** (already configured with `restart: unless-stopped`)

---

## 📊 Monitoring

### Check Application Health

```bash
# Quick health check
curl http://localhost:5000/api/health

# Pretty print JSON response (Windows PowerShell)
(Invoke-WebRequest http://localhost:5000/api/health).Content | ConvertFrom-Json

# Check container resource usage
docker stats quantumbotx-quantumbotx-1
```

### View Resource Usage

```bash
# See CPU, Memory, Network usage
docker stats

# One-time snapshot
docker stats --no-stream
```

---

## 🚨 Common Issues & Solutions

### Issue: Container keeps restarting

**Solution:**

```bash
# Check the logs for errors
docker logs quantumbotx-quantumbotx-1

# Common causes:
# 1. Missing dependencies → Rebuild: docker-compose up --build -d
# 2. Wrong environment variables → Check .env and docker-compose.yml
# 3. Port already in use → Change port in docker-compose.yml
```

### Issue: Can't access localhost:5000

**Solution:**

```bash
# Check if container is running
docker ps

# Check if port is mapped correctly
docker port quantumbotx-quantumbotx-1

# Try accessing from inside container
docker exec quantumbotx-quantumbotx-1 curl http://localhost:5000/api/health
```

### Issue: Changes not reflecting

**Solution:**

```bash
# You need to rebuild after code changes
docker-compose up --build -d

# For major changes, use --no-cache
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Out of disk space

**Solution:**

```bash
# Clean up old images and containers
docker system prune

# More aggressive cleanup (removes everything not in use)
docker system prune -a --volumes
```

---

## 💡 Tips & Best Practices

1. **Always use `docker-compose`** instead of raw `docker` commands for this project
2. **Check logs regularly** when developing: `docker logs -f quantumbotx-quantumbotx-1`
3. **Use volumes** for data you want to keep (already configured)
4. **Don't commit `.env`** to git (already in `.gitignore`)
5. **Rebuild after dependency changes** in `requirements-docker.txt`
6. **Use `--no-cache`** if you suspect caching issues

---

## 📚 Learning Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker CLI Cheat Sheet](https://docs.docker.com/get-started/docker_cheatsheet.pdf)

---

## 🆘 Need Help?

If you're stuck:

1. Check the logs: `docker logs quantumbotx-quantumbotx-1`
2. Verify the container is running: `docker ps`
3. Try rebuilding: `docker-compose up --build -d`
4. Check this guide's troubleshooting section above
