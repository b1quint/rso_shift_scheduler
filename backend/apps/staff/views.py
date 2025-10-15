from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import StaffMember, StaffAvailability
from .serializers import (
    StaffMemberSerializer,
    StaffMemberCreateSerializer,
    StaffAvailabilitySerializer
)


class StaffMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StaffMember CRUD operations
    """
    queryset = StaffMember.objects.select_related('user').all()
    serializer_class = StaffMemberSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status', 'prefers_night_shifts']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'user__email']
    ordering_fields = ['hire_date', 'user__last_name']
    ordering = ['user__last_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StaffMemberCreateSerializer
        return StaffMemberSerializer


class StaffAvailabilityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StaffAvailability CRUD operations
    """
    queryset = StaffAvailability.objects.select_related('staff_member__user').all()
    serializer_class = StaffAvailabilitySerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['staff_member', 'availability_type', 'start_date']
    ordering_fields = ['start_date']
    ordering = ['start_date']
