from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from src.database.models import User

from ....deps import get_logged_in_user

router = APIRouter()


@router.get("/whoami", response_class=HTMLResponse)
async def whoami(user: User | None = Depends(get_logged_in_user)) -> str:
    if not user:
        return "<span class='text-muted-foreground'>Not logged in</span>"

    return f"""
    <div class="flex items-center gap-2">
        <uk-icon icon="user" class="size-4"></uk-icon>
        <span class="text-sm">{user.email}</span>
    </div>
    """
