from django.urls import path
from . import views

urlpatterns = [
    # 首页
    path("", views.index, name="index"),

    # 类别管理
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/add/", views.CategoryCreateView.as_view(), name="category_add"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),

    # 数据记录管理
    path("records/", views.DataRecordListView.as_view(), name="data_record_list"),
    path("records/add/", views.DataRecordCreateView.as_view(), name="data_record_add"),
    path("records/<int:pk>/edit/", views.DataRecordUpdateView.as_view(), name="data_record_edit"),
    path("records/<int:pk>/delete/", views.DataRecordDeleteView.as_view(), name="data_record_delete"),

    # 每日数字记录管理
    path("daily-numbers/", views.DailyNumberListView.as_view(), name="daily_number_list"),
    path("daily-numbers/add/", views.DailyNumberCreateView.as_view(), name="daily_number_add"),
    path("daily-numbers/<int:pk>/edit/", views.DailyNumberUpdateView.as_view(), name="daily_number_edit"),
    path("daily-numbers/<int:pk>/delete/", views.DailyNumberDeleteView.as_view(), name="daily_number_delete"),
    
    # 数字对比工具
    # 在urlpatterns列表末尾添加
    path("number-comparison/", views.NumberComparisonView.as_view(), name="number_comparison"),

    # API接口
    path("api/preset-data-groups/", views.get_preset_data_groups, name="api_preset_data_groups"),
    # 添加新的API路由
    path('api/records-by-date/', views.get_records_by_date, name='get_records_by_date'),
]