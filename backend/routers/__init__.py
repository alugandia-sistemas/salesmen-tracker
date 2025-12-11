# ==============================================================================
# ROUTERS - Exportación centralizada de routers FastAPI
# ==============================================================================

from .clients import router as clients_router
from .sellers import router as sellers_router
from .routes import router as routes_router
from .visits import router as visits_router
from .zones import router as zones_router
from .opportunities import router as opportunities_router
from .auth import router as auth_router

__all__ = [
    "clients_router",
    "sellers_router",
    "routes_router",
    "visits_router",
    "zones_router",
    "opportunities_router",
    "auth_router"
]
