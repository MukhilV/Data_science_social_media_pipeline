from .reddit_routes import reddit_bp
from .chan_routes import chan_bp
from .inter_platform_routes import inter_platform_bp

# Export all blueprints so they can be imported from the routes package
__all__ = ["reddit_bp", "chan_bp", "inter_platform_bp"]