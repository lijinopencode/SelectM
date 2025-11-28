from django.contrib import admin
from .models import Category, DataRecord, Website  # 添加Website导入

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url", "description", "created_at")
    search_fields = ("name", "url")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "website", "description", "created_at")  # 添加website字段
    search_fields = ("name",)

@admin.register(DataRecord)
class DataRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "data_name", "category", "start_date", "end_date")
    search_fields = ("data_name",)
    date_hierarchy = "start_date"  # 按日期层级筛选