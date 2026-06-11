import json
import requests

import os

class TextClassifier:
    SELL_KEYWORDS = ['出售', '卖', '转让', 'sell', '闲置', '二手', '全新', '低价']
    BUY_KEYWORDS = ['求购', '买', '需要', 'buy', 'want', '收购', '想要', '急求']

    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key or os.environ.get('QWEN_API_KEY', '')
        self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"

    def generate_tags_with_qwen(self, title, description):
        if not self.api_key:
            return self.generate_tags_by_keywords(title, description)

        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            data = {
                'model': 'qwen3.7-plus',
                'messages': [
                    {
                        'role': 'system',
                        'content': '''你是一个二手市场商品标签生成器。请根据商品标题和描述，生成3-8个合适的标签。
标签要求：
1. 每个标签1-4个汉字或英文单词
2. 标签应反映商品类别、品牌、成色、用途等特征
3. 只返回JSON数组格式，例如：["电子产品", "九成新", "手机", "苹果"]
4. 不要返回任何其他内容
5. 禁止生成"二手商品"、"二手"、"闲置"、"闲置物品"等标签，因为平台本身就是二手交易平台，这类标签没有区分意义'''
                    },
                    {
                        'role': 'user',
                        'content': f'标题：{title}\n描述：{description}'
                    }
                ],
                'temperature': 0.3,
                'max_tokens': 200
            }

            response = requests.post(url, json=data, headers=headers, timeout=10)
            result = response.json()

            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
                import json
                tags = json.loads(content)
                if isinstance(tags, list):
                    return {
                        'tags': tags[:8],
                        'source': 'qwen'
                    }

        except Exception as e:
            print(f'Qwen tag generation error: {e}')

        return self.generate_tags_by_keywords(title, description)

    def estimate_price_with_qwen(self, title, description, condition):
        """使用Qwen模型估算二手商品价格"""
        if not self.api_key:
            return {'min_price': 0, 'max_price': 0, 'source': 'fallback'}

        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            data = {
                'model': 'qwen3.7-plus',
                'messages': [
                    {
                        'role': 'system',
                        'content': '''你是一个二手市场价格估算专家。请根据商品标题、描述和成色，估算一个合理的二手价格范围。
要求：
1. 价格单位为人民币（元）
2. 返回JSON格式：{"min_price": 最低价格（数字）, "max_price": 最高价格（数字）}
3. 价格范围不要太大，max_price - min_price 不超过 min_price 的 30%
4. 只返回JSON，不要返回任何其他内容
5. 考虑因素：商品类型、品牌、成色、市场行情'''
                    },
                    {
                        'role': 'user',
                        'content': f'标题：{title}\n描述：{description}\n成色：{condition}'
                    }
                ],
                'temperature': 0.2,
                'max_tokens': 100
            }

            response = requests.post(url, json=data, headers=headers, timeout=15)
            result = response.json()

            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
                import json
                parsed = json.loads(content)
                return {
                    'min_price': parsed.get('min_price', 0),
                    'max_price': parsed.get('max_price', 0),
                    'source': 'qwen'
                }

        except Exception as e:
            print(f'Qwen price estimation error: {e}')

        return {'min_price': 0, 'max_price': 0, 'source': 'error'}

    def generate_tags_by_keywords(self, title, description):
        text = f'{title} {description}'.lower()
        tags = []

        category_keywords = {
            '电子产品': ['手机', '电脑', '平板', '耳机', '相机', '键盘', '鼠标', '显示器', '笔记本', 'iphone', 'ipad', 'macbook'],
            '图书': ['书', '教材', '小说', '杂志', 'book'],
            '服装': ['衣服', '裤子', '鞋子', '外套', '裙子', 't恤', '衬衫', 'clothes', 'shoes'],
            '家具': ['桌子', '椅子', '床', '柜子', '沙发', '书架', 'desk', 'chair'],
            '运动': ['篮球', '足球', '羽毛球', '跑步', '健身', '运动', 'sports'],
            '乐器': ['吉他', '钢琴', '小提琴', 'guitar', 'piano'],
            '游戏': ['游戏', 'switch', 'ps5', 'xbox', 'game'],
            '化妆品': ['口红', '粉底', '面膜', '护肤', 'cosmetic'],
        }

        condition_keywords = {
            '全新未拆封': ['全新未拆封', '未拆封', '全新'],
            '几乎全新': ['几乎全新', '九成新', '99新', '几乎没使用'],
            '轻微使用痕迹': ['轻微使用', '轻微磨损', '细微使用', '细微磨损', '小瑕疵'],
            '中度使用痕迹': ['中度使用', '中度磨损', '明显使用', '明显磨损'],
            '严重使用痕迹': ['严重使用', '严重磨损', '大瑕疵', '破损'],
        }

        for category, keywords in category_keywords.items():
            if any(kw in text for kw in keywords):
                tags.append(category)

        for condition, keywords in condition_keywords.items():
            if any(kw in text for kw in keywords):
                tags.append(condition)
                break

        brand_keywords = ['苹果', '华为', '小米', '三星', '索尼', 'nike', 'adidas', 'apple', 'huawei']
        for brand in brand_keywords:
            if brand in text:
                tags.append(brand)
                break

        return {
            'tags': tags[:8] if tags else ['闲置物品'],
            'source': 'keyword'
        }

class ContentFilter:
    SENSITIVE_WORDS = [
        '作弊', '骗子', '假货', '诈骗', '钓鱼',
        '色情', '赌博', '暴力', '毒品', '枪支'
    ]

    @staticmethod
    def contains_sensitive(text):
        text_lower = text.lower()
        found = []
        for word in ContentFilter.SENSITIVE_WORDS:
            if word in text_lower:
                found.append(word)
        return {
            'is_clean': len(found) == 0,
            'found_words': found
        }

    @staticmethod
    def filter_text(text):
        result = ContentFilter.contains_sensitive(text)
        if result['is_clean']:
            return {'filtered': False, 'text': text}
        return {'filtered': True, 'text': text}

class AIMessageSummarizer:
    @staticmethod
    def summarize(message_content):
        if not message_content:
            return ''

        content = message_content.strip()

        if len(content) <= 50:
            return content

        return content[:50] + '...'

def generate_conversation_hash(user1_id, user2_id):
    sorted_ids = sorted([str(user1_id), str(user2_id)])
    return hashlib.md5('_'.join(sorted_ids).encode()).hexdigest()

def format_timestamp(dt=None):
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M:%S')