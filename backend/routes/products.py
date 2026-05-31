from flask import Blueprint, request, jsonify, g
from sqlalchemy import or_

from models import db, Product
from app import log_action, token_required, allowed_file, save_uploaded_file

bp = Blueprint('products', __name__)

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
        query = query.filter(or_(
            Product.title.like(f'%{keyword}%'),
            Product.description.like(f'%{keyword}%')
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