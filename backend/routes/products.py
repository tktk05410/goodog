from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_

from models import db, Product, Tag, ProductTag
from app import log_action, token_required, allowed_file, save_uploaded_file

bp = Blueprint('products', __name__)

def auto_generate_tags(product):
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from ai_services.text_classifier import TextClassifier
    from ai_services.image_processor import ImageProcessor

    text_tags = []
    image_tags = []

    try:
        classifier = TextClassifier()
        text_result = classifier.generate_tags_with_qwen(product.title, product.description)
        text_tags = text_result.get('tags', [])
    except Exception as e:
        print(f'Text tag generation error: {e}')

    if product.image_path:
        try:
            image_path = os.path.join('d:\\End-of-term Professional Comprehensive Practice\\project\\goodog\\uploads', product.image_path)
            if os.path.exists(image_path):
                classifier = TextClassifier()
                image_result = ImageProcessor.recognize_with_qwen(
                    image_path,
                    classifier.api_key,
                    classifier.base_url
                )
                image_tags = image_result.get('tags', [])
        except Exception as e:
            print(f'Image tag generation error: {e}')

    all_tags = list(set(text_tags + image_tags))[:8]

    for tag_name in all_tags:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name, color='#409eff', is_ai_generated=True)
            db.session.add(tag)
            db.session.flush()

        existing = ProductTag.query.filter_by(product_id=product.id, tag_id=tag.id).first()
        if not existing:
            product_tag = ProductTag(
                product_id=product.id,
                tag_id=tag.id,
                is_ai_generated=True
            )
            db.session.add(product_tag)

    log_action('AI_AUTO_TAG', {
        'product_id': product.id,
        'tags': all_tags,
        'text_tags': text_tags,
        'image_tags': image_tags
    })

    return all_tags

@bp.route('/', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    type_filter = request.args.get('type')
    status_filter = request.args.get('status', 'on')
    keyword = request.args.get('keyword')

    query = Product.query

    if type_filter:
        query = query.filter(Product.type == type_filter)

    if status_filter:
        query = query.filter(Product.status == status_filter)

    if keyword:
        product_ids_with_tag = db.session.query(ProductTag.product_id).join(
            Tag, ProductTag.tag_id == Tag.id
        ).filter(
            Tag.name.like(f'%{keyword}%')
        ).subquery()

        query = query.filter(or_(
            Product.title.like(f'%{keyword}%'),
            Product.description.like(f'%{keyword}%'),
            Product.id.in_(product_ids_with_tag)
        ))

    pagination = query.order_by(Product.create_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'products': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify({'product': product.to_dict()})

@bp.route('/', methods=['POST'])
@token_required
def create_product():
    title = request.form.get('title')
    description = request.form.get('description')
    type_val = request.form.get('type')
    price = request.form.get('price')
    image = request.files.get('image')

    if not title or not description or not type_val:
        return jsonify({'error': 'Title, description and type are required'}), 400

    if type_val not in ['sell', 'buy']:
        return jsonify({'error': 'Type must be sell or buy'}), 400

    image_path = None
    if image:
        image_path = save_uploaded_file(image)
        if not image_path:
            return jsonify({'error': 'Invalid image file'}), 400

    product = Product(
        title=title,
        description=description,
        type=type_val,
        price=float(price) if price else None,
        image_path=image_path,
        user_id=g.user.id
    )

    db.session.add(product)
    db.session.commit()

    auto_generate_tags(product)
    db.session.commit()

    log_action('PRODUCT_CREATE', {
        'product_id': product.id,
        'title': title,
        'type': type_val
    })

    return jsonify({
        'message': 'Product created successfully',
        'product': product.to_dict()
    }), 201

@bp.route('/<int:product_id>', methods=['PUT'])
@token_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.user_id != g.user.id:
        return jsonify({'error': 'You can only update your own products'}), 403

    title = request.form.get('title', product.title)
    description = request.form.get('description', product.description)
    price = request.form.get('price', product.price)
    status = request.form.get('status', product.status)
    image = request.files.get('image')

    product.title = title
    product.description = description
    product.price = float(price) if price else product.price
    product.status = status

    if image:
        image_path = save_uploaded_file(image)
        if image_path:
            product.image_path = image_path

    db.session.commit()

    log_action('PRODUCT_UPDATE', {'product_id': product.id})

    return jsonify({
        'message': 'Product updated successfully',
        'product': product.to_dict()
    })

@bp.route('/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.user_id != g.user.id:
        return jsonify({'error': 'You can only delete your own products'}), 403

    db.session.delete(product)
    db.session.commit()

    log_action('PRODUCT_DELETE', {'product_id': product_id})

    return jsonify({'message': 'Product deleted successfully'})

@bp.route('/my', methods=['GET'])
@token_required
def get_my_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Product.query.filter_by(user_id=g.user.id).order_by(
        Product.create_time.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'products': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })