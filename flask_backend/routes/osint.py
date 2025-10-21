from flask import Blueprint, request, jsonify
from services.osint_handler import OSINTHandler
from models.osint_result import OSINTResult
from extensions import db
import logging

logger = logging.getLogger(__name__)
osint_bp = Blueprint('osint', __name__)

@osint_bp.route('/', methods=['GET'])
def osint_root():
    """Root OSINT endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'OSINT API is running',
        'endpoints': {
            'search': '/search (POST)',
            'results': '/results (GET)',
            'analyze': '/analyze (POST)',
            'sources': '/sources (GET)',
            'monitor': '/monitor (POST)',
            'investigate-user': '/investigate-user (POST)',
            'tools/status': '/tools/status (GET)'
        }
    }), 200

@osint_bp.route('/search', methods=['POST'])
def search_osint():
    """Perform OSINT search"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Query parameter is required'
            }), 400
        
        query = data['query']
        search_type = data.get('type', 'general')
        
        osint_handler = OSINTHandler()
        results = osint_handler.search(query, search_type)
        
        # Store results in database
        osint_result = OSINTResult(
            query=query,
            search_type=search_type,
            results=results,
            status='completed'
        )
        
        db.session.add(osint_result)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'query': query,
                'search_type': search_type,
                'results': results,
                'result_id': osint_result.id
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@osint_bp.route('/results', methods=['GET'])
def get_osint_results():
    """Get all OSINT search results"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        results_paginated = OSINTResult.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'data': [result.to_dict() for result in results_paginated.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': results_paginated.total,
                'pages': results_paginated.pages
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@osint_bp.route('/results/<int:result_id>', methods=['GET'])
def get_osint_result(result_id):
    """Get specific OSINT result"""
    try:
        result = OSINTResult.query.get_or_404(result_id)
        return jsonify({
            'status': 'success',
            'data': result.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@osint_bp.route('/analyze', methods=['POST'])
def analyze_osint():
    """Analyze OSINT data for threats"""
    try:
        data = request.get_json()
        
        if not data or 'result_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'result_id parameter is required'
            }), 400
        
        result_id = data['result_id']
        osint_result = OSINTResult.query.get_or_404(result_id)
        
        osint_handler = OSINTHandler()
        analysis = osint_handler.analyze_threats(osint_result.results)
        
        # Update result with analysis
        osint_result.analysis = analysis
        osint_result.status = 'analyzed'
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'result_id': result_id,
                'analysis': analysis,
                'threat_level': analysis.get('threat_level', 'low'),
                'findings': analysis.get('findings', [])
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@osint_bp.route('/sources', methods=['GET'])
def get_osint_sources():
    """Get available OSINT sources"""
    try:
        osint_handler = OSINTHandler()
        sources = osint_handler.get_available_sources()
        
        return jsonify({
            'status': 'success',
            'data': sources
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@osint_bp.route('/monitor', methods=['POST'])
def start_monitoring():
    """Start continuous OSINT monitoring"""
    try:
        data = request.get_json()
        
        if not data or 'keywords' not in data:
            return jsonify({
                'status': 'error',
                'message': 'keywords parameter is required'
            }), 400
        
        keywords = data['keywords']
        interval = data.get('interval', 3600)  # Default 1 hour
        
        osint_handler = OSINTHandler()
        monitoring_id = osint_handler.start_monitoring(keywords, interval)
        
        return jsonify({
            'status': 'success',
            'data': {
                'monitoring_id': monitoring_id,
                'keywords': keywords,
                'interval': interval,
                'message': 'Monitoring started successfully'
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@osint_bp.route('/monitor/<monitoring_id>', methods=['DELETE'])
def stop_monitoring(monitoring_id):
    """Stop OSINT monitoring"""
    try:
        osint_handler = OSINTHandler()
        osint_handler.stop_monitoring(monitoring_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Monitoring stopped successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@osint_bp.route('/investigate-user', methods=['POST'])
def investigate_user():
    """Investigate a user using OSINT tools"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Username parameter is required'
            }), 400
        
        username = data['username'].strip()
        platform = data.get('platform', 'Unknown')
        
        if not username:
            return jsonify({
                'status': 'error',
                'message': 'Username cannot be empty'
            }), 400
        
        logger.info(f"Starting user investigation for: {username}")
        
        osint_handler = OSINTHandler()
        results = osint_handler.investigate_user(username, platform)
        
        if results['status'] == 'success':
            logger.info(f"Investigation completed for {username}. Found {len(results['data'].get('linkedProfiles', []))} profiles")
            
            # Track investigation activity
            try:
                from services.activity_tracker import activity_tracker
                from flask_jwt_extended import get_jwt_identity
                
                # Get current user ID from JWT token
                current_user_id = get_jwt_identity()
                if current_user_id:
                    activity_tracker.track_investigation_activity(
                        user_id=current_user_id,
                        username=username,
                        platform=platform,
                        investigation_results=results['data']
                    )
                    logger.info(f"Tracked investigation activity for user {current_user_id}")
            except ImportError as e:
                logger.warning(f"Activity tracker not available: {str(e)}")
            except Exception as e:
                logger.warning(f"Failed to track investigation activity: {str(e)}")
        
        return jsonify(results), 200 if results['status'] == 'success' else 500
        
    except Exception as e:
        logger.error(f"User investigation error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@osint_bp.route('/tools/status', methods=['GET'])
def check_tools_status():
    """Check if OSINT tools are installed and available"""
    try:
        from services.osint_tools import OSINTToolsService
        
        tools_service = OSINTToolsService()
        
        status = {
            'sherlock': {
                'installed': tools_service.sherlock_path.exists(),
                'path': str(tools_service.sherlock_path)
            },
            'spiderfoot': {
                'installed': tools_service.spiderfoot_path.exists(),
                'path': str(tools_service.spiderfoot_path)
            }
        }
        
        return jsonify({
            'status': 'success',
            'tools': status
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
