# ==============================================================================
# MODELS - Exportación centralizada de modelos SQLAlchemy
# ==============================================================================

from .client import Client
from .seller import Seller
from .route import Route
from .visit import Visit
from .zone import Zone
from .opportunity import Opportunity

__all__ = [
    "Client",
    "Seller", 
    "Route",
    "Visit",
    "Zone",
    "Opportunity"
]
