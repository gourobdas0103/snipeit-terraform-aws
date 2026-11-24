#!/usr/bin/env bash
# ==============================================================================
# Snipe-IT Automated Deployment Cloud-Init Script for Ubuntu
# Deploys official Snipe-IT + MariaDB via Docker Compose
# ==============================================================================
set -euo pipefail
exec > >(tee -a /var/log/snipeit-cloudinit.log) 2>&1

echo "===================================================================="
echo "[$(date)] Starting Snipe-IT automated provisioning..."
echo "===================================================================="

# 1. CONFIGURE 2GB SWAP FILE (CRITICAL FOR t2.micro/t3.micro 1GB INSTANCES)
if [ ! -f /swapfile ]; then
    echo "[$(date)] Configuring 2GB Swapfile to prevent MariaDB Out-Of-Memory (OOM)..."
    fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    sysctl vm.swappiness=10
    echo 'vm.swappiness=10' >> /etc/sysctl.d/99-swap.conf
    free -h
fi

# 2. INSTALL DOCKER ENGINE & DOCKER COMPOSE V2
echo "[$(date)] Installing Docker and Docker Compose v2..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release git jq ufw

install -m 0755 -d /etc/apt/keyrings
if [ ! -f /etc/apt/keyrings/docker.asc ]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    chmod a+r /etc/apt/keyrings/docker.asc
fi

UBUNTU_CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $UBUNTU_CODENAME stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable --now docker
usermod -aG docker ubuntu

docker --version
docker compose version

# 3. CONFIGURE DIRECTORY & DOWNLOAD OFFICIAL DOCKER FILES
echo "[$(date)] Setting up ~/snipe-it and fetching official configurations..."
SNIPEIT_DIR="/home/ubuntu/snipe-it"
mkdir -p "$SNIPEIT_DIR"
cd "$SNIPEIT_DIR"

curl -fsSL https://raw.githubusercontent.com/grokability/snipe-it/master/docker-compose.yml -o docker-compose.yml
curl -fsSL https://raw.githubusercontent.com/grokability/snipe-it/master/.env.docker -o .env

# 4. DISCOVER PUBLIC IP (IMDSv2)
echo "[$(date)] Resolving EC2 Public IP address..."
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60" 2>/dev/null || true)
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || curl -s https://ifconfig.me || echo "127.0.0.1")
echo "Public IP detected: $PUBLIC_IP"

# 5. CONFIGURE .env FILE
echo "[$(date)] Configuring .env parameters..."
sed -i "s|^APP_URL=.*|APP_URL=http://$${PUBLIC_IP}:${app_port}|g" .env
sed -i "s|^APP_PORT=.*|APP_PORT=${app_port}|g" .env
sed -i "s|^APP_TIMEZONE=.*|APP_TIMEZONE='${timezone}'|g" .env
sed -i "s|^DB_CONNECTION=.*|DB_CONNECTION=mariadb|g" .env
sed -i "s|^DB_HOST=.*|DB_HOST=db|g" .env
sed -i "s|^DB_DATABASE=.*|DB_DATABASE=${db_database}|g" .env
sed -i "s|^DB_USERNAME=.*|DB_USERNAME=${db_username}|g" .env
sed -i "s|^DB_PASSWORD=.*|DB_PASSWORD=${db_password}|g" .env
sed -i "s|^MYSQL_ROOT_PASSWORD=.*|MYSQL_ROOT_PASSWORD=${mysql_root_password}|g" .env

# Mail configuration
sed -i "s|^MAIL_MAILER=.*|MAIL_MAILER=${mail_mailer}|g" .env
if [ "${mail_mailer}" = "smtp" ]; then
    sed -i "s|^MAIL_HOST=.*|MAIL_HOST=${mail_host}|g" .env
    sed -i "s|^MAIL_PORT=.*|MAIL_PORT=${mail_port}|g" .env
    sed -i "s|^MAIL_USERNAME=.*|MAIL_USERNAME=${mail_username}|g" .env
    sed -i "s|^MAIL_PASSWORD=.*|MAIL_PASSWORD=${mail_password}|g" .env
    sed -i "s|^MAIL_ENCRYPTION=.*|MAIL_ENCRYPTION=${mail_encryption}|g" .env
fi

# 6. GENERATE FRESH APP_KEY
echo "[$(date)] Generating new APP_KEY using Docker container..."
APP_KEY=$(docker compose run --rm -T app php artisan key:generate --show)
echo "Generated APP_KEY: $APP_KEY"
sed -i "s|^APP_KEY=.*|APP_KEY=$APP_KEY|g" .env

# Adjust ownership
chown -R ubuntu:ubuntu "$SNIPEIT_DIR"

# 7. DEPLOY SNIPE-IT SERVICES
echo "[$(date)] Launching Docker Compose stack in detached mode..."
docker compose up -d

# 8. VERIFY HEALTH AND WAIT FOR MARIADB
echo "[$(date)] Waiting for MariaDB service to report healthy..."
for i in {1..30}; do
    STATUS=$(docker compose ps db --format '{{.Health}}' 2>/dev/null || echo "")
    if [[ "$STATUS" == *"healthy"* ]]; then
        echo "MariaDB is healthy!"
        break
    fi
    echo "Current MariaDB health status: $STATUS. Sleeping 5s ($i/30)..."
    sleep 5
done

# Run initial database migration check
echo "[$(date)] Running artisan migration check..."
docker compose exec -T app php artisan migrate --force || true

echo "===================================================================="
echo "[$(date)] Snipe-IT deployment finished successfully!"
echo "Access the portal at: http://$PUBLIC_IP:${app_port}"
echo "===================================================================="
touch /home/ubuntu/snipeit-ready.flag
