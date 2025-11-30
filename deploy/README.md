# Deploy Scripts

This directory contains deployment scripts and configurations for the FastAPI application.

## Directory Structure

```
deploy/
├── db_scripts/           # Database initialization scripts
├── entrypoint_scripts/   # Docker entrypoint scripts
├── shell_scripts/        # Shell scripts for starting services
├── supervisor_scripts/   # Supervisor configuration files
└── uvicorn_start.sh     # Legacy uvicorn startup script (deprecated)
```

## Scripts Overview

### Database Scripts (`db_scripts/`)

#### `init_schema.sh`
- Initializes PostgreSQL database schema
- Waits for PostgreSQL to be available
- Creates schema if it doesn't exist
- **Environment Variables Required:**
  - `POSTGRES_USER` - Database user
  - `POSTGRES_PASSWORD` - Database password
  - `POSTGRES_DB` - Database name
  - `DB_SCHEMA` - Schema name to create

**Usage:**
```bash
./deploy/db_scripts/init_schema.sh
```

### Entrypoint Scripts (`entrypoint_scripts/`)

#### `gunicorn_entrypoint.sh`
- Main entrypoint for production deployments
- Loads environment variables from `env/.env`
- Supports two modes:
  - **Supervisor mode** (default): Runs Gunicorn under Supervisor for process management
  - **Direct mode**: Runs Gunicorn directly without Supervisor

**Environment Variables:**
- `USE_SUPERVISOR` - Set to `false` to skip Supervisor (default: `true`)

**Usage:**
```bash
./deploy/entrypoint_scripts/gunicorn_entrypoint.sh
```

#### `entrypoint.sh`
- Generic entrypoint script
- Loads environment variables
- Executes any command passed as arguments

**Usage:**
```bash
./deploy/entrypoint_scripts/entrypoint.sh <command>
```

### Shell Scripts (`shell_scripts/`)

#### `gunicorn_start.sh`
- Starts Gunicorn with Uvicorn workers
- Configurable number of workers
- Production-ready timeouts and settings

**Environment Variables:**
- `UVICORN_WORKERS` - Number of worker processes (default: 4)

**Configuration:**
- **Bind address:** `0.0.0.0:8000`
- **Worker class:** `uvicorn.workers.UvicornWorker`
- **Timeout:** 130 seconds
- **Graceful timeout:** 130 seconds
- **Keep-alive:** 60 seconds
- **Log level:** info

**Usage:**
```bash
./deploy/shell_scripts/gunicorn_start.sh
```

### Supervisor Scripts (`supervisor_scripts/`)

#### `gunicorn_supervisord.conf`
- Supervisor configuration for Gunicorn/Uvicorn process
- Manages process lifecycle (auto-restart, retries)
- Configures logging with rotation

**Features:**
- Auto-start on supervisor startup
- Auto-restart on failure
- 5 retry attempts
- Log rotation (10MB max, 5 backups)

#### `supervisord.conf`
- Main Supervisor configuration
- Includes all configs from `/etc/supervisor/conf.d/`

## Deployment Modes

### 1. Direct Mode (Development)
Run Gunicorn directly without Supervisor:

```bash
export USE_SUPERVISOR=false
./deploy/entrypoint_scripts/gunicorn_entrypoint.sh
```

### 2. Supervisor Mode (Production)
Run Gunicorn under Supervisor for process management:

```bash
export USE_SUPERVISOR=true
./deploy/entrypoint_scripts/gunicorn_entrypoint.sh
```

### 3. Docker Deployment
Use the entrypoint in your Dockerfile:

```dockerfile
ENTRYPOINT ["/app/deploy/entrypoint_scripts/gunicorn_entrypoint.sh"]
```

## Environment Variables

Create an `env/.env` file with the following variables:

```bash
# Application
APP_MODULE=src.main:app

# Gunicorn/Uvicorn
UVICORN_WORKERS=4
USE_SUPERVISOR=true

# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=myapp
DB_SCHEMA=public

# Server
HOST=0.0.0.0
PORT=8000
```

## Logging

### Supervisor Logs
- **Supervisor main log:** `/var/log/supervisor/supervisord.log`
- **Uvicorn stdout:** `/var/log/supervisor/uvicorn.log`
- **Gunicorn errors:** `/var/log/supervisor/gunicorn_error.log`

### Application Logs
Gunicorn logs to stdout/stderr, which are captured by Supervisor.

## Process Management

### Supervisor Commands

```bash
# Start all processes
supervisorctl start all

# Stop all processes
supervisorctl stop all

# Restart all processes
supervisorctl restart all

# Check status
supervisorctl status

# Reload configuration
supervisorctl reread
supervisorctl update
```

## Migration from Legacy Script

The legacy `uvicorn_start.sh` script is deprecated. Use the new structured approach:

**Old:**
```bash
./deploy/uvicorn_start.sh
```

**New:**
```bash
./deploy/entrypoint_scripts/gunicorn_entrypoint.sh
```

## Best Practices

1. **Always use Supervisor in production** for automatic process recovery
2. **Set appropriate worker count** based on CPU cores (recommended: 2-4 × CPU cores)
3. **Monitor logs** regularly for errors and performance issues
4. **Use environment variables** for configuration, never hardcode
5. **Test scripts locally** before deploying to production

## Troubleshooting

### Gunicorn won't start
- Check environment variables are loaded correctly
- Verify `env/.env` file exists and is readable
- Check application code for syntax errors

### Supervisor issues
- Check `/var/log/supervisor/supervisord.log` for errors
- Ensure supervisor is installed: `apt-get install supervisor`
- Verify configuration syntax: `supervisord -c <config> -n`

### Database connection issues
- Run `init_schema.sh` to ensure schema exists
- Check PostgreSQL is running and accessible
- Verify database credentials in environment variables

## Additional Resources

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Supervisor Documentation](http://supervisord.org/)
