from django.test import TestCase
from .utils import get_zodiac_by_number, get_numbers_by_zodiac, CHINESE_ZODIAC_MAP

class ChineseZodiacTests(TestCase):
    """测试中国生肖与数字的转换功能"""

    def test_get_zodiac_by_number_basic(self):
        """测试基本的数字到生肖转换"""
        # 测试鼠的数字
        self.assertEqual(get_zodiac_by_number(6), '鼠')
        self.assertEqual(get_zodiac_by_number(18), '鼠')
        self.assertEqual(get_zodiac_by_number(30), '鼠')
        self.assertEqual(get_zodiac_by_number(42), '鼠')
        
        # 测试其他生肖
        self.assertEqual(get_zodiac_by_number(5), '牛')
        self.assertEqual(get_zodiac_by_number(4), '虎')
        self.assertEqual(get_zodiac_by_number(3), '兔')
        self.assertEqual(get_zodiac_by_number(2), '龙')
        self.assertEqual(get_zodiac_by_number(1), '蛇')
        self.assertEqual(get_zodiac_by_number(12), '马')
        self.assertEqual(get_zodiac_by_number(11), '羊')
        self.assertEqual(get_zodiac_by_number(10), '猴')
        self.assertEqual(get_zodiac_by_number(9), '鸡')
        self.assertEqual(get_zodiac_by_number(8), '狗')
        self.assertEqual(get_zodiac_by_number(7), '猪')

    def test_get_zodiac_by_number_string_input(self):
        """测试字符串类型的数字输入"""
        self.assertEqual(get_zodiac_by_number('6'), '鼠')
        self.assertEqual(get_zodiac_by_number('18'), '鼠')
        self.assertEqual(get_zodiac_by_number('06'), '鼠')  # 带前导零的字符串

    def test_get_zodiac_by_number_invalid_input(self):
        """测试无效输入"""
        # 超出范围的数字
        self.assertIsNone(get_zodiac_by_number(0))
        self.assertIsNone(get_zodiac_by_number(50))
        
        # 非数字输入
        self.assertIsNone(get_zodiac_by_number('abc'))
        self.assertIsNone(get_zodiac_by_number(None))
        self.assertIsNone(get_zodiac_by_number([]))

    def test_get_numbers_by_zodiac_basic(self):
        """测试基本的生肖到数字列表转换"""
        # 验证所有生肖对应的数字列表
        expected_numbers = {
            '鼠': [6, 18, 30, 42],
            '牛': [5, 17, 29, 41],
            '虎': [4, 16, 28, 40],
            '兔': [3, 15, 27, 39],
            '龙': [2, 14, 26, 38],
            '蛇': [1, 13, 25, 37, 49],
            '马': [12, 24, 36, 48],
            '羊': [11, 23, 35, 47],
            '猴': [10, 22, 34, 46],
            '鸡': [9, 21, 33, 45],
            '狗': [8, 20, 32, 44],  # 注意：这里使用了修正后的数字
            '猪': [7, 19, 31, 43]
        }
        
        for zodiac, expected in expected_numbers.items():
            self.assertEqual(get_numbers_by_zodiac(zodiac), expected)

    def test_get_numbers_by_zodiac_aliases(self):
        """测试生肖别名处理"""
        # 测试'免'会自动修正为'兔'
        self.assertEqual(get_numbers_by_zodiac('免'), [3, 15, 27, 39])
        self.assertEqual(get_numbers_by_zodiac('兔'), [3, 15, 27, 39])

    def test_get_numbers_by_zodiac_invalid_input(self):
        """测试无效的生肖输入"""
        # 不存在的生肖
        self.assertIsNone(get_numbers_by_zodiac('猫'))
        self.assertIsNone(get_numbers_by_zodiac('龙1'))
        
        # 空值和非字符串
        self.assertIsNone(get_numbers_by_zodiac(''))
        self.assertIsNone(get_numbers_by_zodiac(None))
        self.assertIsNone(get_numbers_by_zodiac(123))

    def test_zodiac_map_consistency(self):
        """测试生肖映射的一致性"""
        # 确保每个生肖都有对应的数字列表
        for zodiac in ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']:
            self.assertIn(zodiac, CHINESE_ZODIAC_MAP)
            self.assertIsInstance(CHINESE_ZODIAC_MAP[zodiac], list)
            self.assertTrue(len(CHINESE_ZODIAC_MAP[zodiac]) > 0)
        
        # 确保每个数字都能正确映射到对应的生肖
        for zodiac, numbers in CHINESE_ZODIAC_MAP.items():
            for number in numbers:
                self.assertEqual(get_zodiac_by_number(number), zodiac)

# 还可以为现有函数添加测试
from .utils import parse_number_group, format_number_list

class NumberParsingTests(TestCase):
    """测试数字解析和格式化功能"""

    def test_parse_number_group_basic(self):
        """测试基本的数字解析功能"""
        self.assertEqual(parse_number_group('1,2,3'), [1, 2, 3])
        self.assertEqual(parse_number_group('1.2.3'), [1, 2, 3])
        self.assertEqual(parse_number_group('1，2，3'), [1, 2, 3])

    def test_parse_number_group_mixed_separators(self):
        """测试混合分隔符"""
        self.assertEqual(parse_number_group('1,2.3，4'), [1, 2, 3, 4])

    def test_parse_number_group_with_text(self):
        """测试包含文字的数字字符串"""
        self.assertEqual(parse_number_group('数字1,数字2和数字3'), [1, 2, 3])
        self.assertEqual(parse_number_group('啊实打实的22,33,44'), [22, 33, 44])

    def test_parse_number_group_empty_input(self):
        """测试空输入"""
        self.assertEqual(parse_number_group(''), [])
        self.assertEqual(parse_number_group('   '), [])
        self.assertEqual(parse_number_group(None), [])

    def test_format_number_list(self):
        """测试数字列表格式化"""
        self.assertEqual(format_number_list([1, 2, 3]), '1.2.3')
        self.assertEqual(format_number_list([]), '')
        self.assertEqual(format_number_list([6, 18, 30, 42]), '6.18.30.42')