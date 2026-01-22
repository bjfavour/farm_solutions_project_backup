from rest_framework import viewsets, status
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import AnimalType, Batch, Expense, FeedingRecord, MortalityRecord, ShopItem
from .serializers import (AnimalTypeSerializer, BatchSerializer, ExpenseSerializer,
                          FeedingRecordSerializer, MortalityRecordSerializer, ShopItemSerializer,RegisterSerializer)
from .permissions import IsStaffOrAdmin

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AnimalTypeViewSet(viewsets.ModelViewSet):
    queryset = AnimalType.objects.all()
    serializer_class = AnimalTypeSerializer
    permission_classes = [IsAdminUser]

class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all().order_by('-arrival_date')
    serializer_class = BatchSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def expense(self, request, pk=None):
        batch = self.get_object()
        data = request.data.copy()
        data['batch'] = batch.pk
        serializer = ExpenseSerializer(data=data)
        if serializer.is_valid():
            serializer.save(recorded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def feeding(self, request, pk=None):
        batch = self.get_object()
        data = request.data.copy()
        data['batch'] = batch.pk
        serializer = FeedingRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save(recorded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def mortality(self, request, pk=None):
        batch = self.get_object()
        data = request.data.copy()
        data['batch'] = batch.pk
        serializer = MortalityRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()  # approval happens separately
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminUser])
    def move_to_shop(self, request, pk=None):
        batch = self.get_object()
        try:
            with transaction.atomic():
                batch.move_to_shop(by_user=request.user)
            return Response({'detail':'moved to shop','locked_unit_cost':str(batch.locked_unit_cost)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class MortalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MortalityRecord.objects.all().order_by('-created_at')
    serializer_class = MortalityRecordSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        mr = get_object_or_404(MortalityRecord, pk=pk)
        try:
            with transaction.atomic():
                mr.approve(request.user)
            return Response({'detail':'approved'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail':str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ShopItemViewSet(viewsets.ModelViewSet):
    queryset = ShopItem.objects.all()
    serializer_class = ShopItemSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminUser])
    def set_price(self, request, pk=None):
        item = self.get_object()
        price = request.data.get('selling_price_per_unit')
        try:
            price_dec = float(price)
        except Exception:
            return Response({'detail':'invalid price'}, status=400)
        # basic validation: cannot set price <= locked_unit_cost
        if item.batch.locked_unit_cost is not None and price_dec <= float(item.batch.locked_unit_cost):
            return Response({'detail':'selling price must be greater than locked unit cost'}, status=400)
        item.selling_price_per_unit = price_dec
        item.save()
        return Response({'detail':'price set','selling_price_per_unit':item.selling_price_per_unit})
