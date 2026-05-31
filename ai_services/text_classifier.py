import json
import hashlib
import requests
import time
from datetime import datetime

class TextClassifier:
    SELL_KEYWORDS = ['出售', '卖', '转让', 'sell', 'sell', '转让', '闲置', '二手', '全新', '低价']
    BUY_KEYWORDS = ['求购', '买', '需要', 'buy', 'want', '收购', '想要', '急求']

    def __init__(self, app_id=None, api_key=None, api_secret=None):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret

    def classify(self, text):
        text_lower = text.lower()

        sell_score = sum(1 for kw in self.SELL_KEYWORDS if kw in text_lower)
        buy_score = sum(1 for kw in self.BUY_KEYWORDS if kw in text_lower)

        if sell_score > buy_score:
            return {
                'type': 'sell',
                'confidence': sell_score / (sell_score + buy_score + 1),
                'scores': {'sell': sell_score, 'buy': buy_score}
            }
        elif buy_score > sell_score:
            return {
                'type': 'buy',
                'confidence': buy_score / (sell_score + buy_score + 1),
                'scores': {'sell': sell_score, 'buy': buy_score}
            }
        else:
            return {
                'type': 'sell',
                'confidence': 0.5,
                'scores': {'sell': sell_score, 'buy': buy_score}
            }

    def classify_with_xunfei(self, text):
        if not self.app_id or not self.api_key:
            return self.classify(text)

        try:
            url = "https://api.xfyun.cn/v1/service/v1/aiui"
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                'app_id': self.app_id,
                'text': text,
                'scene': 'second_hand_market'
            }

            response = requests.post(url, json=data, headers=headers, timeout=5)
            result = response.json()

            if result.get('code') == '000000':
                intent = result.get('data', {}).get('intent', {})
                slot = intent.get('slots', [])
                if slot:
                    return {
                        'type': slot[0].get('type', 'sell'),
                        'confidence': 0.9,
                        'source': 'xunfei'
                    }

        except Exception as e:
            print(f'Xunfei API error: {e}')

        return self.classify(text)

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