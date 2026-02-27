---
name: docker-ram-checker
description: Check Docker container RAM/memory usage before deploying to cloud services like Cloud Run, ECS, or Kubernetes. Use this skill when users want to test memory consumption of their Docker containers, verify applications fit within memory limits, or diagnose memory issues before deployment. Triggers on requests like "check docker memory", "test container RAM usage", "will my app fit in 1GB", or "memory test before deploy".
---

# Docker RAM Checker

Test Docker container memory usage locally before deploying to cloud services.

## Prerequisites

**Docker Desktop must be running.** Verify with:
```bash
docker info > /dev/null 2>&1 && echo "Docker is running" || echo "Start Docker Desktop first"
```

## Workflow

### 1. Build the Docker Image

```bash
docker build -t <app-name>-test:latest .
```

Check image size:
```bash
docker images <app-name>-test --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

### 2. Run Container with Memory Limit

```bash
docker run -d --name <app-name>-test \
  --memory=<limit>g \
  -p <host-port>:<container-port> \
  --env-file .env \
  <app-name>-test:latest
```

Common memory limits: `512m`, `1g`, `2g`, `4g`

### 3. Check Startup Memory

```bash
# Wait for startup
sleep 15

# Check memory usage
docker stats <app-name>-test --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
```

### 4. Test Under Load

Send requests to simulate load, then check memory:

```bash
# Example: send 5 requests
for i in {1..5}; do
  curl -s -X POST http://localhost:<port>/endpoint -H "Content-Type: application/json" -d '{}' > /dev/null
  sleep 1
done

# Check memory after load
docker stats <app-name>-test --no-stream --format "{{.MemUsage}} ({{.MemPerc}})"
```

### 5. Check for Memory Leaks

Send more requests and compare:
```bash
# Before
docker stats <app-name>-test --no-stream --format "{{.MemUsage}}"

# Send 20 more requests
for i in {1..20}; do curl -s <endpoint> > /dev/null; done

# After
docker stats <app-name>-test --no-stream --format "{{.MemUsage}}"

# Wait for GC
sleep 15
docker stats <app-name>-test --no-stream --format "{{.MemUsage}}"
```

If memory keeps growing without returning to baseline, investigate potential leaks.

### 6. Check Disk Usage (Optional)

```bash
docker exec <app-name>-test du -sh /app
docker exec <app-name>-test df -h /
```

### 7. Cleanup

```bash
docker rm -f <app-name>-test
```

## Interpreting Results

| Startup Memory | Assessment |
|----------------|------------|
| < 50% of limit | Safe to deploy |
| 50-70% of limit | Monitor closely |
| > 70% of limit | Consider increasing limit |

### Cloud Run Memory Overhead Warning

**IMPORTANT**: Cloud Run memory usage differs from local Docker tests due to gVisor sandbox runtime.

**Why the difference:**
- Cloud Run uses [gVisor](https://gvisor.dev/) sandbox for isolation
- Memory accounting includes kernel memory and file system cache
- Overhead varies by workload (no fixed multiplier documented)

**Recommendation for Cloud Run:**
1. Test locally to establish baseline
2. Deploy to Cloud Run with generous memory (e.g., 1Gi)
3. Monitor actual usage in [Cloud Console metrics](https://console.cloud.google.com/run)
4. Adjust based on real Cloud Run metrics, not local Docker stats

**How to check Cloud Run memory:**
```bash
# View OOM events
gcloud logging read 'resource.type="cloud_run_revision" AND textPayload=~"Memory"' \
  --project=PROJECT_ID --limit=10

# Or use Cloud Console: Cloud Run > Service > Metrics tab
```

## Common Issues

**Container exits immediately**: Check logs with `docker logs <name>`

**Port already in use**: Use a different host port (e.g., `-p 8081:8080`)

**Env vars not loading**: Verify `.env` file format (no quotes around values)

**OOM killed**: Container exceeded memory limit - increase `--memory` or optimize app
