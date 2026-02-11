# Deployment Guide

Complete guide for deploying the AI Research Assistant to production.

## Local Development

### Quick Start
```bash
./QUICKSTART.sh
```

### Manual Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Edit .env with your settings

python3 main.py index
python3 main.py chat
```

## Docker Deployment

### Single Container
```bash
# Build image
docker build -t research-assistant:latest .

# Run container
docker run -it \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e ENDEE_BASE_URL=http://endee:8080/api/v1 \
  -e LLM_API_KEY=your_key_here \
  research-assistant:latest \
  chat
```

### Docker Compose (Recommended)
```bash
# Start all services (Endee + Application)
docker-compose up -d

# View logs
docker-compose logs -f research-assistant

# Stop services
docker-compose down
```

## Cloud Deployment

### AWS ECS/Fargate

1. **Push Docker image to ECR**
```bash
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

docker tag research-assistant:latest \
  <account>.dkr.ecr.us-east-1.amazonaws.com/research-assistant:latest

docker push <account>.dkr.ecr.us-east-1.amazonaws.com/research-assistant:latest
```

2. **Create ECS Task Definition**
```json
{
  "family": "research-assistant",
  "containerDefinitions": [
    {
      "name": "research-assistant",
      "image": "<account>.dkr.ecr.us-east-1.amazonaws.com/research-assistant:latest",
      "environment": [
        {
          "name": "ENDEE_BASE_URL",
          "value": "http://endee-service:8080/api/v1"
        },
        {
          "name": "LLM_PROVIDER",
          "value": "openai"
        }
      ],
      "secrets": [
        {
          "name": "LLM_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<account>:secret:llm-key"
        }
      ]
    }
  ]
}
```

3. **Run on Fargate**
```bash
aws ecs run-task \
  --cluster research-cluster \
  --task-definition research-assistant \
  --launch-type FARGATE
```

### Google Cloud Run

```bash
# Build and push
docker build -t gcr.io/PROJECT_ID/research-assistant .
docker push gcr.io/PROJECT_ID/research-assistant

# Deploy
gcloud run deploy research-assistant \
  --image gcr.io/PROJECT_ID/research-assistant \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --set-env-vars "ENDEE_BASE_URL=http://endee:8080/api/v1"
```

### Azure Container Instances

```bash
az container create \
  --resource-group mygroup \
  --name research-assistant \
  --image research-assistant:latest \
  --cpu 2 --memory 2 \
  --environment-variables \
    ENDEE_BASE_URL=http://endee:8080/api/v1 \
  --secure-environment-variables \
    LLM_API_KEY=$LLM_API_KEY
```

## Kubernetes Deployment

### Create Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: research-assistant
spec:
  replicas: 3
  selector:
    matchLabels:
      app: research-assistant
  template:
    metadata:
      labels:
        app: research-assistant
    spec:
      containers:
      - name: research-assistant
        image: research-assistant:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENDEE_BASE_URL
          value: "http://endee-service:8080/api/v1"
        - name: LLM_PROVIDER
          value: "openai"
        envFrom:
        - secretRef:
            name: llm-credentials
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "from config import load_config; load_config()"
          initialDelaySeconds: 10
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: research-assistant
spec:
  selector:
    app: research-assistant
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Create secrets
kubectl create secret generic llm-credentials \
  --from-literal=LLM_API_KEY=your_key

# Apply deployment
kubectl apply -f deployment.yaml

# Check status
kubectl get pods
kubectl logs deployment/research-assistant
```

## Production Configuration

### Environment Variables

```env
# Endee Configuration
ENDEE_BASE_URL=http://endee-prod:8080/api/v1
ENDEE_TOKEN=production_token

# Embedding
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
EMBEDDING_DEVICE=cuda
EMBEDDING_BATCH_SIZE=64

# LLM
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
LLM_API_KEY=${SECRET_KEY}

# Performance
TOP_K=10
SIMILARITY_THRESHOLD=0.5
CHUNK_SIZE=1000

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

### Monitoring and Logging

1. **Application Logging**
```bash
# Centralized logging with ELK Stack or CloudWatch
docker-compose up -d logstash elasticsearch kibana
```

2. **Performance Monitoring**
```python
# Add metrics to main.py
from prometheus_client import Counter, Histogram

queries = Counter('queries_total', 'Total queries')
latency = Histogram('query_latency_seconds', 'Query latency')

@queries.count_exceptions()
@latency.time()
def answer_question(question):
    # Your code
```

3. **Health Checks**
```bash
# Endpoint for health checks
curl http://localhost:5000/health
```

### Security Considerations

1. **API Keys**
   - Use secrets management (AWS Secrets, HashiCorp Vault)
   - Never commit keys to repository
   - Rotate keys regularly

2. **Database**
   - Enable authentication on Endee
   - Use password protection
   - Encrypt data in transit (TLS)

3. **Application**
   - Run as non-root user in containers
   - Use network policies
   - Implement rate limiting

4. **Data Privacy**
   - Implement access control
   - Log data handling
   - Comply with regulations (GDPR, CCPA)

## Scaling Strategies

### Horizontal Scaling

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: research-assistant-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: research-assistant
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Vertical Scaling

Increase memory and CPU for single instance:
```bash
# Kubernetes
kubectl set resources deployment research-assistant \
  --limits=cpu=4,memory=8Gi \
  --requests=cpu=2,memory=4Gi
```

### Caching Layer

Add Redis for embedding cache:
```python
import redis

r = redis.Redis(host='localhost', port=6379)

# Cache embeddings
embedding_key = f"embedding:{hash(text)}"
cached = r.get(embedding_key)
```

## Backup and Recovery

### Document Backup

```bash
# Backup data directory
tar czf backup-$(date +%Y%m%d).tar.gz data/

# Backup Endee index
# Use Endee's built-in backup mechanism
curl -X POST http://localhost:8080/api/v1/backup
```

### Database Recovery

```bash
# Restore from backup
tar xzf backup-20260211.tar.gz

# Re-index if necessary
python3 main.py clear
python3 main.py index
```

## Performance Tuning

### Embedding Optimization

```env
# For maximum speed (accuracy trade-off)
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cuda
EMBEDDING_BATCH_SIZE=128

# For maximum accuracy
EMBEDDING_MODEL=sentence-transformers/all-roberta-large-v1
EMBEDDING_DEVICE=cuda
EMBEDDING_BATCH_SIZE=32
```

### Query Optimization

```env
# For speed
TOP_K=3
SIMILARITY_THRESHOLD=0.6
CHUNK_SIZE=500

# For accuracy
TOP_K=20
SIMILARITY_THRESHOLD=0.3
CHUNK_SIZE=1000
```

## Troubleshooting Production Issues

### Check Service Health

```bash
# Check logs
docker-compose logs research-assistant

# Check Endee connection
curl http://localhost:8080/api/v1/indexes

# Check resource usage
docker stats research-assistant
```

### Common Issues

**Memory Issues:**
```bash
# Reduce batch size
EMBEDDING_BATCH_SIZE=16
```

**Slow Queries:**
```bash
# Increase TOP_K for better caching
# Profile with Python profiler
python3 -m cProfile main.py query "test"
```

**Connection Failures:**
```bash
# Check network connectivity
telnet endee-server 8080
# Verify ENDEE_BASE_URL setting
```

## Release Management

### Version Bumping

```bash
# Semantic versioning
git tag -a v1.1.0 -m "Release 1.1.0"
git push origin v1.1.0
```

### Rolling Updates

```bash
# Kubernetes rolling update
kubectl set image deployment/research-assistant \
  research-assistant=research-assistant:v1.1.0 \
  --record

# Check rollout status
kubectl rollout status deployment/research-assistant

# Rollback if needed
kubectl rollout undo deployment/research-assistant
```

## Maintenance Checklist

- [ ] Daily: Check logs for errors
- [ ] Weekly: Verify backups
- [ ] Weekly: Update dependencies
- [ ] Monthly: Performance review
- [ ] Monthly: Security audit
- [ ] Quarterly: Disaster recovery test
- [ ] Annually: Architecture review

---

For questions, see README.md or open an issue on GitHub.
