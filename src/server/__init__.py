import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, cast

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse
from starlette.exceptions import HTTPException
from starlette.middleware import _MiddlewareFactory
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from watchfiles import awatch

from src.state import AppState

from .api import router as api_router
from .health import router as health_router
from .pages import router as pages_router


def create_app(app_state: AppState) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await app_state.startup()
        yield
        await app_state.shutdown()

    app = FastAPI(lifespan=lifespan, title="py-chess")

    # Store app_state on the app instance
    app.state.app_state = app_state

    async def state_middleware(request: Request, call_next):
        request.state.app_state = app.state.app_state
        return await call_next(request)

    async def logger_middleware(request: Request, call_next):
        request.state.logger = app.state.app_state.logger.with_request(request)
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            request.state.logger.error(str(e))
            raise

    async def db_middleware(request: Request, call_next):
        async with app.state.app_state.database.session() as session:
            request.state.db = session
            try:
                response = await call_next(request)
                return response
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    templates = Jinja2Templates(directory="templates")

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        # Return JSON for API routes, HTML for everything else
        if request.url.path.startswith("/api"):
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )

        # For 404s on non-API routes, return nice HTML page
        if exc.status_code == 404:
            return HTMLResponse(
                content=templates.TemplateResponse("pages/404.html", {"request": request}).body,
                status_code=404,
            )

        # Other HTTP errors - return JSON for now
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # Add middleware
    app.middleware("http")(state_middleware)
    app.middleware("http")(logger_middleware)
    app.middleware("http")(db_middleware)

    # Trust proxy headers (X-Forwarded-Proto, X-Forwarded-For) for HTTPS behind reverse proxy
    app.add_middleware(cast(_MiddlewareFactory[Any], ProxyHeadersMiddleware), trusted_hosts=["*"])

    # Hot reloading for development
    if app_state.config.dev_mode:
        dev_router = APIRouter()

        @dev_router.get("/dev/hot-reload")
        async def hot_reload(request: Request):
            async def event_generator():
                watch_dirs = [Path("templates"), Path("src"), Path("static")]
                try:
                    watcher = awatch(*watch_dirs, stop_event=asyncio.Event())
                    print("✓ Hot reload watcher started")

                    yield {"event": "connected", "data": "Hot reload connected"}

                    async for changes in watcher:
                        # Check if client disconnected
                        if await request.is_disconnected():
                            break
                        if changes:
                            for change_type, path in changes:
                                print(f"Hot reload: {change_type} {path}")
                            yield {"event": "reload", "data": "reload"}
                except asyncio.CancelledError:
                    pass  # Clean shutdown
                finally:
                    print("Hot reload cleanup")

            return EventSourceResponse(event_generator())

        app.include_router(dev_router)

    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Include routers
    app.include_router(pages_router)
    app.include_router(api_router, prefix="/api")
    app.include_router(health_router, prefix="/_status")

    @app.get("/up")
    async def up():
        return {"status": "ok"}

    return app
