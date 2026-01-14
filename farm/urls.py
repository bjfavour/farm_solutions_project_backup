from rest_framework.routers import DefaultRouter
from django.urls import path, include
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import AnimalTypeViewSet, BatchViewSet, MortalityViewSet, ShopItemViewSet, RegisterAPIView


router = DefaultRouter()
router.register(r'animal-types', AnimalTypeViewSet)
router.register(r'batches', BatchViewSet)
router.register(r'mortalities', MortalityViewSet, basename='mortality')
router.register(r'shop', ShopItemViewSet, basename='shop')

urlpatterns = [
    path('admin/', admin.site.urls),

    # router endpoints
    path('', include(router.urls)),

    # registration
    path('register/', RegisterAPIView.as_view(), name='register'),

    # JWT authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
