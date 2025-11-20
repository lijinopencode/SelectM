from django.contrib import admin
from .models import Category, DataRecord


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "created_at")
    search_fields = ("name",)


@admin.register(DataRecord)
class DataRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "data_name", "record_date", "data_value", "updated_at")
    list_filter = ("category", "record_date")  # 筛选器
    search_fields = ("data_name",)
    date_hierarchy = "record_date"  # 按日期层级筛选