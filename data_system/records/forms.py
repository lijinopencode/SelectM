# 添加必要的导入语句
from django import forms
from datetime import date, datetime
from .models import Category, DataRecord, DailyNumber

# 添加CategoryForm表单类
class CategoryForm(forms.ModelForm):
    """类别表单"""
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# 添加DataRecordForm表单类
# 在文件顶部导入parse_number_group函数
from .utils import parse_number_group

class DataRecordForm(forms.ModelForm):
    """数据记录表单"""
    class Meta:
        model = DataRecord
        fields = ['category', 'data_name', 'start_date', 'end_date', 'data_value', 'is_excluded_group']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'data_name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'id': 'id_start_date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'id': 'id_end_date'
            }),
            'data_value': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_excluded_group': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 只有在新建记录时（没有instance）才排除已存在的日期组合
        if not self.instance.pk:
            # 获取所有已存在的记录，按类别和名称分组
            existing_records = DataRecord.objects.values('category_id', 'data_name', 'start_date')
            
            # 构建类别ID和数据名称到日期列表的映射
            category_name_dates = {}
            for record in existing_records:
                key = f"{record['category_id']}_{record['data_name']}"
                date_str = record['start_date'].strftime('%Y-%m-%d')
                if key not in category_name_dates:
                    category_name_dates[key] = []
                category_name_dates[key].append(date_str)
            
            # 将按类别和名称分组的日期信息转换为JSON字符串
            import json
            self.fields['start_date'].widget.attrs['data-category-name-dates'] = json.dumps(category_name_dates)
    
    def clean_data_value(self):
        """处理data_value字段"""
        data_value = self.cleaned_data.get('data_value', '')
        return data_value

    def clean(self):
        """处理表单数据，解析数字"""
        cleaned_data = super().clean()
        data_value = cleaned_data.get('data_value', '')
        
        # 初始化parsed_numbers为空列表
        cleaned_data['parsed_numbers'] = []
        
        # 如果有数据值，尝试解析其中的数字
        if data_value and data_value.strip():
            try:
                # 使用parse_number_group函数解析数字
                numbers_to_add = parse_number_group(data_value)
                
                # 如果成功解析到数字，更新parsed_numbers
                if numbers_to_add:
                    cleaned_data['parsed_numbers'] = numbers_to_add
            except Exception as e:
                # 任何错误都不阻止表单提交，保持为空列表
                print(f"解析错误: {e}")
        
        return cleaned_data
        
    def save(self, commit=True):
        """重写save方法，确保parsed_numbers字段被正确处理"""
        instance = super().save(commit=False)
        
        # 将解析后的数字从cleaned_data设置到实例上
        if 'parsed_numbers' in self.cleaned_data:
            parsed_numbers = self.cleaned_data['parsed_numbers']
            # 确保parsed_numbers是有效的JSON数据
            if isinstance(parsed_numbers, list):
                instance.parsed_numbers = parsed_numbers
            else:
                instance.parsed_numbers = []
        
        if commit:
            instance.save()
        return instance

class DailyNumberForm(forms.ModelForm):
    """每日数字记录表单"""
    
    # 显式定义hit_number为CharField，确保可以接收任意字符串
    hit_number = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入命中数字（如：27.24.6.26.18.41.32.10.28）',
            'type': 'text',
        })
    )
    
    # 移除之前的parsed_numbers字段定义，改为使用自定义方法处理
    
    # 显式定义opened_number为CharField以避免整数值过大问题
    # 然后在clean方法中验证它是有效整数并转换
    opened_number = forms.CharField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入开出数字（单个数字）',
            'type': 'number'
        })
    )
    
    class Meta:
        model = DailyNumber
        fields = ['date', 'hit_number', 'hit_time', 'opened_number']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                },
                format='%Y-%m-%d'  # 明确指定格式
            ),
            'hit_time': forms.TimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'time',
                },
                format='%H:%M'  # 明确指定格式
            ),
        }

    def __init__(self, *args, **kwargs):
        # 先获取初始值字典
        initial = kwargs.get('initial', {})
        
        # 检查是否是新建记录（没有instance）
        if not kwargs.get('instance'):
            # 对于新建记录，如果初始值中没有日期，设置为今天
            if 'date' not in initial:
                from datetime import date
                initial['date'] = date.today().strftime('%Y-%m-%d')  # 格式化为字符串
            # 如果初始值中没有时间，设置为当前时间
            if 'hit_time' not in initial:
                from datetime import datetime
                initial['hit_time'] = datetime.now().strftime('%H:%M')  # 格式化为字符串
            # 设置opened_number默认值为0
            if 'opened_number' not in initial:
                initial['opened_number'] = '0'
                
            # 更新kwargs中的初始值
            kwargs['initial'] = initial
            
        # 调用父类初始化
        super().__init__(*args, **kwargs)
        
        # 编辑模式时的处理
        if kwargs.get('instance'):
            instance = kwargs.get('instance')
            # 如果hit_number存在，保留原始格式
            if instance.hit_number and not initial.get('hit_number'):
                self.initial['hit_number'] = instance.hit_number
            # 处理opened_number显示
            if instance.opened_number is not None:
                self.initial['opened_number'] = str(instance.opened_number)
            elif instance.opened_number is None:
                self.initial['opened_number'] = '0'

    # 添加一个方法来生成高亮显示的parsed_numbers HTML
    def get_highlighted_parsed_numbers(self):
        # 获取opened_number的值
        opened_number = None
        
        # 首先检查cleaned_data
        if hasattr(self, 'cleaned_data') and self.cleaned_data.get('opened_number') is not None:
            opened_number = self.cleaned_data.get('opened_number')
        # 然后检查实例
        elif hasattr(self, 'instance') and self.instance.opened_number is not None:
            opened_number = self.instance.opened_number
        # 最后检查初始值
        elif self.initial.get('opened_number'):
            try:
                opened_number = int(self.initial.get('opened_number'))
            except (ValueError, TypeError):
                pass
        
        # 获取parsed_numbers
        parsed_numbers = []
        
        # 首先检查cleaned_data
        if hasattr(self, 'cleaned_data') and self.cleaned_data.get('parsed_numbers'):
            parsed_numbers = self.cleaned_data.get('parsed_numbers')
        # 然后检查实例
        elif hasattr(self, 'instance') and self.instance.parsed_numbers:
            parsed_numbers = self.instance.parsed_numbers
        # 如果有hit_number，尝试解析
        elif hasattr(self, 'cleaned_data') and self.cleaned_data.get('hit_number'):
            try:
                parsed_numbers = parse_number_group(self.cleaned_data.get('hit_number'))
            except Exception:
                pass
        elif self.initial.get('hit_number'):
            try:
                parsed_numbers = parse_number_group(self.initial.get('hit_number'))
            except Exception:
                pass
        
        # 生成高亮HTML
        if parsed_numbers:
            parts = []
            for num in parsed_numbers:
                if opened_number is not None and num == opened_number:
                    # 高亮显示匹配的数字
                    parts.append(f'<span style="background-color: yellow; padding: 0 2px;">{num}</span>')
                else:
                    parts.append(str(num))
            return '.'.join(parts)
        return ''

    def clean_opened_number(self):
        """验证opened_number是一个有效的整数字符串并转换为整数"""
        opened_number_str = self.cleaned_data.get('opened_number', '').strip()
        
        # 重要：如果为空，显式返回None而不是空字符串
        if not opened_number_str:
            return None
            
        try:
            # 验证是有效的整数且在MySQL INT范围内
            value = int(opened_number_str)
            # MySQL INT范围检查
            if value < -2147483648 or value > 2147483647:
                raise forms.ValidationError("数字超出范围，请输入-2147483648到2147483647之间的整数")
            return value
        except ValueError:
            raise forms.ValidationError("请输入有效的整数字符串")

    def clean(self):
        """处理表单数据"""
        cleaned_data = super().clean()
        hit_number_str = cleaned_data.get('hit_number', '')
        
        # 确保opened_number为None而不是空字符串
        if 'opened_number' in cleaned_data:
            if cleaned_data['opened_number'] == '':
                cleaned_data['opened_number'] = None
        
        # 初始化parsed_numbers为空列表
        cleaned_data['parsed_numbers'] = []
        
        # 如果有命中数字字符串，尝试解析其中的数字
        if hit_number_str and hit_number_str.strip():
            try:
                # 使用我们修改过的parse_number_group函数解析数字
                numbers_to_add = parse_number_group(hit_number_str)
                
                # 如果成功解析到数字，更新parsed_numbers
                if numbers_to_add:
                    cleaned_data['parsed_numbers'] = numbers_to_add
                    # 同时更新表单显示值
                    self.initial['parsed_numbers'] = '.'.join(map(str, numbers_to_add))
            except Exception as e:
                # 任何错误都不阻止表单提交，保持为空列表
                print(f"解析错误: {e}")  # 添加调试信息
                # 保持parsed_numbers为空列表
        
        return cleaned_data
        
    def save(self, commit=True):
        """重写save方法，确保所有字段被正确处理"""
        instance = super().save(commit=False)
        
        # 确保如果opened_number为空，它被设置为None而不是空字符串
        if hasattr(self.cleaned_data, 'get'):
            opened_value = self.cleaned_data.get('opened_number')
            if opened_value == '':
                instance.opened_number = None
        
        # 关键修复：将解析后的数字从cleaned_data设置到实例上
        if hasattr(self.cleaned_data, 'get') and 'parsed_numbers' in self.cleaned_data:
            # 确保parsed_numbers是有效的JSON数据
            parsed_numbers = self.cleaned_data['parsed_numbers']
            # 如果是列表，直接赋值（Django的JSONField会自动处理）
            if isinstance(parsed_numbers, list):
                instance.parsed_numbers = parsed_numbers
            else:
                # 如果不是列表，设置为空列表
                instance.parsed_numbers = []
        
        # 直接检查instance.opened_number的值
        if hasattr(instance, 'opened_number'):
            if instance.opened_number == '':
                instance.opened_number = None
        
        if commit:
            instance.save()
        return instance