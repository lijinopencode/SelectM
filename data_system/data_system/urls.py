from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("records.urls")),  # 包含应用URL
]

# 配置静态文件访问
urlpatterns += staticfiles_urlpatterns()