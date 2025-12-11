# ==============================================================================
# SCHEMAS - Exportación centralizada de schemas Pydantic
# ==============================================================================

from .client import (
    ClientBase, ClientCreate, ClientUpdate, ClientResponse,
    ClientListResponse, ClientSearchResponse
)
from .seller import (
    SellerBase, SellerCreate, SellerLogin, SellerResponse,
    SellerLoginResponse
)
from .route import (
    RouteBase, RouteCreate, RouteUpdate, RouteResponse,
    RouteListResponse, RouteWithClient
)
from .visit import (
    VisitBase, CheckinRequest, CheckoutRequest, VisitResponse,
    VisitListResponse, VisitStats
)
from .zone import (
    ZoneBase, ZoneCreate, ZoneUpdate, ZoneResponse
)
from .opportunity import (
    OpportunityBase, OpportunityCreate, OpportunityUpdate, OpportunityResponse
)

__all__ = [
    # Client
    "ClientBase", "ClientCreate", "ClientUpdate", "ClientResponse",
    "ClientListResponse", "ClientSearchResponse",
    # Seller
    "SellerBase", "SellerCreate", "SellerLogin", "SellerResponse",
    "SellerLoginResponse",
    # Route
    "RouteBase", "RouteCreate", "RouteUpdate", "RouteResponse",
    "RouteListResponse", "RouteWithClient",
    # Visit
    "VisitBase", "CheckinRequest", "CheckoutRequest", "VisitResponse",
    "VisitListResponse", "VisitStats",
    # Zone
    "ZoneBase", "ZoneCreate", "ZoneUpdate", "ZoneResponse",
    # Opportunity
    "OpportunityBase", "OpportunityCreate", "OpportunityUpdate", "OpportunityResponse"
]
