from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
import datetime  # 添加datetime模块导入
from .utils import parse_number_group  # 添加这个导入

# 添加Website模型
class Website(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="网站名称")
    url = models.URLField(max_length=255, blank=True, null=True, verbose_name="网站URL")
    description = models.TextField(blank=True, null=True, verbose_name="网站描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "数据来源网站"
        verbose_name_plural = "数据来源网站"
        ordering = ["-id"]

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="类别名称")
    description = models.TextField(blank=True, null=True, verbose_name="类别描述")
    # 添加website外键字段
    website = models.ForeignKey(
        Website, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="categories",
        verbose_name="数据来源网站"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "数据类别"
        verbose_name_plural = "数据类别"
        ordering = ["-id"]


# 在DataRecord模型中添加parsed_numbers字段
class DataRecord(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name="data_records",
        verbose_name="所属类别"
    )
    data_name = models.CharField(max_length=100, verbose_name="数据名字")
    # 替换record_date为start_date和end_date
    start_date = models.DateField(verbose_name="开始日期", default=datetime.date.today)
    end_date = models.DateField(verbose_name="结束日期", blank=True, null=True)
    # 将JSONField改为TextField以支持任意字符串输入
    data_value = models.TextField(verbose_name="数据内容", blank=True, null=True)
    # 新增parsed_numbers字段，用于存储解析出的数字列表
    parsed_numbers = models.JSONField(verbose_name="解析后的数字", blank=True, null=True)
    # 新增is_excluded_group字段，用于标记是否属于被排除的组
    is_excluded_group = models.BooleanField(verbose_name="是否属于被排除的组", default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        if self.end_date:
            return f"{self.data_name}（{self.start_date} 至 {self.end_date}）"
        else:
            return f"{self.data_name}（{self.start_date} 起）"

    class Meta:
        verbose_name = "数据记录"
        verbose_name_plural = "数据记录"
        ordering = ["-start_date", "data_name"]
        unique_together = ["category", "data_name", "start_date"]  # 更新唯一性约束

# 添加DataRecord的信号接收器，用于自动解析数字
@receiver(pre_save, sender=DataRecord)
def set_default_parsed_numbers_data_record(sender, instance, **kwargs):
    # 如果parsed_numbers为None，初始化为空列表
    if instance.parsed_numbers is None:
        instance.parsed_numbers = []
    
    # 自动解析data_value中的数字，更新parsed_numbers
    if instance.data_value and instance.data_value.strip():
        try:
            # 使用parse_number_group函数解析数字
            numbers = parse_number_group(instance.data_value)
            if numbers:
                instance.parsed_numbers = numbers
        except Exception:
            # 如果解析失败，保持原有值或空列表
            pass


class DailyNumber(models.Model):
    """每日数字记录模型"""
    date = models.DateField(verbose_name="日期", unique=True)
    hit_number = models.CharField(max_length=255, verbose_name="命中数字")  
    hit_time = models.TimeField(verbose_name="命中时间")
    opened_number = models.IntegerField(verbose_name="开出数字", blank=True, null=True)  
    parsed_numbers = models.JSONField(verbose_name="解析后的数字", blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"{self.date} - {self.hit_number}"

    class Meta:
        verbose_name = "每日数字记录"
        verbose_name_plural = "每日数字记录"
        ordering = ["-date"]


        
@receiver(pre_save, sender=DailyNumber)
def set_default_parsed_numbers(sender, instance, **kwargs):
    if instance.parsed_numbers is None:
        instance.parsed_numbers = []