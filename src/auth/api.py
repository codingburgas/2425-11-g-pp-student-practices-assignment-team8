from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from .models import User
from .. import db

auth_api_bp = Blueprint('auth_api', __name__)

@auth_api_bp.route('/login', methods=['POST'])
def api_login():
    """
    API endpoint for user login
    Returns JWT tokens for authentication
    """
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Create tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }), 200

@auth_api_bp.route('/register', methods=['POST'])
def api_register():
    """
    API endpoint for user registration
    """
    if not request.is_json:
        return jsonify({"error": "Missing JSON in request"}), 400
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    email = request.json.get('email', None)

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 409
    
    if not email:
        return jsonify({"error": "Missing email"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    new_user = User(
        username=username,
        email=email,
        role='client',
    )
    new_user.password = password
    
    db.session.add(new_user)
    db.session.commit()
    
    # Create tokens for the new user
    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)
    
    return jsonify({
        "message": "User registered successfully",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": new_user.id,
        "username": new_user.username,
        "role": new_user.role
    }), 201

@auth_api_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    API endpoint to refresh access token using refresh token
    """
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        "access_token": access_token
    }), 200

@auth_api_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    return jsonify({
        "message": f"Hello, {user.username}! This is a protected endpoint.",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }), 200