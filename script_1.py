# Create deployment configuration files
deployment_configs = {
    "docker-compose.production.yml": """version: '3.8'

services:
  # MongoDB with replica set for production
  mongodb:
    image: mongo:7
    container_name: designstudio-mongodb
    restart: unless-stopped
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_ROOT_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: designstudio
      MONGO_REPLICA_SET_NAME: rs0
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
      - ./docker/mongodb/mongod.conf:/etc/mongod.conf
      - ./docker/mongodb/init-replica.js:/docker-entrypoint-initdb.d/init-replica.js
    command: ["--replSet", "rs0", "--bind_ip_all", "--keyFile", "/etc/mongodb-keyfile"]
    networks:
      - designstudio-network

  # Redis Cluster for high availability
  redis-master:
    image: redis:7-alpine
    container_name: designstudio-redis-master
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_master_data:/data
      - ./docker/redis/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    networks:
      - designstudio-network

  redis-slave:
    image: redis:7-alpine
    container_name: designstudio-redis-slave
    restart: unless-stopped
    ports:
      - "6380:6379"
    volumes:
      - redis_slave_data:/data
    command: redis-server --slaveof redis-master 6379
    depends_on:
      - redis-master
    networks:
      - designstudio-network

  # Backend API instances (load balanced)
  backend-1:
    build:
      context: ./packages/backend
      dockerfile: Dockerfile.production
    container_name: designstudio-backend-1
    restart: unless-stopped
    environment:
      NODE_ENV: production
      PORT: 3000
      INSTANCE_ID: backend-1
      DATABASE_URL: ${DATABASE_URL}
      REDIS_MASTER_URL: redis://redis-master:6379
      REDIS_SLAVE_URL: redis://redis-slave:6379
      JWT_SECRET: ${JWT_SECRET}
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_SERVICE_ROLE_KEY: ${SUPABASE_SERVICE_ROLE_KEY}
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      AWS_S3_BUCKET: ${AWS_S3_BUCKET}
      AWS_REGION: ${AWS_REGION}
    depends_on:
      - mongodb
      - redis-master
    networks:
      - designstudio-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend-2:
    build:
      context: ./packages/backend
      dockerfile: Dockerfile.production
    container_name: designstudio-backend-2
    restart: unless-stopped
    environment:
      NODE_ENV: production
      PORT: 3000
      INSTANCE_ID: backend-2
      DATABASE_URL: ${DATABASE_URL}
      REDIS_MASTER_URL: redis://redis-master:6379
      REDIS_SLAVE_URL: redis://redis-slave:6379
      JWT_SECRET: ${JWT_SECRET}
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_SERVICE_ROLE_KEY: ${SUPABASE_SERVICE_ROLE_KEY}
      AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
      AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
      AWS_S3_BUCKET: ${AWS_S3_BUCKET}
      AWS_REGION: ${AWS_REGION}
    depends_on:
      - mongodb
      - redis-master
    networks:
      - designstudio-network

  # Web PWA
  web:
    build:
      context: ./packages/web
      dockerfile: Dockerfile.production
    container_name: designstudio-web
    restart: unless-stopped
    environment:
      VITE_API_URL: https://api.designstudio.com
      VITE_WS_URL: wss://api.designstudio.com
      VITE_SUPABASE_URL: ${SUPABASE_URL}
      VITE_SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY}
    networks:
      - designstudio-network

  # Nginx Load Balancer
  nginx:
    image: nginx:alpine
    container_name: designstudio-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.prod.conf:/etc/nginx/nginx.conf
      - ./docker/nginx/ssl:/etc/nginx/ssl
      - ./docker/nginx/logs:/var/log/nginx
    depends_on:
      - backend-1
      - backend-2
      - web
    networks:
      - designstudio-network

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    container_name: designstudio-prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - designstudio-network

  grafana:
    image: grafana/grafana:latest
    container_name: designstudio-grafana
    restart: unless-stopped
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./docker/grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - designstudio-network

  # Log aggregation
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: designstudio-elasticsearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - designstudio-network

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: designstudio-logstash
    restart: unless-stopped
    volumes:
      - ./docker/logstash/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch
    networks:
      - designstudio-network

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: designstudio-kibana
    restart: unless-stopped
    ports:
      - "5601:5601"
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    depends_on:
      - elasticsearch
    networks:
      - designstudio-network

volumes:
  mongodb_data:
  redis_master_data:
  redis_slave_data:
  prometheus_data:
  grafana_data:
  elasticsearch_data:

networks:
  designstudio-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
""",

    "docker/nginx/nginx.prod.conf": """user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                   '$status $body_bytes_sent "$http_referer" '
                   '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # Performance settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=websocket:10m rate=5r/s;

    # Upstream backend servers
    upstream backend {
        least_conn;
        server backend-1:3000 max_fails=3 fail_timeout=30s;
        server backend-2:3000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: ws:;" always;

    # Main server block
    server {
        listen 80;
        listen [::]:80;
        server_name designstudio.com www.designstudio.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name designstudio.com www.designstudio.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # WebSocket connections
        location /socket.io/ {
            limit_req zone=websocket burst=10 nodelay;
            
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400s;
            proxy_send_timeout 86400s;
        }

        # Static files with caching
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            add_header Vary Accept-Encoding;
            
            proxy_pass http://web:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # PWA routes
        location / {
            proxy_pass http://web:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # PWA support
            location ~* \\.(html|json|js)$ {
                add_header Cache-Control "no-cache, no-store, must-revalidate";
                add_header Pragma "no-cache";
                add_header Expires "0";
            }
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
    }
}""",

    "kubernetes/namespace.yaml": """apiVersion: v1
kind: Namespace
metadata:
  name: designstudio
  labels:
    name: designstudio
    environment: production
""",

    "kubernetes/mongodb-deployment.yaml": """apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongodb
  namespace: designstudio
spec:
  serviceName: mongodb-service
  replicas: 3
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:7
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: username
        - name: MONGO_INITDB_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mongodb-secret
              key: password
        volumeMounts:
        - name: mongodb-persistent-storage
          mountPath: /data/db
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: mongodb-persistent-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
      storageClassName: ssd

---
apiVersion: v1
kind: Service
metadata:
  name: mongodb-service
  namespace: designstudio
spec:
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017
  clusterIP: None
""",

    "kubernetes/backend-deployment.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: designstudio
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: designstudio/backend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: redis-url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: jwt-secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: designstudio
spec:
  selector:
    app: backend
  ports:
  - port: 3000
    targetPort: 3000
  type: ClusterIP
""",

    "terraform/main.tf": """terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    bucket = "designstudio-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC and Networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "designstudio-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false
  enable_dns_hostnames = true
  enable_dns_support = true

  tags = {
    Environment = "production"
    Project     = "designstudio"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name    = "designstudio-cluster"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  node_groups = {
    main = {
      desired_capacity = 3
      max_capacity     = 10
      min_capacity     = 1

      instance_types = ["t3.medium"]

      k8s_labels = {
        Environment = "production"
        Application = "designstudio"
      }
    }
  }

  tags = {
    Environment = "production"
    Project     = "designstudio"
  }
}

# RDS MongoDB DocumentDB
resource "aws_docdb_cluster" "main" {
  cluster_identifier      = "designstudio-docdb"
  engine                  = "docdb"
  master_username         = var.docdb_username
  master_password         = var.docdb_password
  backup_retention_period = 7
  preferred_backup_window = "07:00-09:00"
  skip_final_snapshot     = false
  
  vpc_security_group_ids = [aws_security_group.docdb.id]
  db_subnet_group_name   = aws_docdb_subnet_group.main.name

  tags = {
    Environment = "production"
    Project     = "designstudio"
  }
}

resource "aws_docdb_cluster_instance" "cluster_instances" {
  count              = 3
  identifier         = "designstudio-docdb-${count.index}"
  cluster_identifier = aws_docdb_cluster.main.id
  instance_class     = "db.t3.medium"
}

# ElastiCache Redis
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "designstudio-redis"
  description                = "Redis cluster for DesignStudio"
  
  node_type                  = "cache.t3.micro"
  port                       = 6379
  parameter_group_name       = "default.redis7"
  
  num_cache_clusters         = 3
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]

  tags = {
    Environment = "production"
    Project     = "designstudio"
  }
}

# S3 Bucket for assets
resource "aws_s3_bucket" "assets" {
  bucket = "designstudio-assets-${random_id.bucket_suffix.hex}"

  tags = {
    Environment = "production"
    Project     = "designstudio"
  }
}

resource "aws_s3_bucket_cors_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "POST", "PUT", "DELETE"]
    allowed_origins = ["https://designstudio.com", "https://app.designstudio.com"]
    max_age_seconds = 3000
  }
}

# CloudFront CDN
resource "aws_cloudfront_distribution" "main" {
  origin {
    domain_name = aws_s3_bucket.assets.bucket_regional_domain_name
    origin_id   = "S3-${aws_s3_bucket.assets.bucket}"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.main.cloudfront_access_identity_path
    }
  }

  enabled = true
  comment = "DesignStudio CDN"

  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-${aws_s3_bucket.assets.bucket}"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Environment = "production"
    Project     = "designstudio"
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "docdb_username" {
  description = "DocumentDB master username"
  type        = string
  sensitive   = true
}

variable "docdb_password" {
  description = "DocumentDB master password"
  type        = string
  sensitive   = true
}

# Random ID for unique resource naming
resource "random_id" "bucket_suffix" {
  byte_length = 4
}""",

    ".env.production.example": """# Production Environment Variables

# Database
DATABASE_URL="mongodb://username:password@docdb-cluster.region.docdb.amazonaws.com:27017/designstudio?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"

# Redis Cache
REDIS_URL="redis://designstudio-redis.cache.amazonaws.com:6379"

# Authentication
JWT_SECRET="your-super-secure-jwt-secret-key"
JWT_EXPIRES_IN="7d"
REFRESH_TOKEN_EXPIRES_IN="30d"

# Supabase
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_ANON_KEY="your-supabase-anon-key"
SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"

# AWS Services
AWS_ACCESS_KEY_ID="your-aws-access-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
AWS_REGION="us-east-1"
AWS_S3_BUCKET="designstudio-assets-prod"
AWS_CLOUDFRONT_DOMAIN="d123456789.cloudfront.net"

# File Upload
MAX_FILE_SIZE="50MB"
ALLOWED_FILE_TYPES="image/jpeg,image/png,image/svg+xml,image/webp"

# Email Service (SendGrid/SES)
EMAIL_FROM="noreply@designstudio.com"
EMAIL_API_KEY="your-email-service-api-key"

# WebSocket
WEBSOCKET_PORT=3001
WEBSOCKET_PATH="/socket.io"

# CORS
CORS_ORIGIN="https://designstudio.com,https://app.designstudio.com"

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# Monitoring
SENTRY_DSN="your-sentry-dsn"
LOG_LEVEL="info"

# SSL/Security
SSL_CERT_PATH="/etc/ssl/certs/fullchain.pem"
SSL_KEY_PATH="/etc/ssl/private/privkey.pem"

# Performance
NODE_ENV="production"
PORT=3000
CLUSTER_WORKERS=4

# Feature Flags
ENABLE_VOICE_CHAT=true
ENABLE_VIDEO_CHAT=true
ENABLE_AI_FEATURES=false
ENABLE_ANALYTICS=true

# Third-party Integrations
FIGMA_CLIENT_ID="your-figma-client-id"
FIGMA_CLIENT_SECRET="your-figma-client-secret"
GOOGLE_CLIENT_ID="your-google-oauth-client-id"
GOOGLE_CLIENT_SECRET="your-google-oauth-client-secret"

# CDN and Asset Management
CDN_URL="https://cdn.designstudio.com"
ASSET_COMPRESSION_QUALITY=85
ENABLE_WEBP_CONVERSION=true

# Backup and Disaster Recovery
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30
BACKUP_S3_BUCKET="designstudio-backups-prod"

# Compliance and Security
GDPR_COMPLIANCE=true
DATA_RETENTION_DAYS=2555
ENCRYPTION_AT_REST=true
AUDIT_LOGGING=true"""
}

# Save all deployment configuration files
import os
import json

# Create deployment_configs.json
with open('deployment_configs.json', 'w') as f:
    json.dump(deployment_configs, f, indent=2)

print("✅ Created comprehensive deployment configuration files:")
for filename in deployment_configs.keys():
    print(f"  📁 {filename}")

print("\n🚀 Deployment configurations include:")
print("  • Docker Compose for production with full monitoring stack")
print("  • Nginx configuration with SSL, load balancing, and security")
print("  • Kubernetes manifests for container orchestration")
print("  • Terraform infrastructure as code for AWS")
print("  • Environment variables template for production")