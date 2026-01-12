# Production Deployment Checklist

## Pre-Deployment

### Security Configuration

- [ ] **Change SECRET_KEY**
  - Generate new 50+ character random key
  - Never commit to version control
  - Store in environment variables or secrets manager

- [ ] **Change JWT_SIGNING_KEY**
  - Generate new signing key
  - Consider using RS256 with public/private key pairs
  - Store private key securely

- [ ] **Set DEBUG=False**
  - Disables debug mode
  - Hides sensitive error information

- [ ] **Configure ALLOWED_HOSTS**
  - Add your domain names
  - Example: `api.yourdomain.com,yourdomain.com`

- [ ] **Review CORS Settings**
  - Update `CORS_ALLOWED_ORIGINS` with production domains
  - Remove localhost/development URLs

### Database Configuration

- [ ] **Production Database**
  - Set up PostgreSQL instance
  - Configure connection pooling
  - Enable SSL/TLS connections
  - Set up automated backups

- [ ] **Database Credentials**
  - Use strong passwords
  - Rotate credentials regularly
  - Store in secrets manager

- [ ] **Run Migrations**
  ```bash
  python manage.py migrate
  ```

- [ ] **Create Superuser**
  ```bash
  python manage.py createsuperuser
  ```

### Static Files

- [ ] **Collect Static Files**
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] **Configure Static File Serving**
  - WhiteNoise is already configured
  - Or use CDN for static files

### Application Server

- [ ] **Install Gunicorn**
  - Already in requirements.txt

- [ ] **Configure Gunicorn**
  ```bash
  gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
  ```

- [ ] **Workers Calculation**
  - Recommended: `(2 x num_cores) + 1`
  - Monitor and adjust based on load

### Reverse Proxy

- [ ] **Configure Nginx**
  ```nginx
  server {
      listen 80;
      server_name api.yourdomain.com;
      
      location / {
          proxy_pass http://127.0.0.1:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
      
      location /static/ {
          alias /path/to/staticfiles/;
      }
  }
  ```

- [ ] **HTTPS/TLS**
  - Obtain SSL certificate (Let's Encrypt)
  - Configure HTTPS in Nginx
  - Redirect HTTP to HTTPS

### Environment Variables

- [ ] **Production .env File**
  ```bash
  SECRET_KEY=<your-production-secret>
  JWT_SIGNING_KEY=<your-jwt-key>
  DEBUG=False
  ALLOWED_HOSTS=api.yourdomain.com
  
  DB_NAME=production_db
  DB_USER=prod_user
  DB_PASSWORD=<secure-password>
  DB_HOST=db.yourdomain.com
  DB_PORT=5432
  
  JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
  JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
  
  CORS_ALLOWED_ORIGINS=https://yourdomain.com
  ```

- [ ] **Secrets Management**
  - Use AWS Secrets Manager, Azure Key Vault, or similar
  - Never commit secrets to git

## Deployment

### Docker Deployment (Optional)

- [ ] **Create Dockerfile**
  ```dockerfile
  FROM python:3.11-slim
  
  WORKDIR /app
  
  # Install dependencies
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  
  # Copy application
  COPY . .
  
  # Collect static files
  RUN python manage.py collectstatic --noinput
  
  # Expose port
  EXPOSE 8000
  
  # Run gunicorn
  CMD ["gunicorn", "config.wsgi:application", \
       "--bind", "0.0.0.0:8000", \
       "--workers", "4"]
  ```

- [ ] **Create docker-compose.yml**
  ```yaml
  version: '3.8'
  
  services:
    db:
      image: postgres:15
      environment:
        POSTGRES_DB: real_solutions
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: ${DB_PASSWORD}
      volumes:
        - postgres_data:/var/lib/postgresql/data
    
    api:
      build: .
      command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
      volumes:
        - .:/app
      ports:
        - "8000:8000"
      env_file:
        - .env
      depends_on:
        - db
  
  volumes:
    postgres_data:
  ```

### Cloud Deployment

#### AWS

- [ ] **EC2 Instance**
  - Launch Ubuntu instance
  - Configure security groups (port 80, 443)
  - Install dependencies

- [ ] **RDS PostgreSQL**
  - Create RDS instance
  - Configure security groups
  - Enable automated backups

- [ ] **Elastic Load Balancer**
  - Configure for high availability
  - Set up health checks

- [ ] **CloudWatch**
  - Configure logging
  - Set up alarms

#### Heroku

- [ ] **Create Heroku App**
  ```bash
  heroku create your-app-name
  ```

- [ ] **Add PostgreSQL**
  ```bash
  heroku addons:create heroku-postgresql:hobby-dev
  ```

- [ ] **Set Environment Variables**
  ```bash
  heroku config:set SECRET_KEY=your-secret-key
  heroku config:set DEBUG=False
  ```

- [ ] **Deploy**
  ```bash
  git push heroku main
  heroku run python manage.py migrate
  ```

#### DigitalOcean

- [ ] **Create Droplet**
  - Ubuntu 22.04
  - 2GB RAM minimum

- [ ] **Managed PostgreSQL**
  - Create database cluster
  - Configure firewall rules

- [ ] **Deploy Application**
  - Clone repository
  - Install dependencies
  - Configure systemd service

## Post-Deployment

### Monitoring

- [ ] **Application Monitoring**
  - Set up Sentry for error tracking
  - Configure New Relic or DataDog

- [ ] **Log Aggregation**
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - CloudWatch Logs
  - Papertrail

- [ ] **Health Check Endpoint**
  - Create `/health/` endpoint
  - Monitor from external service

- [ ] **Uptime Monitoring**
  - UptimeRobot
  - Pingdom
  - StatusCake

### Performance

- [ ] **Database Indexing**
  - Already configured on tenant fields
  - Add custom indexes as needed

- [ ] **Query Optimization**
  - Use Django Debug Toolbar in staging
  - Identify slow queries
  - Add `select_related()` and `prefetch_related()`

- [ ] **Caching**
  - Set up Redis
  - Cache frequently accessed data
  - Configure session storage in Redis

- [ ] **CDN**
  - CloudFlare
  - AWS CloudFront
  - For static files and API caching

### Security

- [ ] **Firewall Configuration**
  - Allow only necessary ports
  - Whitelist IP addresses
  - Use security groups

- [ ] **Rate Limiting**
  - Already configured in DRF
  - Consider additional WAF rules

- [ ] **SSL/TLS**
  - A+ rating on SSL Labs
  - Strong cipher suites
  - HSTS enabled

- [ ] **Security Headers**
  - Already configured when DEBUG=False
  - X-Frame-Options
  - X-Content-Type-Options
  - Strict-Transport-Security

- [ ] **Regular Updates**
  - Keep Django and dependencies updated
  - Subscribe to security mailing lists
  - Automated dependency scanning (Dependabot)

### Backup & Recovery

- [ ] **Database Backups**
  - Automated daily backups
  - Test restore procedures
  - Off-site backup storage

- [ ] **Application Backups**
  - Version control (Git)
  - Docker images stored in registry

- [ ] **Disaster Recovery Plan**
  - Document recovery procedures
  - Define RTO/RPO
  - Regular disaster recovery drills

### Documentation

- [ ] **API Documentation**
  - OpenAPI/Swagger accessible
  - Keep documentation updated
  - Provide examples

- [ ] **Operational Runbook**
  - Deployment procedures
  - Troubleshooting guide
  - Escalation contacts

- [ ] **Architecture Diagram**
  - Document infrastructure
  - Network topology
  - Data flow diagrams

## Validation

### Functional Testing

- [ ] **Smoke Tests**
  ```bash
  # Test health endpoint
  curl https://api.yourdomain.com/health/
  
  # Test authentication
  curl -X POST https://api.yourdomain.com/api/v1/auth/token/ \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}'
  
  # Test API endpoint
  curl https://api.yourdomain.com/api/v1/projects/ \
    -H "Authorization: Bearer <token>"
  ```

- [ ] **Integration Tests**
  - Run full test suite
  - Test all critical paths
  - Verify tenant isolation

### Performance Testing

- [ ] **Load Testing**
  - Use Apache Bench, Locust, or JMeter
  - Test under expected load
  - Identify bottlenecks

- [ ] **Stress Testing**
  - Test beyond expected load
  - Identify breaking points
  - Verify graceful degradation

### Security Testing

- [ ] **Penetration Testing**
  - OWASP Top 10
  - SQL injection attempts
  - XSS attempts
  - CSRF protection

- [ ] **Tenant Isolation Testing**
  - Verify cross-tenant access blocked
  - Test with multiple tenants
  - Validate JWT token requirements

## Maintenance

### Regular Tasks

- [ ] **Weekly**
  - Review error logs
  - Check disk space
  - Monitor database size

- [ ] **Monthly**
  - Security updates
  - Dependency updates
  - Review access logs

- [ ] **Quarterly**
  - Performance audit
  - Security audit
  - Disaster recovery test

### Scaling Considerations

- [ ] **Horizontal Scaling**
  - Add more application servers
  - Load balancer configuration
  - Session storage in Redis

- [ ] **Database Scaling**
  - Read replicas
  - Connection pooling
  - Consider sharding by tenant

- [ ] **Caching Strategy**
  - Redis for sessions
  - Cache frequently accessed data
  - CDN for static content

## Emergency Procedures

### Rollback Plan

1. Keep previous version available
2. Document rollback steps
3. Test rollback in staging
4. Keep database migrations reversible

### Incident Response

1. **Detection**: Monitoring alerts
2. **Assessment**: Determine severity
3. **Containment**: Stop the issue
4. **Resolution**: Fix the problem
5. **Recovery**: Restore normal operations
6. **Post-Mortem**: Document and learn

## Sign-off

- [ ] **Development Team Lead**: _______________
- [ ] **Operations Team Lead**: _______________
- [ ] **Security Team**: _______________
- [ ] **Product Owner**: _______________

**Deployment Date**: _______________  
**Deployed By**: _______________  
**Version**: _______________

---

## Additional Resources

- Django Deployment Checklist: https://docs.djangoproject.com/en/stable/howto/deployment/checklist/
- Django Production Settings: https://docs.djangoproject.com/en/stable/ref/settings/
- Gunicorn Deployment: https://docs.gunicorn.org/en/stable/deploy.html
- PostgreSQL Best Practices: https://wiki.postgresql.org/wiki/Performance_Optimization

---

**Remember**: This is a living document. Update it based on your specific requirements and lessons learned from deployments.
