from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.logger import Logger
from src.server.deps import async_db, logger, require_logged_in_user
from src.server.handlers.page import PageResponse

# Create page response helper
page = PageResponse(template="pages/app/dashboard.html", layout="layouts/app.html")


async def handler(
    request: Request,
    user: User = Depends(require_logged_in_user),
    db: AsyncSession = Depends(async_db),
    logger: Logger = Depends(logger),
):
    """Dashboard page - requires authentication

    Args:
        request: The incoming request
        user: Current authenticated user (auto-injected via deps)
        db: Database session
        logger: Request span for logging

    Returns:
        HTMLResponse with full layout or just content for HTMX
    """
    logger.info(f"Dashboard access by user: {user.email}")

    # For now just pass user data
    # In the future you might fetch recent activity, stats, etc.
    return page.render(
        request,
        {
            "user": user,
        },
    )
