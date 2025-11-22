# Deployment Guide

## Overview

This guide covers deploying the ClickBank Affiliate SaaS to production using AWS ECS (Elastic Container Service).

## Architecture

```
Internet
    │
    ▼
CloudFront (CDN)
    │
    ▼
Application Load Balancer (ALB)
    │
    ├─> Frontend (ECS Service)
    ├─> Backend (ECS Service)
    ├─> Celery Workers (ECS Service)
    └─> Celery Beat (ECS Service)
    │
    ├─> RDS PostgreSQL
    ├─> ElastiCache Redis
    └─> S3 (Static Assets)
```

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Docker installed locally
- Domain name (for SSL certificate)

## AWS Resources Required

1. **VPC** - Virtual Private Cloud
2. **RDS** - PostgreSQL database
3. **ElastiCache** - Redis cluster
4. **ECS** - Container orchestration
5. **ECR** - Docker image registry
6. **ALB** - Application Load Balancer
7. **S3** - Static file storage
8. **CloudFront** - CDN
9. **Route53** - DNS management
10. **ACM** - SSL certificates
11. **Secrets Manager** - Secure credentials
12. **CloudWatch** - Logging and monitoring

## Step-by-Step Deployment

### 1. Set Up Infrastructure (Terraform)

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file=environments/production/terraform.tfvars

# Apply changes
terraform apply -var-file=environments/production/terraform.tfvars
```

### 2. Configure Secrets

Store sensitive data in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
    --name clickbank-saas/production \
    --secret-string '{
      "DATABASE_URL": "postgresql://...",
      "JWT_SECRET_KEY": "...",
      "ANTHROPIC_API_KEY": "...",
      "STRIPE_SECRET_KEY": "..."
    }'
```

### 3. Build and Push Docker Images

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build backend image
cd backend
docker build -t clickbank-saas-backend:latest .
docker tag clickbank-saas-backend:latest \
    <account-id>.dkr.ecr.us-east-1.amazonaws.com/clickbank-saas-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/clickbank-saas-backend:latest

# Build frontend image
cd ../frontend
docker build -t clickbank-saas-frontend:latest .
docker tag clickbank-saas-frontend:latest \
    <account-id>.dkr.ecr.us-east-1.amazonaws.com/clickbank-saas-frontend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/clickbank-saas-frontend:latest
```

### 4. Run Database Migrations

```bash
# Connect to ECS task and run migrations
aws ecs run-task \
    --cluster clickbank-saas-production \
    --task-definition clickbank-backend-migration \
    --launch-type FARGATE

# Or use ECS Exec
aws ecs execute-command \
    --cluster clickbank-saas-production \
    --task <task-id> \
    --container backend \
    --command "alembic upgrade head" \
    --interactive
```

### 5. Deploy ECS Services

```bash
# Update backend service
aws ecs update-service \
    --cluster clickbank-saas-production \
    --service backend \
    --force-new-deployment

# Update frontend service
aws ecs update-service \
    --cluster clickbank-saas-production \
    --service frontend \
    --force-new-deployment

# Update Celery workers
aws ecs update-service \
    --cluster clickbank-saas-production \
    --service celery-worker \
    --force-new-deployment
```

### 6. Configure DNS

Point your domain to the ALB:

```bash
# Get ALB DNS name
aws elbv2 describe-load-balancers \
    --names clickbank-saas-alb \
    --query 'LoadBalancers[0].DNSName'

# Create Route53 record
aws route53 change-resource-record-sets \
    --hosted-zone-id <zone-id> \
    --change-batch file://dns-change.json
```

### 7. Verify Deployment

```bash
# Check service status
aws ecs describe-services \
    --cluster clickbank-saas-production \
    --services backend frontend celery-worker

# View logs
aws logs tail /ecs/clickbank-saas-backend --follow
```

## Environment-Specific Configuration

### Staging Environment

```bash
# Use staging tfvars
terraform apply -var-file=environments/staging/terraform.tfvars

# Smaller instance sizes
# Auto-scaling: 1-3 tasks
# No multi-AZ deployment
```

### Production Environment

```bash
# Use production tfvars
terraform apply -var-file=environments/production/terraform.tfvars

# Larger instance sizes
# Auto-scaling: 2-10 tasks
# Multi-AZ deployment
# Automated backups
```

## Auto-Scaling Configuration

```json
{
  "ServiceName": "backend",
  "ScalableTargetAction": {
    "MinCapacity": 2,
    "MaxCapacity": 10
  },
  "TargetTrackingScalingPolicy": {
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    }
  }
}
```

## Monitoring Setup

### CloudWatch Alarms

```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
    --alarm-name backend-high-error-rate \
    --alarm-description "Alert when error rate > 1%" \
    --metric-name 5XXError \
    --namespace AWS/ApplicationELB \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 1 \
    --comparison-operator GreaterThanThreshold

# High CPU alarm
aws cloudwatch put-metric-alarm \
    --alarm-name backend-high-cpu \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold
```

### Sentry Integration

Add to environment variables:
```bash
SENTRY_DSN=https://...@sentry.io/...
SENTRY_ENVIRONMENT=production
```

## Backup and Recovery

### Database Backups

RDS automated backups:
- Daily snapshots
- 30-day retention
- Point-in-time recovery

```bash
# Manual snapshot
aws rds create-db-snapshot \
    --db-instance-identifier clickbank-saas-prod \
    --db-snapshot-identifier manual-backup-$(date +%Y%m%d)

# Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier clickbank-saas-restored \
    --db-snapshot-identifier manual-backup-20250101
```

### Application Data Backup

```bash
# Backup S3 content
aws s3 sync s3://clickbank-saas-uploads s3://clickbank-saas-backups/$(date +%Y%m%d)/
```

## Rollback Procedure

### Quick Rollback

```bash
# Rollback to previous task definition
aws ecs update-service \
    --cluster clickbank-saas-production \
    --service backend \
    --task-definition clickbank-backend:123  # previous revision

# Or use blue-green deployment
aws ecs update-service \
    --cluster clickbank-saas-production \
    --service backend \
    --deployment-configuration "deploymentCircuitBreaker={enable=true,rollback=true}"
```

## SSL/TLS Configuration

### Request Certificate

```bash
aws acm request-certificate \
    --domain-name yourapp.com \
    --subject-alternative-names *.yourapp.com \
    --validation-method DNS
```

### Configure ALB

```bash
# Add HTTPS listener
aws elbv2 create-listener \
    --load-balancer-arn <alb-arn> \
    --protocol HTTPS \
    --port 443 \
    --certificates CertificateArn=<cert-arn> \
    --default-actions Type=forward,TargetGroupArn=<tg-arn>
```

## Performance Optimization

### CDN Configuration

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
    --origin-domain-name <alb-dns> \
    --default-cache-behavior \
    "TargetOriginId=ALB,ViewerProtocolPolicy=redirect-to-https"
```

### Database Connection Pooling

```python
# In backend configuration
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 10
SQLALCHEMY_POOL_TIMEOUT = 30
```

## Cost Optimization

### Resource Sizing

**Production:**
- Backend: 2-10 tasks (1 vCPU, 2GB RAM each)
- Frontend: 2-5 tasks (0.5 vCPU, 1GB RAM each)
- Celery: 2-5 workers (1 vCPU, 2GB RAM each)
- RDS: db.t3.medium (2 vCPU, 4GB RAM)
- ElastiCache: cache.t3.small (2 vCPU, 1.37GB RAM)

**Estimated Monthly Cost:** $400-800

### Cost Reduction Tips

1. Use Spot Instances for Celery workers
2. Schedule auto-scaling (lower at night)
3. Use S3 Intelligent-Tiering
4. Enable RDS backtrack instead of read replicas for dev
5. Use CloudFront for static assets

## Security Checklist

- [ ] All secrets in AWS Secrets Manager
- [ ] SSL/TLS enabled (HTTPS only)
- [ ] Security groups properly configured
- [ ] WAF rules enabled
- [ ] Database encryption at rest
- [ ] VPC with private subnets
- [ ] IAM roles with least privilege
- [ ] CloudWatch logging enabled
- [ ] Automated security patches

## Post-Deployment Verification

```bash
# Health check
curl https://yourapp.com/health

# API test
curl https://yourapp.com/api/v1/products/search

# Load test
ab -n 1000 -c 10 https://yourapp.com/api/v1/analytics/dashboard
```

## Maintenance

### Updates

```bash
# Update dependencies
cd backend && pip install --upgrade -r requirements.txt
cd frontend && npm update

# Build and deploy new images
./scripts/deploy.sh production
```

### Database Maintenance

```bash
# Vacuum and analyze
psql $DATABASE_URL -c "VACUUM ANALYZE;"

# Reindex
psql $DATABASE_URL -c "REINDEX DATABASE clickbank_saas;"
```

## Troubleshooting

### Service Won't Start

```bash
# Check task logs
aws logs tail /ecs/clickbank-saas-backend --follow

# Describe task
aws ecs describe-tasks \
    --cluster clickbank-saas-production \
    --tasks <task-id>
```

### High Memory Usage

```bash
# Check metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/ECS \
    --metric-name MemoryUtilization \
    --dimensions Name=ServiceName,Value=backend
```

### Database Connection Issues

```bash
# Check RDS status
aws rds describe-db-instances \
    --db-instance-identifier clickbank-saas-prod

# Test connection from ECS
aws ecs execute-command \
    --cluster clickbank-saas-production \
    --task <task-id> \
    --command "psql $DATABASE_URL -c 'SELECT 1;'"
```

---

For automated deployments, use the GitHub Actions workflow in `.github/workflows/deploy-production.yml`.
