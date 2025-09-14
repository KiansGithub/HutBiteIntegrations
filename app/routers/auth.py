from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from urllib.parse import urlencode
import base64, secrets
import httpx
from app.core.config import settings

router = APIRouter(prefix="", tags=["auth"])

@router.get("/")
def root(request: Request):
    return {
        "hello": "world",
        "hubrise_connected": bool(request.session.get("hubrise_conn")),
    }

@router.get("/connect")
def connect_to_hubrise(request: Request):
    redirect_uri = f"{settings.APP_BASE_URL}/hubrise/oauth/callback"
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    params = {
        "redirect_uri": redirect_uri,
        "client_id": settings.HUBRISE_CLIENT_ID,
        "scope": settings.HUBRISE_SCOPE,
        "state": state,
    }
    auth_url = f"{settings.HUBRISE_OAUTH_URL}/authorize?{urlencode(params)}"
    return RedirectResponse(auth_url)

@router.get("/hubrise/oauth/callback")
async def hubrise_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        return HTMLResponse(f"<h3>Authorization error:</h3><pre>{error}</pre>", status_code=400)

    saved_state = request.session.get("oauth_state")
    if not code or not state or state != saved_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth callback/state")

    token_url = f"{settings.HUBRISE_OAUTH_URL}/token"
    basic = base64.b64encode(f"{settings.HUBRISE_CLIENT_ID}:{settings.HUBRISE_CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post(token_url, headers=headers, data={"code": code})
        r.raise_for_status()
        payload = r.json()

    request.session["hubrise_conn"] = payload  # includes access_token, account_id, location_id, etc.
    request.session.pop("oauth_state", None)

    return HTMLResponse("<p>Connected to HubRise. Now hit <a href='/orders/example'>/orders/example</a></p>")
