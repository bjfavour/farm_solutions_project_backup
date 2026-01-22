from rest_framework import serializers
from .models import AnimalType, Batch, Expense, FeedingRecord, MortalityRecord, ShopItem
from django.contrib.auth.models import User


# ===========================
# ANIMAL TYPE
# ===========================
class AnimalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalType
        fields = ['id', 'code', 'name']


# ===========================
# EXPENSE
# ===========================
class ExpenseSerializer(serializers.ModelSerializer):
    recorded_by = serializers.ReadOnlyField(source='recorded_by.username')

    class Meta:
        model = Expense
        fields = ['id', 'batch', 'description', 'amount', 'recorded_by', 'created_at']


# ===========================
# FEEDING
# ===========================
class FeedingRecordSerializer(serializers.ModelSerializer):
    recorded_by = serializers.ReadOnlyField(source='recorded_by.username')

    class Meta:
        model = FeedingRecord
        fields = ['id', 'batch', 'bags', 'amount', 'note', 'recorded_by', 'created_at']


# ===========================
# MORTALITY
# ===========================
class MortalityRecordSerializer(serializers.ModelSerializer):
    approved_by = serializers.ReadOnlyField(source='approved_by.username')
    approved = serializers.ReadOnlyField()

    class Meta:
        model = MortalityRecord
        fields = [
            'id', 'batch', 'count', 'reason',
            'approved', 'approved_by', 'created_at'
        ]


# ===========================
# SHOP ITEM
# ===========================
class ShopItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopItem
        fields = ['id', 'batch', 'selling_price_per_unit', 'created_at']


# ===========================
# BATCH (MAIN SERIALIZER)
# ===========================
class BatchSerializer(serializers.ModelSerializer):
    # Relationships
    animal = AnimalTypeSerializer(read_only=True)
    animal_id = serializers.PrimaryKeyRelatedField(
        queryset=AnimalType.objects.all(),
        source='animal',
        write_only=True
    )
    animal_name = serializers.CharField(source='animal.name', read_only=True)

    # Computed fields
    total_expenses = serializers.SerializerMethodField()
    total_feed = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()

    class Meta:
        model = Batch
        fields = [
            'id', 'animal', 'animal_id', 'animal_name',
            'arrival_date', 'serial_number',
            'initial_quantity', 'current_quantity',
            'is_moved_to_shop',
            'total_expenses', 'total_feed', 'total_cost', 'unit_cost',
            'created_at'
        ]

        read_only_fields = [
            'serial_number',
            'current_quantity',
            'created_at'
        ]

    # ---------- COMPUTED VALUES ----------
    def get_total_expenses(self, obj):
        return obj.total_expenses()

    def get_total_feed(self, obj):
        return obj.total_feed()

    def get_total_cost(self, obj):
        return obj.total_cost

    def get_unit_cost(self, obj):
        return obj.unit_cost
    
    
# ===========================
# USER REGISTRATION
# ===========================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
