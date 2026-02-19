#!/bin/bash
set -e

# Configuration
DB_NAME="psra"
DB_USER="psra_user"
DB_PASS="psra_pass123"
DB_HOST="localhost"
DB_PORT="5432"

echo "=== Installing PostgreSQL on Ubuntu ==="

# 1. Update package list and install PostgreSQL
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# 2. Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 3. Wait for PostgreSQL to be ready
sleep 2
sudo -u postgres pg_isready

# 4. Create database user (if not exists)
sudo -u postgres psql -c "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

# 5. Create database (if not exists)
sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

# 6. Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
sudo -u postgres psql -d $DB_NAME -c "GRANT ALL ON SCHEMA public TO $DB_USER;"

# 7. Configure pg_hba.conf for password authentication
PG_HBA="/etc/postgresql/*/main/pg_hba.conf"
for f in $PG_HBA; do
    if [ -f "$f" ]; then
        grep -q "host.*all.*all.*127.0.0.1/32.*md5" "$f" || \
            echo "host    all             all             127.0.0.1/32            md5" | sudo tee -a "$f"
    fi
done

# 8. Reload PostgreSQL configuration
sudo systemctl reload postgresql

# 9. Update .env file
if [ -f ".env" ]; then
    if grep -q "DATABASE_URL" .env; then
        sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}|" .env
    else
        echo "DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}" >> .env
    fi
fi

echo ""
echo "=== Setup Complete ==="
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Port: $DB_PORT"
echo ""
echo "Run migrations: flask db upgrade"
echo "Run migration script: python migrate_data.py"
