# ==============================================================================
# MODELS - Exportación centralizada de modelos SQLAlchemy
# ==============================================================================

from models.client import Client
from models.seller import Seller
from models.route import Route
from models.visit import Visit
from models.zone import Zone
from models.opportunity import Opportunity

__all__ = [
    "Client",
    "Seller", 
    "Route",
    "Visit",
    "Zone",
    "Opportunity"
]
