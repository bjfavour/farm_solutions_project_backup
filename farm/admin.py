from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html

from .models import AnimalType, Batch, Expense, FeedingRecord, MortalityRecord, ShopItem


# ============================
# INLINE TABLES
# ============================

class ExpenseInline(admin.TabularInline):
    model = Expense
    extra = 0
    fields = ('description', 'amount', 'recorded_by', 'created_at')
    readonly_fields = ('recorded_by', 'created_at')


class FeedingInline(admin.TabularInline):
    model = FeedingRecord
    extra = 0
    fields = ('bags', 'amount', 'note', 'recorded_by', 'created_at')
    readonly_fields = ('recorded_by', 'created_at')


class MortalityInline(admin.TabularInline):
    model = MortalityRecord
    extra = 0
    fields = ('count', 'reason', 'approved', 'approved_by', 'created_at')
    readonly_fields = ('approved', 'approved_by', 'created_at')
    can_delete = False     # Prevent admin from bypassing logic


# ============================
# ACTIONS
# ============================

@admin.action(description="Approve selected mortalities")
def approve_mortalities(modeladmin, request, queryset):
    for m in queryset:
        m.approve(request.user)


@admin.action(description="Move selected batches to shop")
def move_batches_to_shop(modeladmin, request, queryset):
    for b in queryset:
        b.move_to_shop(by_user=request.user)


# ============================
# BATCH ADMIN
# ============================

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = (
        'serial_number', 'animal', 'arrival_date',
        'initial_quantity', 'current_quantity',
        'is_moved_to_shop', 'view_report_button'
    )

    inlines = [ExpenseInline, FeedingInline, MortalityInline]

    # 👉 IMPORTANT: ONLY batch-related actions here
    # (Do NOT put approve_mortalities here, queryset is Batch, not MortalityRecord)
    actions = [move_batches_to_shop]

    def view_report_button(self, obj):
        return format_html('<a class="button" href="{}">View Report</a>', f'./{obj.id}/report/')
    view_report_button.short_description = "Batch Report"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:batch_id>/report/',
                self.admin_site.admin_view(self.batch_report_view),
                name='batch-report'
            )
        ]
        return custom_urls + urls

    def batch_report_view(self, request, batch_id):
        batch = Batch.objects.get(pk=batch_id)

        context = {
            'batch': batch,
            'expenses': batch.expenses.all(),
            'feedings': batch.feeding_records.all(),
            'mortalities': batch.mortalities.all(),

            'total_expenses': batch.total_expenses(),
            'total_feed': batch.total_feed(),
            'total_cost': batch.total_cost,
            'unit_cost': batch.unit_cost,

            'title': f"Report for {batch.serial_number}"
        }

        return render(request, 'admin/batch_report.html', context)


# ============================
# REGISTER OTHER MODELS
# ============================

@admin.register(AnimalType)
class AnimalTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('batch', 'description', 'amount', 'recorded_by', 'created_at')


@admin.register(FeedingRecord)
class FeedingAdmin(admin.ModelAdmin):
    list_display = ('batch', 'bags', 'amount', 'note', 'recorded_by', 'created_at')


@admin.register(MortalityRecord)
class MortalityAdmin(admin.ModelAdmin):
    list_display = ('batch', 'count', 'reason', 'approved', 'approved_by', 'created_at')
    actions = [approve_mortalities]

    # You can still edit count/reason normally; approval is done via action only
    readonly_fields = ('approved', 'approved_by', 'created_at')


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('batch', 'selling_price_per_unit', 'created_at')
