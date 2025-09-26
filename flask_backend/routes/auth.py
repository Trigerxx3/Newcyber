"""
Authentication routes for system users (analysts/admins)
"""
from flask import Blueprint, request, jsonify, current_app, redirect, url_for, make_response, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import uuid
from authlib.integrations.flask_client import OAuth
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from extensions import db
from models.user import SystemUser, SystemUserRole

auth_bp = Blueprint('auth', __name__)


def _ensure_google_oauth(app):
    """Register Google OAuth client if configured and not already registered."""
    if not hasattr(app, 'oauth'):
        app.oauth = OAuth(app)
    # Check if already registered
    if 'google' in app.oauth._clients:
        return app.oauth
    client_id = app.config.get('GOOGLE_CLIENT_ID')
    client_secret = app.config.get('GOOGLE_CLIENT_SECRET')
    if not client_id or not client_secret:
        return None
    app.oauth.register(
        name='google',
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    return app.oauth

@auth_bp.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        return ("", 204)
    
    try:
        data = request.get_json() or {}
        # Normalize inputs
        raw_email = data.get('email') or ''
        email = raw_email.strip().lower()
        password = (data.get('password') or '')
        username = (data.get('username') or '').strip()
        role_str = (data or {}).get('role', 'Analyst')

        if not email or not password or not username:
            return jsonify({'error': 'Missing email, password, or username'}), 400
        
        # Check if user already exists
        if SystemUser.get_by_email(email):
            return jsonify({'error': 'User already exists'}), 400
        
        # Create new system user
        try:
            role = SystemUserRole(role_str) if isinstance(role_str, str) else SystemUserRole.ANALYST
        except Exception:
            role = SystemUserRole.ANALYST

        user = SystemUser(
            email=email,
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role.value if user.role else 'Analyst'
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/signin', methods=['POST', 'OPTIONS'])
def signin():
    if request.method == 'OPTIONS':
        return ("", 204)
    
    try:
        data = request.get_json() or {}
        print(f"🔐 Signin request data: {data}")
        
        # Normalize inputs
        raw_email = data.get('email') or ''
        email = raw_email.strip().lower()
        password = (data.get('password') or '')
        
        print(f"🔐 Processing login for email: {email} (original: {raw_email})")

        if not email or not password:
            print("❌ Missing email or password")
            return jsonify({'error': 'Missing email or password'}), 400

        user = SystemUser.get_by_email(email)
        print(f"🔐 User found: {user is not None}")
        
        if user:
            password_valid = check_password_hash(user.password_hash, password)
            print(f"🔐 Password valid: {password_valid}")
        
        if not user or not check_password_hash(user.password_hash, password):
            print("❌ Invalid credentials")
            return jsonify({'error': 'Invalid credentials'}), 401

        # Generate JWT token via flask_jwt_extended
        token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'username': user.username,
                'role': user.role.value if user.role else 'Analyst',
            },
            expires_delta=timedelta(hours=24)
        )

        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Login successful',
            'access_token': token,
            'refresh_token': None,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'role': user.role.value if user.role else 'Analyst'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/google/login', methods=['GET'])
def google_login():
    app = current_app
    oauth = _ensure_google_oauth(app)
    if oauth is None:
        return jsonify({'error': 'Google OAuth is not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment.'}), 500
    redirect_uri = url_for('auth.google_callback', _external=True)
    # Generate and store nonce for OIDC validation
    nonce = uuid.uuid4().hex
    session['google_oauth_nonce'] = nonce
    # Prompt select account to make testing easier
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce, prompt='select_account')


@auth_bp.route('/google/callback', methods=['GET'])
def google_callback():
    app = current_app
    oauth = _ensure_google_oauth(app)
    if oauth is None:
        return jsonify({'error': 'Google OAuth is not configured.'}), 500
    try:
        token = oauth.google.authorize_access_token()
        # Validate ID token with stored nonce
        stored_nonce = session.pop('google_oauth_nonce', None)
        userinfo = None
        try:
            userinfo = oauth.google.parse_id_token(token, nonce=stored_nonce)
        except Exception:
            userinfo = None
        if not userinfo:
            # Fallback to userinfo endpoint
            resp = oauth.google.get('userinfo')
            userinfo = resp.json()
        email = (userinfo.get('email') or '').strip().lower()
        if not email:
            return jsonify({'error': 'Email not available from Google account'}), 400
        # Find or create system user
        user = SystemUser.get_by_email(email)
        if not user:
            # Create a username from email local-part
            local_part = email.split('@')[0]
            base_username = local_part if local_part else f'user_{uuid.uuid4().hex[:8]}'
            # Ensure uniqueness if needed
            existing = SystemUser.get_by_username(base_username)
            username = base_username if not existing else f"{base_username}_{uuid.uuid4().hex[:4]}"
            # Set a random password (not used for OAuth)
            random_password = uuid.uuid4().hex
            user = SystemUser(
                email=email,
                username=username,
                password_hash=generate_password_hash(random_password),
                role=SystemUserRole.ANALYST,
                created_at=datetime.utcnow()
            )
            db.session.add(user)
            db.session.commit()
        # Issue JWT
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'username': user.username,
                'role': user.role.value if user.role else 'Analyst',
            },
            expires_delta=timedelta(hours=24)
        )
        user.last_login = datetime.utcnow()
        db.session.commit()

        # Return small HTML that posts message to opener and closes
        html = f"""
<!doctype html>
<html>
  <body>
    <script>
      try {{
        const payload = {{ type: 'oauth', provider: 'google', access_token: '{access_token}', refresh_token: null }};
        if (window.opener && !window.opener.closed) {{
          window.opener.postMessage(payload, '*');
        }}
      }} catch (e) {{}}
      window.close();
    </script>
    <p>You can close this window.</p>
  </body>
</html>
"""
        response = make_response(html)
        response.headers['Content-Type'] = 'text/html'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET', 'OPTIONS'])
@jwt_required()
def profile():
    if request.method == 'OPTIONS':
        return ("", 204)
    
    ident = get_jwt_identity()
    user_id = ident
    # Ensure identity is an integer ID
    try:
        user_id = int(user_id) if user_id is not None else None
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid token'}), 401
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    user = SystemUser.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'role': user.role.value if user.role else 'Analyst',
        'last_login': user.last_login.isoformat() if user.last_login else None,
    }}), 200

