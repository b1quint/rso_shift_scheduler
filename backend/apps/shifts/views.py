from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Shift, Schedule
from .serializers import (
    ShiftSerializer,
    ShiftListSerializer,
    ScheduleSerializer,
    ScheduleListSerializer
)


class ShiftViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Shift CRUD operations
    """
    queryset = Shift.objects.select_related(
        'assigned_staff__user',
        'telescope',
        'created_by'
    ).all()
    serializer_class = ShiftSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['shift_type', 'status', 'assigned_staff', 'telescope']
    search_fields = ['description', 'assigned_staff__user__first_name', 'assigned_staff__user__last_name']
    ordering_fields = ['start_time', 'shift_type']
    ordering = ['start_time']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ShiftListSerializer
        return ShiftSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Schedule CRUD operations
    """
    queryset = Schedule.objects.prefetch_related('shifts').all()
    serializer_class = ScheduleSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['start_date', 'name']
    ordering = ['-start_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ScheduleListSerializer
        return ScheduleSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
