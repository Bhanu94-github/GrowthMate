from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView # For serving index.html
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.api_urls')), # Include your API endpoints

    # Catch-all for React app:
    # This serves the React app's index.html for all non-API routes.
    # React Router will then take over for client-side routing.
    # Ensure 'index.html' is in one of your TEMPLATES DIRS.
    re_path(r'^.*', TemplateView.as_view(template_name='index.html')),
]

# Serve static files in development (Django's built-in staticfiles app)
# In production, WhiteNoise handles this.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)