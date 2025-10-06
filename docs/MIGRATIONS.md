# Database Migrations

This template includes a single, comprehensive migration file that contains all database tables. You can customize it by removing sections you don't need.

## Migration File

### Initial Database Schema
**File:** `42ab7b48e86b_initial_database_schema_with_all_tables.py`

This single migration file contains three main sections:

#### 1. Users Table Section
- Creates the `users` table with authentication fields
- Includes: email, username, password_hash, first_name, last_name, age, is_active, is_verified, is_superuser, last_login
- **Remove this section** if you don't need user authentication

#### 2. Articles Table Section
- Creates the `articles` table for content management
- Includes: title, content
- **Remove this section** if you don't need content management

#### 3. Sensitive Fields Table Section
- Creates the `sensitive_fields` table for data protection
- Includes: field_name, is_exact_match, is_active, description
- **Remove this section** if you don't need data protection features

All tables use generic `sa.UUID()` for database portability.

## Usage

### Run Migration
```bash
alembic upgrade head
```

### Rollback Migration
```bash
# Rollback to previous migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base
```

## Template Customization

When using this as a template, customize the migration file by removing sections you don't need:

### 1. Authentication Only (Users Table)
Remove the Articles and Sensitive Fields sections from the migration file:
- Delete lines 107-144 (Articles table section)
- Delete lines 146-198 (Sensitive Fields table section)
- Update the downgrade function accordingly

### 2. Content Management (Users + Articles)
Remove the Sensitive Fields section from the migration file:
- Delete lines 146-198 (Sensitive Fields table section)
- Update the downgrade function accordingly

### 3. Data Protection (Users + Sensitive Fields)
Remove the Articles section from the migration file:
- Delete lines 107-144 (Articles table section)
- Update the downgrade function accordingly

### 4. Custom Tables
Add your own table sections following the same pattern:
- Use clear section headers with comments
- Include all necessary columns and indexes
- Add corresponding drop statements in the downgrade function

## Migration Structure

```
base → 42ab7b48e86b (all tables in one migration)
```

## Generic UUID vs PostgreSQL UUID

This project uses `sa.UUID()` (generic SQLAlchemy UUID) instead of `postgresql.UUID()` for:
- **Database portability** - Works with PostgreSQL, MySQL, SQLite, etc.
- **Template flexibility** - Can be used with different database backends
- **Consistency** - All UUID fields use the same type

## Base Models

All tables inherit from `BaseModel` which provides:
- `id`: UUID primary key with auto-generation
- `created_at`: Timestamp when record was created
- `updated_at`: Timestamp when record was last updated
- Automatic indexing on common fields
- Consistent field naming and types

## Examples

### Authentication Only Setup
1. Edit the migration file and remove the Articles and Sensitive Fields sections
2. Run the migration:
```bash
alembic upgrade head
```

### Content Management Setup
1. Edit the migration file and remove the Sensitive Fields section
2. Run the migration:
```bash
alembic upgrade head
```

### Data Protection Setup
1. Edit the migration file and remove the Articles section
2. Run the migration:
```bash
alembic upgrade head
```

### Full Setup (All Tables)
1. Keep the migration file as-is
2. Run the migration:
```bash
alembic upgrade head
```

