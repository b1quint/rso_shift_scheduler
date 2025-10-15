from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Team, ShiftType, StaffMember, StaffAvailability, DailyAvailability
from .serializers import (
    TeamSerializer,
    ShiftTypeSerializer,
    StaffMemberSerializer,
    StaffMemberCreateSerializer,
    StaffAvailabilitySerializer,
    DailyAvailabilitySerializer
)
from .pagination import LargeResultsSetPagination


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Team read-only operations
    """
    queryset = Team.objects.filter(is_active=True)
    serializer_class = TeamSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing


class ShiftTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ShiftType read-only operations
    """
    queryset = ShiftType.objects.filter(is_active=True).select_related('team')
    serializer_class = ShiftTypeSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['team']


class StaffMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StaffMember CRUD operations
    """
    queryset = StaffMember.objects.select_related('user', 'team').all()
    serializer_class = StaffMemberSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status', 'prefers_night_shifts', 'team']
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


class DailyAvailabilityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DailyAvailability CRUD operations
    """
    queryset = DailyAvailability.objects.select_related('staff_member__user').all()
    serializer_class = DailyAvailabilitySerializer
    pagination_class = LargeResultsSetPagination  # Allow large page sizes for calendar view
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['staff_member', 'date', 'availability_code']
    ordering_fields = ['date', 'staff_member']
    ordering = ['date', 'staff_member']
