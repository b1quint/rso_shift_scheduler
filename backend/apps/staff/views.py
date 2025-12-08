from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Team, ShiftType, StaffMember, StaffAvailability, DailyAvailability
from .serializers import (
    TeamSerializer,
    ShiftTypeSerializer,
    StaffMemberSerializer,
    StaffMemberCreateSerializer,
    StaffMemberUpdateSerializer,
    StaffAvailabilitySerializer,
    DailyAvailabilitySerializer
)
from .pagination import LargeResultsSetPagination


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Team CRUD operations.
    Supports creating, reading, updating, and deleting teams.
    
    Note: Returns all teams (active and inactive) to allow management
    of inactive teams. Use ?is_active=true query param to filter for active only.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ShiftTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ShiftType CRUD operations.
    Supports creating, reading, updating, and deleting shift types.
    
    Note: Returns all shift types (active and inactive) to allow management
    of inactive shift types. Use ?is_active=true query param to filter for active only.
    """
    queryset = ShiftType.objects.all().select_related('team')
    serializer_class = ShiftTypeSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['team', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['team', 'sort_order']


class StaffMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for StaffMember CRUD operations
    """
    queryset = StaffMember.objects.select_related('user', 'team').all()
    serializer_class = StaffMemberSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status', 'prefers_night_shifts', 'team', 'team__name']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id', 'user__email']
    ordering_fields = ['hire_date', 'user__last_name']
    ordering = ['user__last_name']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StaffMemberCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StaffMemberUpdateSerializer
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
