from typing import List, Dict, Optional
import re

# 定义生肖与数字的映射关系
CHINESE_ZODIAC_MAP: Dict[str, List[int]] = {
    '鼠': [6, 18, 30, 42],
    '牛': [5, 17, 29, 41],
    '虎': [4, 16, 28, 40],
    '兔': [3, 15, 27, 39],  # 修正了"免"为正确的"兔"
    '龙': [2, 14, 26, 38],
    '蛇': [1, 13, 25, 37, 49], 
    '马': [12, 24, 36, 48],
    '羊': [11, 23, 35, 47],
    '猴': [10, 22, 34, 46],
    '鸡': [9, 21, 33, 45],
    '狗': [8, 20, 32, 44],  # 修正了狗的数字(原数据中21重复)
    '猪': [7, 19, 31, 43]
}

# 创建反向映射：数字到生肖
NUMBER_TO_ZODIAC_MAP: Dict[int, str] = {}
for zodiac, numbers in CHINESE_ZODIAC_MAP.items():
    for number in numbers:
        NUMBER_TO_ZODIAC_MAP[number] = zodiac

def get_zodiac_by_number(number: int) -> Optional[str]:
    """
    通过数字获取对应的生肖
    
    Args:
        number: 要查询的数字(1-49)
        
    Returns:
        Optional[str]: 对应的生肖，若数字不在映射范围内则返回None
    """
    if not isinstance(number, int):
        # 尝试转换字符串到整数
        try:
            number = int(number)
        except (ValueError, TypeError):
            return None
    
    return NUMBER_TO_ZODIAC_MAP.get(number)

def get_numbers_by_zodiac(zodiac: str) -> Optional[List[int]]:
    """
    通过生肖获取对应的数字列表
    
    Args:
        zodiac: 要查询的生肖(如'鼠'、'牛'等)
        
    Returns:
        Optional[List[int]]: 对应的数字列表，若生肖不存在则返回None
    """
    if not isinstance(zodiac, str) or not zodiac:
        return None
    
    # 处理可能的别名或错误输入，如'免'->'兔'
    zodiac_aliases = {
        '免': '兔'
    }
    
    # 检查是否有别名
    if zodiac in zodiac_aliases:
        zodiac = zodiac_aliases[zodiac]
    
    return CHINESE_ZODIAC_MAP.get(zodiac)

def parse_number_group(number_group_str: str) -> List[int]:
    """
    解析多种分隔格式的数字组字符串为整数列表
    支持点号(.)、逗号(,)和中文逗号(，)作为分隔符
    可以处理混合格式如"24.6，26.18.41,32，10.28"
    也可以处理包含文字的格式如"啊实打实的22,33,44"
    
    Args:
        number_group_str: 混合分隔的数字字符串，可包含文字
        
    Returns:
        List[int]: 解析后的整数列表
    """
    if not number_group_str or not number_group_str.strip():
        return []
    
    try:
        # 使用正则表达式匹配所有数字
        # 匹配所有连续的数字字符，忽略非数字字符
        numbers = re.findall(r'\d+', number_group_str)
        
        # 转换为整数列表
        int_numbers = [int(num) for num in numbers]
        
        # 如果没有找到数字，返回空列表而不是抛出异常
        return int_numbers
    except Exception as e:
        # 捕获所有异常，返回空列表
        return []

def format_number_list(numbers: List[int]) -> str:
    """
    将整数列表格式化为点分隔的数字字符串
    
    Args:
        numbers: 整数列表
        
    Returns:
        str: 点分隔的数字字符串
    """
    return '.'.join(map(str, numbers))


# 在utils.py文件中添加
# 添加获取带生肖信息的数字列表函数
def get_numbers_with_zodiac(numbers_list):
    """将数字列表转换为包含生肖信息的字典列表，并按数字从小到大排序"""
    result = []
    # 确保输入是列表
    if not isinstance(numbers_list, list):
        numbers_list = []
    
    # 添加调试信息
    #print(f"Input numbers_list: {numbers_list}")
    
    for num in numbers_list:
        try:
            # 处理数字
            if isinstance(num, (int, float, str)):
                # 尝试转换为整数
                num_int = int(str(num))
                zodiac = get_zodiac_by_number(num_int)
                result.append({
                    'number': num_int,
                    'zodiac': zodiac or ''
                })
                #print(f"Processed num: {num_int}, zodiac: {zodiac}")
            else:
                # 处理其他类型
                result.append({
                    'number': str(num),
                    'zodiac': ''
                })
        except Exception as e:
            print(f"Error processing num {num}: {str(e)}")
            result.append({
                'number': str(num),
                'zodiac': ''
            })
    
    # 按数字从小到大排序
    result.sort(key=lambda x: x['number'] if isinstance(x['number'], int) else float('inf'))
    
    #print(f"Output result: {result}")
    return result