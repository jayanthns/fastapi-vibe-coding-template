# Deploy Folder Comparison

## Django Ninja Ready-to-Go vs FastAPI Vibe Coding Template

### ✅ Structure Alignment Complete

Both projects now have identical deploy folder structures:

```
deploy/
├── db_scripts/
│   └── init_schema.sh
├── entrypoint_scripts/
│   ├── entrypoint.sh
│   └── gunicorn_entrypoint.sh
├── shell_scripts/
│   └── gunicorn_start.sh
├── supervisor_scripts/
│   ├── gunicorn_supervisord.conf
│   └── supervisord.conf
└── README.md (FastAPI only - added documentation)
```

### Key Differences Adapted for FastAPI

#### 1. Application Module Path
**Django Ninja:**
```bash
gunicorn main.asgi:application
```

**FastAPI:**
```bash
gunicorn src.main:app
```

#### 2. Worker Configuration
Both use the same Uvicorn worker class:
```bash
-k uvicorn.workers.UvicornWorker
```

#### 3. Environment Loading
Both load from `env/.env` file with identical error handling

### Features Implemented

✅ **Database Initialization**
- PostgreSQL schema creation
- Wait-for-database logic
- Schema existence checking

✅ **Flexible Deployment Modes**
- Direct Gunicorn mode (development)
- Supervisor mode (production)
- Configurable via `USE_SUPERVISOR` env var

✅ **Process Management**
- Supervisor configuration for auto-restart
- Log rotation (10MB max, 5 backups)
- Graceful shutdown handling

✅ **Production-Ready Settings**
- 130s timeout for long-running requests
- 60s keep-alive for connection reuse
- Configurable worker count (default: 4)
- Proper logging to stdout/stderr

### Additional Improvements in FastAPI

1. **Comprehensive Documentation**
   - Added `deploy/README.md` with full usage guide
   - Environment variable documentation
   - Troubleshooting section
   - Best practices

2. **Backward Compatibility**
   - Kept legacy `uvicorn_start.sh` for existing deployments
   - Documented migration path

### Environment Variables Comparison

| Variable | Django Ninja | FastAPI | Purpose |
|----------|-------------|---------|---------|
| `UVICORN_WORKERS` | ✅ | ✅ | Number of worker processes |
| `USE_SUPERVISOR` | ✅ | ✅ | Enable/disable supervisor mode |
| `POSTGRES_USER` | ✅ | ✅ | Database user |
| `POSTGRES_PASSWORD` | ✅ | ✅ | Database password |
| `POSTGRES_DB` | ✅ | ✅ | Database name |
| `DB_SCHEMA` | ✅ | ✅ | Schema name |

### Deployment Workflow Comparison

Both projects now support identical deployment workflows:

#### Development
```bash
export USE_SUPERVISOR=false
./deploy/entrypoint_scripts/gunicorn_entrypoint.sh
```

#### Production
```bash
export USE_SUPERVISOR=true
./deploy/entrypoint_scripts/gunicorn_entrypoint.sh
```

#### Docker
```dockerfile
ENTRYPOINT ["/app/deploy/entrypoint_scripts/gunicorn_entrypoint.sh"]
```

### Missing from Django Ninja (Not Applicable)

The following Django Ninja files were not replicated as they're Django-specific:

- `celery_entrypoint.sh` - FastAPI doesn't use Celery by default
- `celery_start.sh` - FastAPI uses background tasks differently
- `celery_multiple_workers_start.sh` - Not applicable
- `celery_supervisord.conf` - Not applicable

**Note:** If you need Celery support in FastAPI, these can be added separately.

### Verification Checklist

- [x] Directory structure matches
- [x] Database initialization script
- [x] Gunicorn startup script
- [x] Entrypoint scripts (generic + gunicorn)
- [x] Supervisor configurations
- [x] Environment variable loading
- [x] Executable permissions set
- [x] Documentation added
- [x] Production-ready settings

### Next Steps

1. ✅ Deploy folder structure aligned
2. 🔄 Test deployment scripts locally
3. 🔄 Update Dockerfile to use new entrypoint
4. 🔄 Create `env/.env.example` template
5. 🔄 Update deployment documentation in main README

### Testing the Scripts

```bash
# Test environment loading
./deploy/entrypoint_scripts/entrypoint.sh echo "Environment loaded"

# Test gunicorn startup (dry run)
export USE_SUPERVISOR=false
export UVICORN_WORKERS=2
./deploy/shell_scripts/gunicorn_start.sh

# Test supervisor mode
export USE_SUPERVISOR=true
./deploy/entrypoint_scripts/gunicorn_entrypoint.sh
```

## Conclusion

The FastAPI project now has **feature parity** with the Django Ninja project's deployment infrastructure, with additional improvements in documentation and backward compatibility.
