# 正确的导入位置应该在文件顶部
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
# 在文件顶部添加datetime导入（如果还没有）
from datetime import date, datetime
from .models import Category, DataRecord, DailyNumber
from .forms import CategoryForm, DataRecordForm, DailyNumberForm
# 导入生肖相关函数 - 正确放在顶部
from .utils import get_zodiac_by_number, get_numbers_by_zodiac, CHINESE_ZODIAC_MAP, get_numbers_with_zodiac


# 首页
def index(request):
    return render(request, "records/index.html")


# 类别管理
class CategoryListView(ListView):
    model = Category
    template_name = "records/category_list.html"
    context_object_name = "categories"


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "records/category_form.html"
    success_url = reverse_lazy("category_list")
    success_message = "类别添加成功！"


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "records/category_form.html"
    success_url = reverse_lazy("category_list")
    success_message = "类别更新成功！"


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "records/category_confirm_delete.html"
    success_url = reverse_lazy("category_list")
    success_message = "类别删除成功！"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# 数据记录管理
class DataRecordListView(ListView):
    model = DataRecord
    template_name = "records/data_record_list.html"
    context_object_name = "records"

    def get_queryset(self):
        """带筛选条件的查询"""
        queryset = super().get_queryset().select_related("category")
        category_id = self.request.GET.get("category_id")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if start_date:
            queryset = queryset.filter(record_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(record_date__lte=end_date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()  # 用于筛选下拉框
        
        # 获取查询集中所有记录的日期，然后获取对应的DailyNumber
        records = context.get('records', [])
        # 使用字典存储日期到DailyNumber的映射
        date_to_daily_number = {}
        
        # 提取所有不重复的日期
        dates = set()
        for record in records:
            dates.add(record.record_date)
            # 预处理：为每个记录添加带生肖的数字列表
            if hasattr(record, 'parsed_numbers') and record.parsed_numbers:
                # 使用get_numbers_with_zodiac函数处理
                record.numbers_with_zodiac = get_numbers_with_zodiac(record.parsed_numbers)
            else:
                record.numbers_with_zodiac = []
        
        # 如果有日期，则获取对应的DailyNumber记录
        if dates:
            daily_numbers = DailyNumber.objects.filter(date__in=dates)
            # 填充映射字典
            for dn in daily_numbers:
                date_to_daily_number[dn.date] = dn
                # 为DailyNumber添加生肖信息
                if hasattr(dn, 'opened_number') and dn.opened_number:
                    dn.opened_number_zodiac = get_zodiac_by_number(dn.opened_number)
        
        # 将映射字典添加到上下文
        context["date_to_daily_number"] = date_to_daily_number
        
        # 添加生肖列表到上下文用于筛选
        context["chinese_zodiacs"] = list(CHINESE_ZODIAC_MAP.keys())
        
        return context


class DataRecordCreateView(CreateView):
    model = DataRecord
    form_class = DataRecordForm
    template_name = "records/data_record_form.html"
    success_url = reverse_lazy("data_record_list")
    success_message = "数据添加成功！"

    def form_valid(self, form):
        # 确保data_value被正确设置
        self.object = form.save(commit=False)
        # 将默认值从空字典改为空字符串
        self.object.data_value = form.cleaned_data.get("data_value", "")
        self.object.save()
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class DataRecordUpdateView(UpdateView):
    model = DataRecord
    form_class = DataRecordForm
    template_name = "records/data_record_form.html"
    success_url = reverse_lazy("data_record_list")
    success_message = "数据更新成功！"

    def form_valid(self, form):
        # 确保data_value被正确更新
        self.object = form.save(commit=False)
        # 将默认值从空字典改为空字符串
        self.object.data_value = form.cleaned_data.get("data_value", "")
        self.object.save()
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class DataRecordDeleteView(DeleteView):
    model = DataRecord
    template_name = "records/data_record_confirm_delete.html"
    success_url = reverse_lazy("data_record_list")
    success_message = "数据删除成功！"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# 每日数字记录管理
class DailyNumberListView(ListView):
    model = DailyNumber
    template_name = "records/daily_number_list.html"
    context_object_name = "daily_numbers"
    paginate_by = 20


class DailyNumberCreateView(CreateView):
    model = DailyNumber
    form_class = DailyNumberForm
    template_name = "records/daily_number_form.html"
    success_url = reverse_lazy("daily_number_list")
    success_message = "每日数字记录添加成功！"

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def get_initial(self):
        """设置表单初始值"""
        initial = super().get_initial()
        from datetime import date, datetime
        initial['date'] = date.today().strftime('%Y-%m-%d')
        initial['hit_time'] = datetime.now().strftime('%H:%M')
        initial['opened_number'] = '0'
        return initial


class DailyNumberUpdateView(UpdateView):
    model = DailyNumber
    form_class = DailyNumberForm
    template_name = "records/daily_number_form.html"
    success_url = reverse_lazy("daily_number_list")
    success_message = "每日数字记录更新成功！"

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_valid(form)


class DailyNumberDeleteView(DeleteView):
    model = DailyNumber
    template_name = "records/daily_number_confirm_delete.html"
    success_url = reverse_lazy("daily_number_list")
    success_message = "每日数字记录删除成功！"

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# 在文件末尾添加NumberComparisonView类
# 数字对比工具视图
class NumberComparisonView(ListView):
    model = DataRecord
    template_name = "records/number_comparison.html"
    context_object_name = "comparison_records"

    def get_queryset(self):
        """获取指定日期的数据记录"""
        # 获取请求的日期，如果没有则使用今天
        comparison_date_str = self.request.GET.get('date')
        if comparison_date_str:
            try:
                comparison_date = datetime.strptime(comparison_date_str, '%Y-%m-%d').date()
            except ValueError:
                comparison_date = date.today()
        else:
            comparison_date = date.today()
        
        # 获取该日期的所有数据记录
        queryset = DataRecord.objects.filter(record_date=comparison_date).select_related('category')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # 获取比较日期
        comparison_date_str = self.request.GET.get('date')
        if comparison_date_str:
            try:
                comparison_date = datetime.strptime(comparison_date_str, '%Y-%m-%d').date()
            except ValueError:
                comparison_date = date.today()
        else:
            comparison_date = date.today()
        
        # 将日期格式化为字符串供表单使用
        context['selected_date'] = comparison_date.strftime('%Y-%m-%d')
        
        # 按is_excluded_group分组数据
        records = self.get_queryset()
        
        # 排除列表（is_excluded_group=True）
        excluded_records = list(records.filter(is_excluded_group=True))  # 转换为列表
        # 对比列表（is_excluded_group=False）
        comparison_records = list(records.filter(is_excluded_group=False))  # 转换为列表
        
        # 导入必要的函数
        from .utils import parse_number_group, get_numbers_with_zodiac
        
        # 处理所有记录的数字
        for record in excluded_records + comparison_records:
            # 强制从data_value解析数字
            numbers_list = []
            if record.data_value:
                # 直接解析data_value
                numbers_list = parse_number_group(record.data_value)
                # 添加调试信息
                print(f"Record {record.id} - Parsed numbers: {numbers_list}")
            
            # 确保是列表
            if not isinstance(numbers_list, list):
                numbers_list = []
            
            # 生成带生肖的数字列表
            numbers_with_zodiac = get_numbers_with_zodiac(numbers_list)
            print(f"Record {record.id} - Numbers with zodiac: {numbers_with_zodiac}")
            
            # 直接设置属性
            record.numbers_with_zodiac = numbers_with_zodiac
        
        # 添加到上下文
        context['excluded_records'] = excluded_records
        context['comparison_records'] = comparison_records
        
        # 获取该日期的每日数字记录（如果存在）
        try:
            daily_number = DailyNumber.objects.get(date=comparison_date)
            # 确保opened_number是字符串
            if daily_number.opened_number is not None:
                daily_number.opened_number = str(daily_number.opened_number)
                from .utils import get_zodiac_by_number
                daily_number.opened_number_zodiac = get_zodiac_by_number(daily_number.opened_number)
            context['daily_number'] = daily_number
        except DailyNumber.DoesNotExist:
            context['daily_number'] = None
        
        # 获取选中的记录ID
        context['selected_excluded_ids'] = self.request.GET.getlist('excluded_ids')
        context['selected_comparison_ids'] = self.request.GET.getlist('comparison_ids')
        
        return context