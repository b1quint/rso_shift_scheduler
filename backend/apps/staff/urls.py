from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TeamViewSet,
    ShiftTypeViewSet,
    StaffMemberViewSet,
    StaffAvailabilityViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'shift-types', ShiftTypeViewSet, basename='shift-type')
router.register(r'members', StaffMemberViewSet, basename='staff-member')
router.register(r'availability', StaffAvailabilityViewSet, basename='staff-availability')

urlpatterns = [
    path('', include(router.urls)),
]
