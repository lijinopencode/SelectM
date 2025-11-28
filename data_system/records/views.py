# 正确的导入位置应该在文件顶部
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
# 添加日志模块导入
import logging
# 在文件顶部添加datetime导入（如果还没有）
from datetime import date, datetime, timedelta
from .models import Category, DataRecord, DailyNumber, Website  # 添加Website导入
from .forms import CategoryForm, DataRecordForm, DailyNumberForm, WebsiteForm  # 添加WebsiteForm导入
# 导入生肖相关函数 - 正确放在顶部
from .utils import get_zodiac_by_number, get_numbers_by_zodiac, CHINESE_ZODIAC_MAP, get_numbers_with_zodiac
# 在文件顶部的导入部分添加
from .models import Website
# 配置日志记录器
logger = logging.getLogger(__name__)


# 首页
def index(request):
    # 记录首页访问日志
    logger.info(f"访问首页界面 - 视图函数: index")
    return render(request, "records/index.html")


# 类别管理
class CategoryListView(ListView):
    model = Category
    template_name = "records/category_list.html"
    context_object_name = "categories"
    
    def get_queryset(self):
        # 按网站ID和类别名称排序，使同一个来源网站的类别显示在一起
        return Category.objects.all().order_by('website_id', 'name')
    
    def dispatch(self, request, *args, **kwargs):
        # 记录访问日志
        logger.info(f"访问类别列表界面 - 视图类: CategoryListView, 模板: {self.template_name}")
        return super().dispatch(request, *args, **kwargs)


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "records/category_form.html"
    success_url = reverse_lazy("category_list")
    success_message = "类别添加成功！"
    
    def dispatch(self, request, *args, **kwargs):
        # 记录访问日志
        logger.info(f"访问类别创建界面 - 视图类: CategoryCreateView, 模板: {self.template_name}")
        return super().dispatch(request, *args, **kwargs)


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "records/category_form.html"
    success_url = reverse_lazy("category_list")
    success_message = "类别更新成功！"
    
    def dispatch(self, request, *args, **kwargs):
        # 记录访问日志
        logger.info(f"访问类别更新界面 - 视图类: CategoryUpdateView, 模板: {self.template_name}")
        return super().dispatch(request, *args, **kwargs)


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "records/category_confirm_delete.html"
    success_url = reverse_lazy("category_list")
    success_message = "类别删除成功！"
    
    def dispatch(self, request, *args, **kwargs):
        # 记录访问日志
        logger.info(f"访问类别删除界面 - 视图类: CategoryDeleteView, 模板: {self.template_name}")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)


# 数据记录管理
class DataRecordListView(ListView):
    model = DataRecord
    template_name = "records/data_record_list.html"
    context_object_name = "records"
    
    def dispatch(self, request, *args, **kwargs):
        # 记录访问日志，包含筛选参数信息
        category_id = request.GET.get("category_id")
        website_id = request.GET.get("website_id")  # 新增：获取网站ID筛选参数
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        logger.info(f"访问数据记录列表界面 - 视图类: DataRecordListView, 模板: {self.template_name}, "
                   f"筛选参数: category_id={category_id}, website_id={website_id}, "
                   f"start_date={start_date}, end_date={end_date}")  # 更新日志格式
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """带筛选条件的查询"""
        # 新增：预加载category和website以提高性能
        queryset = super().get_queryset().select_related("category", "category__website")
        category_id = self.request.GET.get("category_id")
        website_id = self.request.GET.get("website_id")  # 新增：获取网站ID筛选参数
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # 新增：按网站类别筛选
        if website_id:
            queryset = queryset.filter(category__website_id=website_id)
        
        # 基于开始时间和结束时间进行筛选
        if start_date and end_date:
            # 筛选时间范围重叠的记录
            # 情况1: 记录的开始时间在筛选范围内
            # 情况2: 记录的结束时间在筛选范围内
            # 情况3: 记录完全包含筛选范围
            queryset = queryset.filter(
                (Q(start_date__gte=start_date) & Q(start_date__lte=end_date)) |
                (Q(end_date__gte=start_date) & Q(end_date__lte=end_date)) |
                (Q(start_date__lte=start_date) & Q(end_date__gte=end_date))
            )
        elif start_date:
            # 只提供开始时间，筛选出结束时间大于等于开始时间的记录
            queryset = queryset.filter(end_date__gte=start_date)
        elif end_date:
            # 只提供结束时间，筛选出开始时间小于等于结束时间的记录
            queryset = queryset.filter(start_date__lte=end_date)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()  # 用于筛选下拉框
        context["websites"] = Website.objects.all()  # 新增：添加所有网站列表到上下文
        
        # 保存当前筛选参数到上下文，用于模板中显示选中状态
        context["selected_website_id"] = self.request.GET.get("website_id")
        context["selected_category_id"] = self.request.GET.get("category_id")
        context["selected_start_date"] = self.request.GET.get("start_date")
        context["selected_end_date"] = self.request.GET.get("end_date")
        
        # 获取查询集中所有记录的日期，然后获取对应的DailyNumber
        records = context.get('records', [])
        # 使用字典存储日期到DailyNumber的映射
        date_to_daily_number = {}
        
        # 提取所有不重复的日期（使用start_date）
        dates = set()
        for record in records:
            dates.add(record.start_date)
            
            # 新增：解析data_value中的生肖并更新parsed_numbers
            if record.data_value and record.data_value.strip():
                # 尝试从data_value中提取生肖
                for zodiac in CHINESE_ZODIAC_MAP.keys():
                    if zodiac in record.data_value:
                        # 如果找到了生肖，获取对应的数字列表
                        zodiac_numbers = get_numbers_by_zodiac(zodiac)
                        if zodiac_numbers:
                            # 将生肖对应的数字添加到parsed_numbers
                            if not record.parsed_numbers:
                                record.parsed_numbers = []
                            # 去重并保留原始数字
                            combined_numbers = list(set(record.parsed_numbers + zodiac_numbers))
                            # 对数字进行排序
                            combined_numbers.sort()
                            record.parsed_numbers = combined_numbers
            
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


# 在文件末尾修改NumberComparisonView类
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
        queryset = DataRecord.objects.filter(start_date=comparison_date).select_related('category')
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
        
        # 获取所有记录
        records = self.get_queryset()
        
        # 导入必要的函数
        from .utils import parse_number_group, get_numbers_with_zodiac, get_zodiac_by_number
        
        # 处理所有记录的数字
        for record in records:
            # 强制从data_value解析数字
            numbers_list = []
            if record.data_value:
                numbers_list = parse_number_group(record.data_value)
            
            # 确保是列表
            if not isinstance(numbers_list, list):
                numbers_list = []
            
            # 生成带生肖的数字列表
            numbers_with_zodiac = get_numbers_with_zodiac(numbers_list)
            
            # 直接设置属性
            record.numbers_with_zodiac = numbers_with_zodiac
            record.numbers = numbers_list
        
        # 添加到上下文 - 将所有记录作为一个列表传递，不再分组
        context['all_records'] = records
        
        # 获取该日期的每日数字记录（如果存在）
        try:
            daily_number = DailyNumber.objects.get(date=comparison_date)
            # 确保opened_number是字符串
            if daily_number.opened_number is not None:
                daily_number.opened_number = str(daily_number.opened_number)
                daily_number.opened_number_zodiac = get_zodiac_by_number(daily_number.opened_number)
            context['daily_number'] = daily_number
        except DailyNumber.DoesNotExist:
            context['daily_number'] = None
        
        # 添加today变量到上下文
        context['today'] = date.today().strftime('%Y-%m-%d')

        return context


# API接口：获取指定日期的预设数据组
def get_preset_data_groups(request):
    """
    API接口：根据日期获取预设数据组
    URL: /api/preset-data-groups/?date=2025-11-26
    """
    # 获取日期参数
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'error': '缺少date参数'}, status=400)

    try:
        # 解析日期
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': '日期格式错误，应为YYYY-MM-DD'}, status=400)

    # 获取该日期的所有数据记录
    records = DataRecord.objects.filter(start_date=query_date).select_related('category')

    # 构建返回数据
    data_groups = []
    group_id = 1

    # 为每个记录创建一个"比较"类型的数据组
    for record in records:
        if record.data_value:
            data_groups.append({
                'id': group_id,
                'name': f'{record.category.name if record.category else "未分类"} - {record.description or "数据记录"}',
                'type': 'compare',
                'data': record.data_value,
                'date': date_str
            })
            group_id += 1

    # 可以添加一些默认的排除数据组
    # 例如：基于历史数据的常见排除值
    common_excludes = get_common_excludes_for_date(query_date)
    if common_excludes:
        data_groups.insert(0, {
            'id': group_id,
            'name': f'{date_str} - 常见排除值',
            'type': 'exclude',
            'data': common_excludes,
            'date': date_str
        })

    return JsonResponse(data_groups, safe=False)


def get_common_excludes_for_date(query_date):
    """
    获取指定日期的常见排除值
    可以基于历史数据或规则生成
    """
    # 这里可以实现更复杂的逻辑
    # 例如：获取前几天的开奖号码作为排除值
    try:
        # 获取最近7天的开奖号码
        recent_numbers = DailyNumber.objects.filter(
            date__lt=query_date,
            date__gte=query_date - timedelta(days=7)
        ).order_by('-date')[:7]

        if recent_numbers:
            exclude_numbers = []
            for dn in recent_numbers:
                if dn.opened_number:
                    exclude_numbers.append(str(dn.opened_number))

            if exclude_numbers:
                return ', '.join(exclude_numbers)
    except Exception as e:
        logger.error(f"获取常见排除值失败: {e}")

    return ''


# 在文件末尾添加新的API端点
def get_records_by_date(request):
    """
    API接口：根据选择的日期获取所有在start_date和end_date范围内的DataRecord数据
    URL: /api/records-by-date/?date=2025-11-26
    """
    # 获取日期参数
    date_str = request.GET.get('date')

    if not date_str:
        return JsonResponse({'error': '缺少date参数'}, status=400)

    try:
        # 解析日期
        query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': '日期格式错误，应为YYYY-MM-DD'}, status=400)

    # 查询在start_date和end_date范围内的所有记录
    # 条件：记录的开始日期 <= 查询日期 <= 记录的结束日期（如果结束日期存在）
    # 或者记录的开始日期 <= 查询日期且结束日期为空（表示持续有效）
    records = DataRecord.objects.filter(
        Q(start_date__lte=query_date) & 
        (Q(end_date__gte=query_date) | Q(end_date__isnull=True))
    ).select_related('category').order_by('category__name', 'data_name')

    # 构建返回数据
    result_data = []
    for record in records:
        # 解析数字
        numbers = []
        if record.data_value:
            try:
                from .utils import parse_number_group
                numbers = parse_number_group(record.data_value)
            except Exception:
                pass
        
        result_data.append({
            'id': record.id,
            'category': record.category.name if record.category else '未分类',
            'data_name': record.data_name,
            'start_date': record.start_date.strftime('%Y-%m-%d'),
            'end_date': record.end_date.strftime('%Y-%m-%d') if record.end_date else None,
            'data_value': record.data_value,
            'numbers': numbers,
            'is_excluded_group': record.is_excluded_group
        })

    return JsonResponse({
        'date': date_str,
        'records': result_data,
        'total': len(result_data)
    })


# 网站管理 - 添加新的视图类
class WebsiteListView(ListView):
    model = Website
    template_name = "records/website_list.html"
    context_object_name = "websites"
    
    def dispatch(self, request, *args, **kwargs):
        # 记录访问日志
        logger.info(f"访问网站列表界面 - 视图类: WebsiteListView, 模板: {self.template_name}")
        return super().dispatch(request, *args, **kwargs)


class WebsiteCreateView(CreateView):
    model = Website
    form_class = WebsiteForm
    template_name = "records/website_form.html"
    success_url = reverse_lazy("website_list")
    success_message = "网站添加成功！"
    
    def dispatch(self, request, *args, **kwargs):
        # 记录访问日志
        logger.info(f"访问网站创建界面 - 视图类: WebsiteCreateView, 模板: {self.template_name}")
        return super().dispatch(request, *args, **kwargs)


class WebsiteUpdateView(UpdateView):
    model = Website
    form_class = WebsiteForm
    template_name = "records/website_form.html"
    success_url = reverse_lazy("website_list")
    success_message = "网站更新成功！"
    
    def dispatch(self, request, *args, **kwargs):
        # 记录访问日志
        logger.info(f"访问网站更新界面 - 视图类: WebsiteUpdateView, 模板: {self.template_name}")
        return super().dispatch(request, *args, **kwargs)


class WebsiteDeleteView(DeleteView):
    model = Website
    template_name = "records/website_confirm_delete.html"
    success_url = reverse_lazy("website_list")
    success_message = "网站删除成功！"
    
    def dispatch(self, request, *args, **kwargs):
        # 记录访问日志
        logger.info(f"访问网站删除界面 - 视图类: WebsiteDeleteView, 模板: {self.template_name}")
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)