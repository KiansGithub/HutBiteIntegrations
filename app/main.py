from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core.errors import install_error_handlers
from app.routers import auth, orders, catalog, deliverability

def create_app() -> FastAPI:
    app = FastAPI(title="HubRise Orders Proxy")
    app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET, same_site="lax")

    install_error_handlers(app)

    app.include_router(auth.router)
    app.include_router(orders.router)
    app.include_router(catalog.router)
    app.include_router(deliverability.router)

    return app

app = create_app()
