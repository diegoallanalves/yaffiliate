from app.bootstrap import bootstrap_app
from app.components.layout import sidebar_navigation
from app.router import render_route
bootstrap_app(); render_route(sidebar_navigation())
