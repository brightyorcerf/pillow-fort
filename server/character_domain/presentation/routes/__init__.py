from .character_routes import router as character_router
from .internal_routes import router as internal_router
from .purchase_routes import router as purchase_router

__all__ = ["character_router", "internal_router", "purchase_router"]
