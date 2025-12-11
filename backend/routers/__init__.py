# ==============================================================================
# ROUTERS - Exportación centralizada de routers FastAPI
# ==============================================================================

from routers.clients import router as clients_router
from routers.sellers import router as sellers_router
from routers.routes import router as routes_router
from routers.visits import router as visits_router
from routers.zones import router as zones_router
from routers.opportunities import router as opportunities_router
from routers.auth import router as auth_router

__all__ = [
    "clients_router",
    "sellers_router",
    "routes_router",
    "visits_router",
    "zones_router",
    "opportunities_router",
    "auth_router"
]
