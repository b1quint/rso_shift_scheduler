from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Telescope, Instrument
from .serializers import TelescopeSerializer, InstrumentSerializer, TelescopeListSerializer


class TelescopeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Telescope CRUD operations
    """
    queryset = Telescope.objects.prefetch_related('instruments').all()
    serializer_class = TelescopeSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'aperture']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TelescopeListSerializer
        return TelescopeSerializer


class InstrumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Instrument CRUD operations
    """
    queryset = Instrument.objects.select_related('telescope').all()
    serializer_class = InstrumentSerializer
    # permission_classes = [IsAuthenticated]  # Temporarily disabled for testing
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['telescope', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name']
    ordering = ['telescope__name', 'name']
