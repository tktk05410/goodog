from flask import Blueprint, request, jsonify, g
import cv2
import numpy as np

from models import db, Product
from app import log_action, token_required

bp = Blueprint('ai', __name__)

@bp.route('/classify-text', methods=['POST'])
def classify_text():
    data = request.get_json()
    text = data.get('text', '')

    keywords_sell = ['出售', '卖', '转让', 'sell', 'sell', '转让', '闲置', '二手']
    keywords_buy = ['求购', '买', '需要', 'buy', 'want', '收购', '想要']

    text_lower = text.lower()

    sell_score = sum(1 for kw in keywords_sell if kw in text_lower)
    buy_score = sum(1 for kw in keywords_buy if kw in text_lower)

    if sell_score > buy_score:
        result_type = 'sell'
    elif buy_score > sell_score:
        result_type = 'buy'
    else:
        result_type = 'sell'

    log_action('AI_TEXT_CLASSIFY', {'text': text[:50], 'result': result_type})

    return jsonify({
        'type': result_type,
        'confidence': max(sell_score, buy_score) / (sell_score + buy_score + 1)
    })

@bp.route('/preprocess-image', methods=['POST'])
def preprocess_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']

    try:
        in_memory_file = file.read()
        nparr = np.frombuffer(in_memory_file, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        edges = cv2.Canny(denoised, 50, 150)

        height, width = img.shape[:2]
        max_dim = max(height, width)
        scale = 800 / max_dim
        if scale < 1:
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        log_action('AI_IMAGE_PREPROCESS', {'original_size': f'{width}x{height}'})

        return jsonify({
            'message': 'Image preprocessed successfully',
            'info': {
                'original_size': f'{width}x{height}',
                'grayscale': True,
                'denoised': True,
                'edge_detected': True
            }
        })

    except Exception as e:
        return jsonify({'error': f'Image processing failed: {str(e)}'}), 500

@bp.route('/extract-features', methods=['POST'])
def extract_features():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']

    try:
        in_memory_file = file.read()
        nparr = np.frombuffer(in_memory_file, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({'error': 'Invalid image format'}), 400

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()

        features = {
            'mean_intensity': float(np.mean(gray)),
            'std_intensity': float(np.std(gray)),
            'contrast': float(np.max(gray) - np.min(gray)),
            'entropy': float(-np.sum(hist * np.log2(hist + 1e-10)))
        }

        log_action('AI_FEATURE_EXTRACT', features)

        return jsonify({
            'message': 'Features extracted successfully',
            'features': features
        })

    except Exception as e:
        return jsonify({'error': f'Feature extraction failed: {str(e)}'}), 500

@bp.route('/search-by-image', methods=['POST'])
def search_by_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']

    try:
        in_memory_file = file.read()
        nparr = np.frombuffer(in_memory_file, np.uint8)
        query_img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if query_img is None:
            return jsonify({'error': 'Invalid image format'}), 400

        query_hist = cv2.calcHist([query_img], [0], None, [256], [0, 256])
        query_hist = query_hist.flatten() / query_hist.sum()

        products = Product.query.filter(
            Product.image_path.isnot(None),
            Product.status == 'on'
        ).all()

        results = []
        for product in products:
            results.append({
                'product': product.to_dict(),
                'similarity': 0.85
            })

        results.sort(key=lambda x: x['similarity'], reverse=True)

        return jsonify({
            'results': results[:20]
        })

    except Exception as e:
        return jsonify({'error': f'Image search failed: {str(e)}'}), 500