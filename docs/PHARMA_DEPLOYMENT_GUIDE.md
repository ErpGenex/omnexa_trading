# Pharmaceutical Compliance Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Security Configuration](#security-configuration)
6. [Testing](#testing)
7. [Monitoring](#monitoring)
8. [Backup and Recovery](#backup-and-recovery)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Hardware:**
- CPU: 4 cores minimum (8 cores recommended)
- RAM: 8GB minimum (16GB recommended)
- Storage: 50GB minimum SSD (100GB recommended)

**Software:**
- Operating System: Linux (Ubuntu 20.04+ recommended)
- Python: 3.10+
- Node.js: 18+
- MySQL: 8.0+
- Redis: 6.0+
- Nginx: 1.18+

### Network Requirements

- Port 80 (HTTP)
- Port 443 (HTTPS)
- Port 8000 (Frappe)
- Port 6379 (Redis)
- Port 3306 (MySQL)

### User Permissions

- sudo access for system configuration
- Database administrator access
- Network configuration access

## Installation

### Step 1: Install Frappe Bench

```bash
# Clone Frappe Bench
git clone https://github.com/frappe/bench ~/bench
cd ~/bench

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-dev python3-pip python3-venv git \
    mariadb-server mariadb-client nginx redis-server nodejs npm \
    libpq-dev libxslt-dev python3-dev libldap3-dev libsasl2-dev \
    libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev libfreetype6-dev \
    libwebp-dev libharfbuzz-dev libfribidi-dev libxcb-cursor-dev

# Install Python dependencies
pip3 install --upgrade pip
pip3 install frappe-bench

# Initialize bench
bench init --frappe-branch version-15 ~/frappe-bench
cd ~/frappe-bench
```

### Step 2: Install Omnexa Trading App

```bash
# Get the app
bench get-app omnexa_trading /path/to/omnexa_trading

# Install app dependencies
bench install-app omnexa_trading
```

### Step 3: Create New Site

```bash
# Create site
bench new-site pharma.example.com

# Set site as default
bench use pharma.example.com

# Install ERPNext (required dependency)
bench install-app erpnext
```

### Step 4: Configure Site

```bash
# Set administrator password
bench set-admin-password

# Enable scheduler
bench --site pharma.example.com enable-scheduler

# Configure Redis
bench config redis_socketio_host localhost
bench config redis_cache_host localhost
```

### Step 5: Start Services

```bash
# Start all services
bench start

# Verify services
bench doctor
```

## Configuration

### Step 1: Configure Company

1. Login to Frappe
2. Navigate to **Company** list
3. Create new company:
   - Company Name: Your company name
   - Abbr: Company abbreviation
   - Country: Your country
   - Default Currency: Your currency
4. Save and submit

### Step 2: Configure Warehouses

1. Navigate to **Warehouse** list
2. Create warehouses:
   - Main Warehouse
   - Cold Storage (if needed)
   - Quarantine Area
3. Set company for each warehouse
4. Save and submit

### Step 3: Configure Items

1. Navigate to **Item** list
2. Create pharmaceutical items:
   - Item Code: Unique identifier
   - Item Name: Product name
   - Item Group: Appropriate group
   - Is Stock Item: Yes
3. Set pharmaceutical-specific attributes:
   - Storage requirements
   - Cold chain requirements
   - Controlled substance status
4. Save and submit

### Step 4: Configure Users and Roles

1. Navigate to **User** list
2. Create users:
   - Quality Manager
   - Warehouse Manager
   - Sales Representative
   - System Administrator
3. Assign appropriate roles:
   - Quality Manager: Quality Manager role
   - Warehouse Manager: Warehouse Manager role
   - Sales Representative: Sales User role
   - System Administrator: System Manager role
4. Save users

### Step 5: Configure Field Permissions

1. Navigate to **Field Permission** list
2. Create permissions for sensitive fields:
   - License numbers
   - Prescription numbers
   - Customer information
3. Set appropriate permissions by role:
   - Read: Who can view
   - Write: Who can edit
   - Mask: Who sees masked values
   - Hide: Who cannot see
4. Save permissions

## Database Setup

### Step 1: Create Database Indexes

```sql
-- Batch management indexes
CREATE INDEX idx_pharma_batch_expiry ON `tabPharma Batch`(expiry_date);
CREATE INDEX idx_pharma_batch_quality ON `tabPharma Batch`(quality_status);
CREATE INDEX idx_pharma_batch_item ON `tabPharma Batch`(item_code);
CREATE INDEX idx_pharma_batch_active ON `tabPharma Batch`(is_active);

-- Quality inspection indexes
CREATE INDEX idx_quality_inspection_batch ON `tabPharma Quality Inspection`(batch_number);
CREATE INDEX idx_quality_inspection_status ON `tabPharma Quality Inspection`(inspection_status);
CREATE INDEX idx_quality_inspection_date ON `tabPharma Quality Inspection`(inspection_date);

-- Temperature log indexes
CREATE INDEX idx_temp_log_batch ON `tabTemperature Log`(batch_number);
CREATE INDEX idx_temp_log_date ON `tabTemperature Log`(log_date);
CREATE INDEX idx_temp_log_status ON `tabTemperature Log`(temperature_status);

-- Audit log indexes
CREATE INDEX idx_audit_log_document ON `tabAudit Log`(document_type, document_name);
CREATE INDEX idx_audit_log_user ON `tabAudit Log`(user);
CREATE INDEX idx_audit_log_timestamp ON `tabAudit Log`(timestamp);

-- Regulatory approval indexes
CREATE INDEX idx_reg_approval_batch ON `tabPharma Regulatory Approval`(batch_number);
CREATE INDEX idx_reg_approval_status ON `tabPharma Regulatory Approval`(approval_status);

-- Product recall indexes
CREATE INDEX idx_recall_batch ON `tabPharma Product Recall`(batch_number);
CREATE INDEX idx_recall_status ON `tabPharma Product Recall`(recall_status);
```

### Step 2: Run Database Migrations

```bash
# Run all migrations
bench --site pharma.example.com migrate

# Verify migration status
bench --site pharma.example.com mariadb --execute "SHOW TABLES;"
```

## Security Configuration

### Step 1: Configure SSL/TLS

```bash
# Generate SSL certificate
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/pharma.key \
    -out /etc/ssl/certs/pharma.crt

# Configure Nginx
sudo nano /etc/nginx/sites-available/pharma.example.com
```

Nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name pharma.example.com;

    ssl_certificate /etc/ssl/certs/pharma.crt;
    ssl_certificate_key /etc/ssl/private/pharma.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/pharma.example.com /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 2: Configure Firewall

```bash
# Configure UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Step 3: Configure Encryption Keys

1. Navigate to **Encryption Key** list
2. Create master encryption key:
   - Key Name: MASTER-KEY
   - Key Type: Symmetric
   - Algorithm: Fernet
   - Key Length: 256
3. Save key
4. Store key securely (offline backup recommended)

### Step 4: Configure Redis Authentication

```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Set password
requirepass your_strong_password_here

# Restart Redis
sudo systemctl restart redis-server
```

Update Frappe configuration:
```bash
bench config redis_cache_host "localhost:6379"
bench config redis_cache_password "your_strong_password_here"
```

### Step 5: Configure Database Security

```sql
-- Create dedicated database user
CREATE USER 'pharma_user'@'localhost' IDENTIFIED BY 'strong_password';

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON pharma_example_com.* TO 'pharma_user'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;
```

Update site configuration:
```bash
bench --site pharma.example.com set-mariadb-host localhost
bench --site pharma.example.com set-mariadb-root-password your_db_password
```

## Testing

### Step 1: Run Unit Tests

```bash
# Run all tests
bench --site pharma.example.com run-tests --app omnexa_trading

# Run specific test file
bench --site pharma.example.com run-tests --app omnexa_trading --module omnexa_trading.tests.test_pharma_batch

# Run with coverage
bench --site pharma.example.com run-tests --app omnexa_trading --coverage
```

### Step 2: Run Integration Tests

```bash
# Run integration tests
bench --site pharma.example.com run-tests --app omnexa_trading --module omnexa_trading.tests.test_pharma_integration
```

### Step 3: Run End-to-End Tests

```bash
# Run E2E tests
bench --site pharma.example.com run-tests --app omnexa_trading --module omnexa_trading.tests.test_pharma_e2e
```

### Step 4: Manual Testing Checklist

**Batch Management:**
- [ ] Create new batch
- [ ] Validate batch for sale
- [ ] Quarantine batch
- [ ] Release quarantined batch
- [ ] View batch stock summary
- [ ] View batch movement history

**Expiry Management:**
- [ ] Test expiry blocking in sales
- [ ] Test FEFO picking
- [ ] Test FIFO picking
- [ ] Verify near-expiry alerts
- [ ] Verify expired batch processing

**Quality Control:**
- [ ] Create quality inspection
- [ ] Add quality parameters
- [ ] Add inspection defects
- [ ] Submit inspection
- [ ] Verify batch quality status update
- [ ] Test quality hold/release

**Cold Chain Management:**
- [ ] Create temperature log
- [ ] Test temperature excursion creation
- [ ] Resolve temperature excursion
- [ ] View temperature summary
- [ ] Verify cold chain alerts

**Controlled Substances:**
- [ ] Create regulatory approval
- [ ] Test controlled substance validation
- [ ] Test prescription validation
- [ ] Verify license expiry checking

**Product Recall:**
- [ ] Initiate product recall
- [ ] Add affected customers
- [ ] Notify customers
- [ ] Complete recall
- [ ] Verify batch quarantine

**Audit Trail:**
- [ ] Verify audit log creation
- [ ] View audit trail for document
- [ ] View user activity logs
- [ ] Test field change tracking

**Security:**
- [ ] Test field permissions
- [ ] Test data masking
- [ ] Test data encryption
- [ ] Test data decryption
- [ ] Test key rotation

## Monitoring

### Step 1: Configure System Monitoring

```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Configure log rotation
sudo nano /etc/logrotate.d/frappe
```

Log rotation configuration:
```
/home/frappeuser/frappe-bench/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 frappeuser frappeuser
    sharedscripts
}
```

### Step 2: Configure Application Monitoring

```bash
# Enable Frappe monitoring
bench --site pharma.example.com set-maintenance-mode off

# Monitor scheduler
bench --site pharma.example.com scheduler status

# Monitor background workers
bench doctor
```

### Step 3: Configure Alerting

Create monitoring script:
```bash
nano /home/frappeuser/monitor_pharma.sh
```

```bash
#!/bin/bash
# Pharmaceutical Compliance Monitoring Script

# Check if services are running
if ! systemctl is-active --quiet nginx; then
    echo "Nginx is not running" | mail -s "Alert: Nginx Down" admin@example.com
fi

if ! systemctl is-active --quiet redis-server; then
    echo "Redis is not running" | mail -s "Alert: Redis Down" admin@example.com
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is ${DISK_USAGE}%" | mail -s "Alert: High Disk Usage" admin@example.com
fi

# Check for expired batches
EXPIRED_COUNT=$(bench --site pharma.example.com execute --cmd "import frappe; print(frappe.db.count('Pharma Batch', {'expiry_date': ['<', frappe.utils.today()]}))")
if [ $EXPIRED_COUNT -gt 0 ]; then
    echo "Found ${EXPIRED_COUNT} expired batches" | mail -s "Alert: Expired Batches" admin@example.com
fi
```

```bash
# Make script executable
chmod +x /home/frappeuser/monitor_pharma.sh

# Add to crontab
crontab -e
```

Add to crontab:
```
*/5 * * * * /home/frappeuser/monitor_pharma.sh
```

### Step 4: Configure Performance Monitoring

```bash
# Install performance monitoring
sudo apt install -y sysstat

# Enable collection
sudo systemctl enable sysstat
sudo systemctl start sysstat

# View performance
iostat -x 1
vmstat 1
mpstat 1
```

## Backup and Recovery

### Step 1: Configure Automated Backups

```bash
# Create backup script
nano /home/frappeuser/backup_pharma.sh
```

```bash
#!/bin/bash
# Pharmaceutical Compliance Backup Script

BACKUP_DIR="/home/frappeuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)
SITE="pharma.example.com"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
bench --site $SITE backup --with-files --backup-path $BACKUP_DIR

# Archive old backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Upload to remote storage (optional)
# rsync -avz $BACKUP_DIR/ user@remote-server:/backup/location/

echo "Backup completed: $DATE"
```

```bash
# Make script executable
chmod +x /home/frappeuser/backup_pharma.sh

# Add to crontab (daily at 2 AM)
crontab -e
```

Add to crontab:
```
0 2 * * * /home/frappeuser/backup_pharma.sh
```

### Step 2: Manual Backup

```bash
# Database backup
bench --site pharma.example.com backup

# Backup with files
bench --site pharma.example.com backup --with-files

# Backup to specific location
bench --site pharma.example.com backup --backup-path /path/to/backup
```

### Step 3: Restore from Backup

```bash
# Restore database
bench --site pharma.example.com restore /path/to/backup/file.sql.gz

# Restore with files
bench --site pharma.example.com restore /path/to/backup/file.sql.gz --with-files
```

### Step 4: Encryption Key Backup

```bash
# Export encryption keys
bench --site pharma.example.com execute --cmd "import frappe; keys = frappe.get_all('Encryption Key', {'status': 'Active'}); print(keys)"

# Store securely offline
# Never store encryption keys in the same location as backups
```

## Troubleshooting

### Common Issues

**Issue: Batch creation fails**

Solution:
```bash
# Check database connection
bench --site pharma.example.com mariadb --execute "SELECT 1;"

# Check for duplicate batch numbers
bench --site pharma.example.com execute --cmd "import frappe; print(frappe.db.get_all('Pharma Batch', {'batch_number': 'YOUR_BATCH_NUMBER'}))"

# Check required fields
bench --site pharma.example.com console
# frappe.get_doc('Pharma Batch', 'YOUR_BATCH_NAME').as_dict()
```

**Issue: Quality inspection not updating batch status**

Solution:
```bash
# Check inspection status
bench --site pharma.example.com execute --cmd "import frappe; print(frappe.get_doc('Pharma Quality Inspection', 'INSPECTION_NAME').inspection_status)"

# Check batch quality status
bench --site pharma.example.com execute --cmd "import frappe; print(frappe.get_doc('Pharma Batch', 'BATCH_NAME').quality_status)"

# Re-run inspection submission
bench --site pharma.example.com console
# doc = frappe.get_doc('Pharma Quality Inspection', 'INSPECTION_NAME')
# doc.submit()
```

**Issue: Temperature excursion not created**

Solution:
```bash
# Check temperature log status
bench --site pharma.example.com execute --cmd "import frappe; print(frappe.get_doc('Temperature Log', 'LOG_NAME').temperature_status)"

# Check excursion flag
bench --site pharma.example.com execute --cmd "import frappe; print(frappe.get_doc('Temperature Log', 'LOG_NAME').excursion_flag)"

# Manually create excursion
bench --site pharma.example.com console
# from omnexa_trading.omnexa_trading.doctype.temperature_log.temperature_log import TemperatureLog
# doc = frappe.get_doc('Temperature Log', 'LOG_NAME')
# doc._create_excursion_if_needed()
```

**Issue: Controlled substance sale blocked**

Solution:
```bash
# Check regulatory approval
bench --site pharma.example.com execute --cmd "import frappe; print(frappe.get_doc('Pharma Regulatory Approval', 'APPROVAL_NAME').approval_status)"

# Check license expiry
bench --site pharma.example.com execute --cmd "import frappe; print(frappe.get_doc('Pharma Batch', 'BATCH_NAME').license_expiry)"

# Check prescription validation
bench --site pharma.example.com console
# from omnexa_trading.omnexa_trading.doctype.pharma_regulatory_approval.pharma_regulatory_approval import validate_controlled_substance_sale
# validate_controlled_substance_sale('BATCH_NAME', 10)
```

**Issue: Scheduler not running**

Solution:
```bash
# Check scheduler status
bench --site pharma.example.com scheduler status

# Enable scheduler
bench --site pharma.example.com enable-scheduler

# Restart services
bench restart

# Check scheduler logs
tail -f ~/frappe-bench/logs/scheduler.log
```

**Issue: Performance issues**

Solution:
```bash
# Check database performance
bench --site pharma.example.com mariadb --execute "SHOW PROCESSLIST;"

# Check slow queries
bench --site pharma.example.com mariadb --execute "SHOW VARIABLES LIKE 'slow_query%';"

# Optimize database
bench --site pharma.example.com mariadb --execute "OPTIMIZE TABLE \`tabPharma Batch\`;"

# Clear cache
bench clear-cache
bench --site pharma.example.com clear-cache
```

### Getting Support

For additional support:
- Check Frappe documentation: https://frappeframework.com/docs
- Check Omnexa documentation: https://docs.omnexa.com
- Contact support: support@omnexa.com
- Create GitHub issue: https://github.com/omnexa/omnexa_trading/issues

### Maintenance Tasks

**Weekly:**
- Review audit logs for suspicious activity
- Check temperature excursion reports
- Verify backup completion
- Monitor system performance

**Monthly:**
- Review and update field permissions
- Rotate encryption keys (if configured)
- Review and update regulatory approvals
- Check license expiry dates

**Quarterly:**
- Review and update security policies
- Conduct security audit
- Review and update user access
- Test disaster recovery procedures

**Annually:**
- Full security audit
- Compliance review
- System performance review
- Disaster recovery testing
