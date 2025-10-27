from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager
import httpx

from app.core.config import settings
from app.core.errors import install_error_handlers
from app.routers import auth, orders, catalog, deliverability, sms, tables, ultimago

@asynccontextmanager 
async def lifespan(app: FastAPI):
    """
    This function runs once when the app starts and once when it shuts down.

    Why:
    - We want a SINGLE httpx.AsyncCLient taht's reused for all outgoing HTTP calls.
    - Reuse enables connection pooling (faster, fewer handshakes).
    - We put it on app.state so any request/route can access it via a dependency. 
    """
    timeout = httpx.Timeout(connect=5.0, read=20.0, write=10.0, pool=5.0)

    # limits to prevent too many simultaneous sockets 
    limits = httpx.Limits(
        max_connections=100, 
        max_keepalive_connections=20, 
        keepalive_expiry=60.0
    )

    # Create ONE AsyncClient for the entire app lifetime and store it. 
    app.state.http_client = httpx.AsyncClient(timeout=timeout, limits=limits)

    try:
        # Yield control back to FastAPI - app runs here. 
        yield 
    
    finally: 
        # On shutdown, close the client cleanly (flush + close sockets)
        await app.state.http_client.aclose()

def create_app() -> FastAPI:
    app = FastAPI(title="Hutbite Backend", lifespan=lifespan)
    app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET, same_site="lax")

    install_error_handlers(app)

    app.include_router(auth.router)
    app.include_router(orders.router)
    app.include_router(catalog.router)
    app.include_router(deliverability.router)
    app.include_router(sms.router)
    # app.include(tables.router)
    app.include_router(ultimago.router)

    return app

app = create_app()
