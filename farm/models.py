from django.db import models, transaction
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class AnimalType(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Batch(models.Model):
    animal = models.ForeignKey(AnimalType, on_delete=models.PROTECT, related_name='batches')
    arrival_date = models.DateField()
    serial_number = models.CharField(max_length=50, unique=True, blank=True)
    initial_quantity = models.PositiveIntegerField()
    current_quantity = models.IntegerField(null=True, blank=True)
    is_moved_to_shop = models.BooleanField(default=False)

    locked_total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    locked_unit_cost = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)

    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.serial_number:
            day = self.arrival_date.strftime('%Y%m%d')
            self.serial_number = f"BATCH-{day}-{self.initial_quantity}"

        if self.current_quantity is None:
            self.current_quantity = self.initial_quantity

        super().save(*args, **kwargs)

    def total_expenses(self):
        return self.expenses.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    def total_feed(self):
        return self.feeding_records.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

    @property
    def total_cost(self):
        return self.total_expenses() + self.total_feed()

    @property
    def unit_cost(self):
        qty = self.current_quantity or 1
        return (self.total_cost / Decimal(qty)).quantize(Decimal("0.0001"))

    @transaction.atomic
    def move_to_shop(self, by_user=None):
        if self.is_moved_to_shop:
            raise ValueError("Batch already moved to shop")

        b = Batch.objects.select_for_update().get(pk=self.pk)

        b.locked_total_cost = self.total_cost
        b.locked_unit_cost = self.unit_cost
        b.is_moved_to_shop = True

        if by_user:
            b.created_by = by_user
        b.save()


class Expense(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    recorded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class FeedingRecord(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='feeding_records')
    bags = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)


class MortalityRecord(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='mortalities')
    count = models.PositiveIntegerField()
    reason = models.CharField(max_length=255, blank=True)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='approved_mortalities'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    @transaction.atomic
    def approve(self, approver):
        print(">>> APPROVE METHOD CALLED for record ID:", self.id, "count=", self.count)

        mr = MortalityRecord.objects.select_for_update().get(pk=self.pk)
        print(">>> Loaded MR from DB. Approved =", mr.approved)

        if mr.approved:
            print(">>> Already approved. EXITING")
            return

        batch = Batch.objects.select_for_update().get(pk=mr.batch_id)

        print(">>> Batch before:", batch.current_quantity)

        new_qty = (batch.current_quantity or 0) - mr.count
        batch.current_quantity = max(0, new_qty)

        print(">>> Batch after:", batch.current_quantity)

        mr.approved = True
        mr.approved_by = approver

        batch.save(update_fields=['current_quantity'])
        mr.save(update_fields=['approved', 'approved_by'])


class ShopItem(models.Model):
    batch = models.OneToOneField(Batch, on_delete=models.CASCADE, related_name='shop_item')
    selling_price_per_unit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
