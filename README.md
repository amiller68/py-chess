# py-chess

A Python chess server with HTMX, SSE for real-time updates, and PostgreSQL persistence.

**Play now at [chess.krondor.org](https://chess.krondor.org)**

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) - Python package manager
- Docker (for PostgreSQL)

## Quick Start

```bash
# Install dependencies
make install

# Start PostgreSQL
make db up

# Run migrations
make db migrate

# Start dev server (with hot reload)
make dev
```

The server will be running at http://localhost:8000

## Development Commands

```bash
make help          # Show all available commands
make dev           # Run dev server with hot reload
make run           # Run production server
make test          # Run test suite
make lint          # Run linter (ruff)
make fmt           # Format code
make fmt-check     # Check code formatting
make types         # Type check (ty)
make check         # Run all checks (fmt-check, lint, types, test)
make clean         # Clean build artifacts
```

## Database Management

All database commands use `make db <command>`:

```bash
make db up         # Start PostgreSQL container (port 5434)
make db down       # Stop and remove container/volume
make db status     # Check container status
make db endpoint   # Print connection URL
make db connect    # Open psql connection
make db migrate    # Run Alembic migrations
make db prepare "Add new table"           # Create auto-generated migration
make db prepare --manual "Custom change"  # Create empty migration
```

### Migration Workflow

Migrations run automatically on deployment. For local development:

```bash
# 1. Make changes to SQLAlchemy models in src/database/models/
# 2. Generate migration
make db prepare "Add user preferences"

# 3. Test locally
make db migrate
make dev

# 4. Commit the migration file
git add alembic/versions/
git commit -m "migration: add user preferences"
```

## Docker

Run the full stack with Docker Compose:

```bash
make docker-run       # Build and run app + postgres
make docker-down      # Stop services
make docker-build     # Build image only
```

Or run the image directly:

```bash
docker build -t py-chess .
docker run -p 8000:8000 -e POSTGRES_URL=postgresql://... py-chess
```

## Deployment

The app deploys to [chess.krondor.org](https://chess.krondor.org) using Kamal with Terraform-managed infrastructure on DigitalOcean.

### Prerequisites

- [1Password CLI](https://developer.1password.com/docs/cli/) - for secrets management
- [Terraform](https://www.terraform.io/) - for infrastructure as code
- [Kamal 2.x](https://kamal-deploy.org/) - for container deployment
- Access to the `cloud-providers` 1Password vault

### First-Time Setup

```bash
# 1. Create Terraform Cloud organization and workspace
make tfc up

# 2. Initialize Terraform
make iac production init

# 3. Create infrastructure (DigitalOcean droplet, Cloudflare DNS)
make iac production apply

# 4. Initial deployment (sets up Docker network, boots postgres, deploys app)
make kamal chess production setup
```

### Deployment Commands

```bash
# Deploy latest changes
make deploy

# Or use the full command
make kamal chess production deploy

# Other useful commands
make kamal chess production logs          # View application logs
make kamal chess production app exec      # SSH into app container
make kamal chess production accessory logs postgres  # View postgres logs
```

### Infrastructure Commands

```bash
make tfc up                    # Create Terraform Cloud org/workspace
make tfc status                # Check Terraform Cloud status
make iac production init       # Initialize Terraform
make iac production apply      # Apply infrastructure changes
make iac production output     # Show infrastructure outputs
make iac production destroy    # Tear down infrastructure
```

### CI/CD

Deployments are automated via GitHub Actions on push to `main`:

- Triggers on changes to: `src/`, `templates/`, `static/`, `alembic/`, `Dockerfile`, `pyproject.toml`, `uv.lock`
- Requires `OP_SERVICE_ACCOUNT_TOKEN` secret in GitHub repository settings
- Creates a 1Password Service Account with access to `cloud-providers` vault

## Project Structure

```
├── src/
│   ├── __main__.py        # Entry point
│   ├── config.py          # Configuration from env vars
│   ├── state.py           # Application state
│   ├── chess/             # Chess logic
│   │   ├── service.py     # Move validation, game logic
│   │   └── render.py      # Board HTML rendering
│   ├── database/          # Database layer
│   │   ├── database.py    # Async SQLAlchemy setup
│   │   └── models/        # SQLAlchemy models
│   └── server/            # FastAPI server
│       ├── api/v0/        # API endpoints
│       └── pages/         # Page routes
├── templates/             # Jinja2 templates
├── static/                # Static assets (CSS, JS)
├── tests/                 # Test suite
├── alembic/               # Database migrations
├── bin/                   # Helper scripts
│   ├── utils              # Shared shell utilities
│   ├── db.sh              # Database management
│   ├── config             # Project configuration
│   ├── vault              # 1Password integration
│   ├── tfc                # Terraform Cloud management
│   ├── iac                # Terraform wrapper
│   └── kamal              # Kamal deployment wrapper
├── config/deploy/         # Kamal deployment configs
├── iac/                   # Terraform infrastructure
│   ├── modules/           # Reusable modules
│   └── stages/            # Stage configurations (production)
├── .github/workflows/     # CI/CD pipelines
├── Dockerfile             # Container image
├── docker-compose.yml     # Local full stack
└── Makefile               # Development commands
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DEV_MODE` | `false` | Enable hot reload |
| `DEBUG` | `true` | Enable debug logging |
| `HOST_NAME` | `http://localhost:8000` | Public server URL |
| `LISTEN_ADDRESS` | `0.0.0.0` | Bind address |
| `LISTEN_PORT` | `8000` | Server port |
| `POSTGRES_URL` | `postgresql://chess:chess@localhost:5434/chess` | Database connection |

Copy `.env.example` to `.env` and customize as needed.

## Troubleshooting

### Port 5434 already in use

```bash
# Check what's using the port
lsof -i :5434

# Or use a different port by modifying bin/db.sh
```

### Database connection refused

```bash
# Check if PostgreSQL is running
make db status

# Restart the container
make db down
make db up
```

### Hot reload not working

Make sure you're running with `make dev` (not `make run`), which sets `DEV_MODE=True`.

### Deployment fails with "could not translate host name"

The postgres accessory needs to be running. For first-time deployment, use `setup` instead of `deploy`:

```bash
make kamal chess production setup
```

For subsequent deploys, if postgres was stopped:

```bash
make kamal chess production accessory boot postgres
make deploy
```

## Tech Stack

**Application:**
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [HTMX](https://htmx.org/) - Frontend interactivity
- [SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) - Real-time updates
- [python-chess](https://python-chess.readthedocs.io/) - Chess move validation
- [SQLAlchemy 2.0](https://www.sqlalchemy.org/) - Async ORM
- [PostgreSQL](https://www.postgresql.org/) - Database
- [Alembic](https://alembic.sqlalchemy.org/) - Migrations
- [Jinja2](https://jinja.palletsprojects.com/) - Templating
- [Franken UI](https://franken-ui.dev/) - Styling

**Infrastructure:**
- [Kamal](https://kamal-deploy.org/) - Container deployment
- [Terraform](https://www.terraform.io/) - Infrastructure as code
- [DigitalOcean](https://www.digitalocean.com/) - Cloud hosting
- [Cloudflare](https://www.cloudflare.com/) - DNS
- [1Password](https://1password.com/) - Secrets management
