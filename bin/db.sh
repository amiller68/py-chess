#!/usr/bin/env bash
# PostgreSQL container management script for py-chess

set -o errexit
set -o nounset

# Get script directory and source utilities
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/utils"

# Configuration
POSTGRES_CONTAINER_NAME="chess-postgres"
POSTGRES_VOLUME_NAME="chess-postgres-data"
POSTGRES_PORT=5434
POSTGRES_USER=chess
POSTGRES_PASSWORD=chess
POSTGRES_IMAGE_NAME=postgres:16
POSTGRES_DB=chess

# Check if docker or podman is available
CONTAINER_RUNTIME="docker"
if ! which docker &>/dev/null && which podman &>/dev/null; then
    CONTAINER_RUNTIME="podman"
fi

# Verify Docker/Podman is running
function check_runtime {
    if ! $CONTAINER_RUNTIME ps &>/dev/null; then
        print_error "$CONTAINER_RUNTIME is not running. Please start it first."
        exit 1
    fi
}

# Start local PostgreSQL for development
function up {
    check_runtime

    print_header "Starting PostgreSQL"

    if $CONTAINER_RUNTIME ps | grep -q "$POSTGRES_CONTAINER_NAME"; then
        print_success "PostgreSQL container is already running."
        verify_connection
        return
    fi

    if $CONTAINER_RUNTIME ps -a | grep -q "$POSTGRES_CONTAINER_NAME"; then
        echo "Starting existing PostgreSQL container..."
        $CONTAINER_RUNTIME start $POSTGRES_CONTAINER_NAME
    else
        echo "Creating new PostgreSQL container..."
        $CONTAINER_RUNTIME volume create $POSTGRES_VOLUME_NAME 2>/dev/null || true

        $CONTAINER_RUNTIME run \
            --name $POSTGRES_CONTAINER_NAME \
            --publish $POSTGRES_PORT:5432 \
            --volume $POSTGRES_VOLUME_NAME:/var/lib/postgresql/data \
            --env POSTGRES_USER=$POSTGRES_USER \
            --env POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
            --env POSTGRES_DB=$POSTGRES_DB \
            --env POSTGRES_HOST_AUTH_METHOD=trust \
            --health-cmd="pg_isready -U $POSTGRES_USER" \
            --health-interval=5s \
            --health-timeout=5s \
            --health-retries=5 \
            --detach \
            $POSTGRES_IMAGE_NAME
    fi

    echo -e "${YELLOW}Waiting for PostgreSQL to be ready...${NC}"
    sleep 3

    verify_connection

    echo ""
    print_success "PostgreSQL started!"
    echo ""
    echo -e "${YELLOW}Connection URL:${NC}"
    echo "  postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}"
}

# Verify connection to PostgreSQL
function verify_connection {
    if command -v pg_isready &>/dev/null; then
        if pg_isready -h localhost -p $POSTGRES_PORT -U $POSTGRES_USER &>/dev/null; then
            print_success "Connection verified"
        else
            print_warning "Connection test failed - PostgreSQL may still be starting"
        fi
    fi
}

function down {
    check_runtime
    print_header "Stopping PostgreSQL"

    echo "Stopping PostgreSQL container..."
    $CONTAINER_RUNTIME stop $POSTGRES_CONTAINER_NAME 2>/dev/null || true
    check_result "Container stop"

    echo "Removing PostgreSQL container..."
    $CONTAINER_RUNTIME rm -f $POSTGRES_CONTAINER_NAME 2>/dev/null || true
    check_result "Container removal"

    echo "Removing PostgreSQL volume..."
    $CONTAINER_RUNTIME volume rm -f $POSTGRES_VOLUME_NAME 2>/dev/null || true
    check_result "Volume removal"

    print_summary "PostgreSQL cleaned up successfully!" "cleanup step(s) failed"
}

function endpoint {
    echo "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT}/${POSTGRES_DB}"
}

function connect {
    check_runtime
    if ! $CONTAINER_RUNTIME ps | grep -q "$POSTGRES_CONTAINER_NAME"; then
        print_error "PostgreSQL container is not running. Start it with: $0 up"
        exit 1
    fi
    psql "$(endpoint)"
}

function migrate {
    print_header "Running Database Migrations"

    if [ -z "${POSTGRES_URL:-}" ]; then
        print_warning "POSTGRES_URL not set, using local container"
        export POSTGRES_URL=$(endpoint)
    fi

    echo "Running migrations with Alembic..."
    uv run alembic upgrade head
    check_result "Database migrations"

    print_summary "Migrations completed!" "migration(s) failed"
}

function prepare {
    print_header "Preparing Database Migration"

    local manual=false
    local description=""

    # Check environment variable for manual flag
    if [ "${MANUAL:-}" = "1" ] || [ "${MANUAL:-}" = "true" ]; then
        manual=true
    fi

    # Parse arguments
    while [[ "$#" -gt 0 ]]; do
        case $1 in
        --manual)
            manual=true
            shift
            ;;
        *)
            description="$*"
            break
            ;;
        esac
    done

    if [ -z "$description" ]; then
        print_error "Please provide a description for the migration."
        echo "Usage: $0 prepare [--manual] <description>"
        echo "Example: $0 prepare 'Add user table'"
        exit 1
    fi

    # Ensure PostgreSQL is running
    up

    export POSTGRES_URL=$(endpoint)

    echo "Generating migration: $description"

    if [ "$manual" = true ]; then
        echo "Creating manual migration..."
        uv run alembic revision -m "$description"
    else
        echo "Auto-generating migration from model changes..."
        uv run alembic revision --autogenerate -m "$description"
    fi

    check_result "Migration generation"
    print_summary "Migration prepared!" "migration preparation failed"
}

function status {
    check_runtime
    print_header "PostgreSQL Status"

    if $CONTAINER_RUNTIME ps | grep -q "$POSTGRES_CONTAINER_NAME"; then
        print_success "PostgreSQL container is running"
        echo ""
        echo -e "${YELLOW}Recent logs:${NC}"
        $CONTAINER_RUNTIME logs --tail 10 $POSTGRES_CONTAINER_NAME 2>&1 || true
        echo ""
        verify_connection
    else
        print_error "PostgreSQL container is not running"
        echo ""
        echo "Start it with: $0 up"
    fi
}

function help {
    echo -e "${YELLOW}PostgreSQL Database Manager${NC}"
    echo ""
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Container Commands:"
    echo "  up                 Start PostgreSQL container"
    echo "  down               Stop and remove container/volume"
    echo "  status             Check container status"
    echo "  endpoint           Print connection URL"
    echo "  connect            Open psql connection"
    echo ""
    echo "Migration Commands:"
    echo "  migrate            Run database migrations"
    echo "  prepare <desc>     Create a new migration"
    echo "    --manual         Create empty migration (no auto-generate)"
    echo ""
    echo "  help               Show this help message"
    echo ""
    echo "Environment:"
    echo "  POSTGRES_URL       Override connection URL"
    echo "  MANUAL=1           Use manual migration mode"
}

# Process command
CMD=${1:-help}
shift || true

case "$CMD" in
up | down | endpoint | connect | status | help | migrate | prepare)
    $CMD "$@"
    ;;
*)
    print_error "Unknown command: $CMD"
    help
    exit 1
    ;;
esac
