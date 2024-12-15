from flask import Flask

# Register routes
from .routes.reddit_routes import reddit_bp
from .routes.chan_routes import chan_bp
from .routes.inter_platform_routes import inter_platform_bp

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(reddit_bp, url_prefix="/reddit")
    app.register_blueprint(chan_bp, url_prefix="/4chan")
    app.register_blueprint(inter_platform_bp, url_prefix="/inter_platform")

    return app
