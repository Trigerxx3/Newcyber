"""
Authentication system using SQLAlchemy and JWT
"""
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, verify_jwt_in_request
)
from werkzeug.security import check_password_hash
from models.user import SystemUser, SystemUserRole
from extensions import db
from datetime import datetime
import re

class Auth:
    """Authentication class for user management"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, "Password is valid"
    
    @staticmethod
    def register_user(email, password, username, role='Analyst'):
        """Register new system user"""
        try:
            # Validate inputs
            if not Auth.validate_email(email):
                return {'success': False, 'error': 'Invalid email format'}
            
            is_valid, message = Auth.validate_password(password)
            if not is_valid:
                return {'success': False, 'error': message}
            
            # Check if user already exists
            if SystemUser.get_by_email(email):
                return {'success': False, 'error': 'User with this email already exists'}
            
            if SystemUser.get_by_username(username):
                return {'success': False, 'error': 'Username already taken'}
            
            # Validate role
            try:
                user_role = SystemUserRole(role)
            except ValueError:
                return {'success': False, 'error': 'Invalid role'}
            
            # Create user
            user = SystemUser(
                email=email,
                username=username,
                role=user_role
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'User registered successfully',
                'user': user.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Registration failed: {str(e)}'}
    
    @staticmethod
    def login_user(email, password):
        """Login system user"""
        try:
            # Find user by email
            user = SystemUser.get_by_email(email)
            if not user:
                return {'success': False, 'error': 'Invalid email or password'}
            
            # Check if user is active
            if not user.is_active:
                return {'success': False, 'error': 'Account is disabled'}
            
            # Verify password
            if not user.check_password(password):
                return {'success': False, 'error': 'Invalid email or password'}
            
            # Update last login
            user.update_last_login()
            
            # Create tokens
            access_token = create_access_token(
                identity={
                    'user_id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role.value
                }
            )
            
            refresh_token = create_refresh_token(
                identity={
                    'user_id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'role': user.role.value
                }
            )
            
            return {
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Login failed: {str(e)}'}
    
    @staticmethod
    def get_current_user():
        """Get current authenticated user"""
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            if not user_id:
                return None
            
            # user_id is a string, not a dict
            user = SystemUser.query.get(int(user_id))
            return user
        except Exception as e:
            print(f"Debug: get_current_user error: {e}")
            return None

# Decorators
def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = Auth.get_current_user()
        if not current_user:
            return jsonify({'error': 'Authentication required'}), 401
        
        if not current_user.is_active:
            return jsonify({'error': 'Account is disabled'}), 401
        
        # Add user to request context
        request.current_user = current_user
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user = Auth.get_current_user()
            if not current_user:
                return jsonify({'error': 'Authentication required'}), 401
            
            if not current_user.is_active:
                return jsonify({'error': 'Account is disabled'}), 401
            
            # Check role
            if isinstance(required_role, str):
                if current_user.role.value != required_role:
                    return jsonify({'error': 'Insufficient permissions'}), 403
            elif isinstance(required_role, list):
                if current_user.role.value not in required_role:
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            # Add user to request context
            request.current_user = current_user
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return require_role('Admin')(f)(*args, **kwargs)
    
    return decorated_function
