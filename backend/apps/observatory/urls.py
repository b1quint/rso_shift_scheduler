from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TelescopeViewSet, InstrumentViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'telescopes', TelescopeViewSet, basename='telescope')
router.register(r'instruments', InstrumentViewSet, basename='instrument')

urlpatterns = [
    path('', include(router.urls)),
]
