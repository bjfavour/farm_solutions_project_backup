from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import AnimalType, Batch, Expense, MortalityRecord

User = get_user_model()

class BasicModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('u','u@example.com','pass')
        self.admin = User.objects.create_superuser('admin','a@a.com','pass')
        self.at = AnimalType.objects.create(code='fish', name='Fish')
    def test_batch_create_and_move(self):
        b = Batch.objects.create(animal=self.at, arrival_date='2025-11-20', initial_quantity=10, created_by=self.user)
        Expense.objects.create(batch=b, description='feed', amount='100.00', recorded_by=self.user)
        # move to shop
        b.move_to_shop(by_user=self.admin)
        self.assertTrue(b.is_moved_to_shop)
        self.assertIsNotNone(b.locked_unit_cost)
    def test_mortality_approve(self):
        b = Batch.objects.create(animal=self.at, arrival_date='2025-11-20', initial_quantity=10, created_by=self.user)
        mr = MortalityRecord.objects.create(batch=b, count=2)
        mr.approve(self.admin)
        b.refresh_from_db()
        self.assertEqual(b.current_quantity, 8)
