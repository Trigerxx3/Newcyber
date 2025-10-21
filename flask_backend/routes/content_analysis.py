"""
Content Analysis API routes for NLP-based drug content detection
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from auth import require_auth, require_role
from extensions import db
from models.content import Content, ContentStatus, RiskLevel, ContentType
from models.source import Source, PlatformType, SourceType
from models.user import SystemUser
from services.content_analysis import analyze_content
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

content_analysis_bp = Blueprint('content_analysis', __name__)

@content_analysis_bp.route('/analyze', methods=['POST'])
@require_auth
def analyze_content_endpoint():
    """
    Analyze content for drug-related keywords and intent detection
    
    Expected JSON payload:
    {
        "platform": "Instagram",
        "username": "drugdealer123", 
        "content": "Buy LSD cheap 💊 DM me",
        "save_to_database": true  // Optional: whether to save results to database (default: true)
    }
    
    Returns:
    {
        "platform": "Instagram",
        "username": "drugdealer123",
        "text": "Buy LSD cheap 💊 DM me",
        "matched_keywords": ["lsd", "💊"],
        "intent": "Selling",
        "suspicion_score": 85,
        "is_flagged": true,
        "confidence": 0.9,
        "analysis_data": {...},
        "content_id": 123,  // null if save_to_database is false
        "saved_to_database": true
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'content' not in data or not data['content']:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: content'
            }), 400
        
        # Use provided values or defaults
        platform = data.get('platform', 'Unknown')
        username = data.get('username', 'Anonymous')
        content_text = data['content']
        save_to_database = data.get('save_to_database', True)  # Default to True for backward compatibility
        
        # Validate platform (allow Unknown as default)
        valid_platforms = ['Instagram', 'Telegram', 'WhatsApp', 'Facebook', 'Twitter', 'TikTok', 'Unknown']
        if platform not in valid_platforms:
            return jsonify({
                'status': 'error',
                'message': f'Invalid platform. Must be one of: {", ".join(valid_platforms)}'
            }), 400
        
        # Get current user
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'User not authenticated'
            }), 401
        
        current_user = SystemUser.query.get(int(user_id))
        if not current_user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Convert platform to PlatformType enum safely
        try:
            platform_enum = PlatformType(platform)
        except ValueError:
            platform_enum = PlatformType.UNKNOWN
        
        # Analyze content using NLP service
        analysis_result = analyze_content(content_text)
        
        # Only save to database if requested
        content_id = None
        if save_to_database:
            # Find or create source
            source = Source.query.filter_by(
                platform=platform_enum,
                source_handle=username
            ).first()
            
            if not source:
                # Create new source
                source = Source(
                    platform=platform_enum,
                    source_handle=username,
                    source_name=username,
                    source_type=SourceType.PROFILE,
                    is_active=True
                )
                db.session.add(source)
                db.session.flush()  # Get the ID
            
            # Create content record
            content = Content(
                source_id=source.id,
                created_by_id=current_user.id,
                text=content_text,
                author=username,
                content_type=ContentType.TEXT,
                risk_level=RiskLevel.HIGH if analysis_result.is_flagged else RiskLevel.LOW,
                status=ContentStatus.ANALYZED,
                keywords=analysis_result.matched_keywords,
                analysis_summary=f"Intent: {analysis_result.intent}, Score: {analysis_result.suspicion_score}",
                analysis_data=analysis_result.analysis_data,
                suspicion_score=analysis_result.suspicion_score,
                intent=analysis_result.intent,
                is_flagged=analysis_result.is_flagged,
                word_count=len(content_text.split()),
                character_count=len(content_text),
                confidence_score=analysis_result.confidence,
                processing_time=analysis_result.processing_time,
                analysis_version='nlp-v1.0',
                last_analyzed=datetime.utcnow()
            )
            
            db.session.add(content)
            db.session.commit()
            content_id = content.id
        
        # Track content analysis activity
        try:
            from services.activity_tracker import activity_tracker
            
            # Prepare analysis results for activity tracking
            analysis_results = {
                'suspicion_score': analysis_result.suspicion_score,
                'intent': analysis_result.intent,
                'is_flagged': analysis_result.is_flagged,
                'matched_keywords': analysis_result.matched_keywords,
                'confidence': analysis_result.confidence,
                'analysis_data': analysis_result.analysis_data
            }
            
            activity_tracker.track_content_analysis_activity(
                user_id=current_user.id,
                content_text=content_text,
                platform=platform,
                username=username,
                analysis_results=analysis_results,
                content_id=content_id
            )
            logger.info(f"Tracked content analysis activity for user {current_user.id}")
        except ImportError as e:
            logger.warning(f"Activity tracker not available: {str(e)}")
        except Exception as e:
            logger.warning(f"Failed to track content analysis activity: {str(e)}")
        
        # Prepare response
        response_data = {
            'status': 'success',
            'platform': platform,
            'username': username,
            'text': content_text,
            'matched_keywords': analysis_result.matched_keywords,
            'intent': analysis_result.intent,
            'suspicion_score': analysis_result.suspicion_score,
            'is_flagged': analysis_result.is_flagged,
            'confidence': analysis_result.confidence,
            'analysis_data': analysis_result.analysis_data,
            'content_id': content_id,  # Will be None if not saved to database
            'processing_time': analysis_result.processing_time,
            'saved_to_database': save_to_database
        }
        
        return jsonify(response_data), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Analysis error: {str(e)}'
        }), 500

@content_analysis_bp.route('/analyze-batch', methods=['POST'])
@require_auth
def analyze_batch_content():
    """
    Analyze multiple content items in batch
    
    Expected JSON payload:
    {
        "platform": "Instagram",
        "content_items": [
            {
                "username": "user1",
                "content": "text content 1"
            },
            {
                "username": "user2", 
                "content": "text content 2"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if 'content_items' not in data or not data['content_items']:
            return jsonify({
                'status': 'error',
                'message': 'Missing required field: content_items'
            }), 400
        
        platform = data.get('platform', 'Unknown')
        content_items = data['content_items']
        
        # Get current user
        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'User not authenticated'
            }), 401
        
        current_user = SystemUser.query.get(int(user_id))
        if not current_user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Analyze each content item
        results = []
        flagged_count = 0
        
        for item in content_items:
            try:
                username = item.get('username', 'Anonymous')
                content_text = item.get('content', '')
                
                if not content_text:
                    continue
                
                # Analyze content
                analysis_result = analyze_content(content_text)
                
                # Track individual content analysis
                try:
                    from services.activity_tracker import activity_tracker
                    
                    analysis_results = {
                        'suspicion_score': analysis_result.suspicion_score,
                        'intent': analysis_result.intent,
                        'is_flagged': analysis_result.is_flagged,
                        'matched_keywords': analysis_result.matched_keywords,
                        'confidence': analysis_result.confidence,
                        'analysis_data': analysis_result.analysis_data
                    }
                    
                    activity_tracker.track_content_analysis_activity(
                        user_id=current_user.id,
                        content_text=content_text,
                        platform=platform,
                        username=username,
                        analysis_results=analysis_results
                    )
                except ImportError as e:
                    logger.warning(f"Activity tracker not available: {str(e)}")
                except Exception as e:
                    logger.warning(f"Failed to track individual content analysis: {str(e)}")
                
                if analysis_result.is_flagged:
                    flagged_count += 1
                
                results.append({
                    'username': username,
                    'content': content_text,
                    'suspicion_score': analysis_result.suspicion_score,
                    'intent': analysis_result.intent,
                    'is_flagged': analysis_result.is_flagged,
                    'matched_keywords': analysis_result.matched_keywords
                })
                
            except Exception as e:
                logger.error(f"Error analyzing content item: {str(e)}")
                continue
        
        # Track batch analysis activity
        try:
            from services.activity_tracker import activity_tracker
            
            batch_results = [{
                'suspicion_score': r['suspicion_score'],
                'is_flagged': r['is_flagged'],
                'intent': r['intent']
            } for r in results]
            
            activity_tracker.track_batch_analysis_activity(
                user_id=current_user.id,
                batch_results=batch_results,
                platform=platform
            )
            logger.info(f"Tracked batch analysis activity for user {current_user.id}")
        except ImportError as e:
            logger.warning(f"Activity tracker not available: {str(e)}")
        except Exception as e:
            logger.warning(f"Failed to track batch analysis activity: {str(e)}")
        
        return jsonify({
            'status': 'success',
            'platform': platform,
            'total_analyzed': len(results),
            'flagged_count': flagged_count,
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Batch analysis error: {str(e)}'
        }), 500

@content_analysis_bp.route('/flagged', methods=['GET'])
@require_auth
def get_flagged_content():
    """
    Get all flagged content (suspicion_score >= 70)
    
    Query parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 20, max: 100)
    - min_score: Minimum suspicion score (default: 70)
    - intent: Filter by intent (Selling, Buying, Informational, Unknown)
    - platform: Filter by platform
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        min_score = request.args.get('min_score', 70, type=int)
        intent_filter = request.args.get('intent')
        platform_filter = request.args.get('platform')
        
        # Build query
        query = Content.query.filter(Content.is_flagged == True)
        
        if min_score is not None:
            query = query.filter(Content.suspicion_score >= min_score)
        
        if intent_filter:
            query = query.filter(Content.intent == intent_filter)
        
        if platform_filter:
            query = query.join(Source).filter(Source.platform == PlatformType(platform_filter.lower()))
        
        # Order by suspicion score (highest first)
        query = query.order_by(Content.suspicion_score.desc(), Content.created_at.desc())
        
        # Get paginated results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        content_data = []
        for content in pagination.items:
            content_dict = content.to_dict()
            # Add source information
            if content.source:
                content_dict['source'] = {
                    'platform': content.source.platform.value if content.source.platform else None,
                    'source_handle': content.source.source_handle,
                    'source_name': content.source.source_name
                }
            content_data.append(content_dict)
        
        return jsonify({
            'status': 'success',
            'data': content_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500

@content_analysis_bp.route('/stats', methods=['GET'])
@require_auth
def get_analysis_stats():
    """
    Get analysis statistics
    """
    try:
        # Total content analyzed
        total_content = Content.query.filter(Content.status == ContentStatus.ANALYZED).count()
        
        # Flagged content
        flagged_content = Content.query.filter(Content.is_flagged == True).count()
        
        # Intent distribution
        intent_stats = db.session.query(
            Content.intent,
            db.func.count(Content.id)
        ).filter(Content.status == ContentStatus.ANALYZED).group_by(Content.intent).all()
        
        # Platform distribution
        platform_stats = db.session.query(
            Source.platform,
            db.func.count(Content.id)
        ).join(Content).filter(Content.status == ContentStatus.ANALYZED).group_by(Source.platform).all()
        
        # Risk level distribution
        risk_stats = db.session.query(
            Content.risk_level,
            db.func.count(Content.id)
        ).filter(Content.status == ContentStatus.ANALYZED).group_by(Content.risk_level).all()
        
        # Average suspicion score
        avg_score = db.session.query(db.func.avg(Content.suspicion_score)).filter(
            Content.status == ContentStatus.ANALYZED
        ).scalar() or 0
        
        # High suspicion content (score >= 80)
        high_suspicion = Content.query.filter(
            Content.suspicion_score >= 80,
            Content.status == ContentStatus.ANALYZED
        ).count()
        
        stats = {
            'total_analyzed': total_content,
            'flagged_content': flagged_content,
            'flag_rate': (flagged_content / total_content * 100) if total_content > 0 else 0,
            'average_suspicion_score': round(avg_score, 2),
            'high_suspicion_content': high_suspicion,
            'intent_distribution': {intent: count for intent, count in intent_stats},
            'platform_distribution': {platform.value if platform else 'Unknown': count for platform, count in platform_stats},
            'risk_distribution': {risk.value if risk else 'Unknown': count for risk, count in risk_stats}
        }
        
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
        
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500

@content_analysis_bp.route('/<int:content_id>/flag', methods=['PUT'])
@require_auth
def update_content_flag(content_id):
    """
    Update content flag status (manual override)
    """
    try:
        data = request.get_json()
        
        content = Content.query.get(content_id)
        if not content:
            return jsonify({
                'status': 'error',
                'message': 'Content not found'
            }), 404
        
        # Update flag status
        if 'is_flagged' in data:
            content.is_flagged = bool(data['is_flagged'])
        
        if 'suspicion_score' in data:
            score = data['suspicion_score']
            if not isinstance(score, int) or not (0 <= score <= 100):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid suspicion score (must be integer 0-100)'
                }), 400
            content.suspicion_score = score
        
        if 'intent' in data:
            valid_intents = ['Selling', 'Buying', 'Informational', 'Unknown']
            if data['intent'] not in valid_intents:
                return jsonify({
                    'status': 'error',
                    'message': f'Invalid intent (must be one of: {", ".join(valid_intents)})'
                }), 400
            content.intent = data['intent']
        
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Content flag updated successfully',
            'data': content.to_dict()
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }), 500

@content_analysis_bp.route('/scraped-content', methods=['GET'])
@require_auth
def get_scraped_content_for_analysis():
    """
    Get scraped content for analysis pipeline (available to all authenticated users)
    
    Query parameters:
    - limit: Maximum number of items to return (default: 100, max: 500)
    - platform: Filter by platform
    - risk_level: Filter by risk level
    - status: Filter by content status
    """
    try:
        limit = min(request.args.get('limit', 100, type=int), 500)
        platform_filter = request.args.get('platform')
        risk_level_filter = request.args.get('risk_level')
        status_filter = request.args.get('status')
        
        # Build query
        query = Content.query
        
        # Apply filters
        if platform_filter:
            try:
                # Handle case-insensitive platform matching
                platform_upper = platform_filter.upper()
                if platform_upper == 'UNKNOWN':
                    platform_enum = PlatformType.UNKNOWN
                elif platform_upper == 'TELEGRAM':
                    platform_enum = PlatformType.TELEGRAM
                elif platform_upper == 'INSTAGRAM':
                    platform_enum = PlatformType.INSTAGRAM
                elif platform_upper == 'WHATSAPP':
                    platform_enum = PlatformType.WHATSAPP
                elif platform_upper == 'FACEBOOK':
                    platform_enum = PlatformType.FACEBOOK
                elif platform_upper == 'TWITTER':
                    platform_enum = PlatformType.TWITTER
                elif platform_upper == 'TIKTOK':
                    platform_enum = PlatformType.TIKTOK
                else:
                    platform_enum = PlatformType.UNKNOWN
                
                query = query.join(Source).filter(Source.platform == platform_enum)
            except Exception:
                pass  # Invalid platform, ignore filter
        
        if risk_level_filter:
            query = query.filter(Content.risk_level == risk_level_filter)
        
        if status_filter:
            query = query.filter(Content.status == status_filter)
        
        # Order by creation date (newest first)
        content_items = query.order_by(Content.created_at.desc()).limit(limit).all()
        
        content_data = []
        for item in content_items:
            # Get source information
            source = item.source if hasattr(item, 'source') else None
            platform = source.platform.value if source and hasattr(source.platform, 'value') else 'Unknown'
            source_handle = source.source_handle if source else 'Unknown'
            
            content_data.append({
                'id': str(item.id),
                'source_handle': source_handle,
                'platform': platform,
                'text': item.text or '',
                'author': item.author or source_handle,
                'posted_at': item.created_at.isoformat() if item.created_at else '',
                'risk_level': item.risk_level.value if item.risk_level else 'Low',
                'status': item.status.value if item.status else 'New',
                'keywords': item.keywords if item.keywords else [],
                'analysis_summary': item.analysis_summary or '',
                'is_analyzed': bool(item.analysis_summary and item.suspicion_score is not None),
                'suspicion_score': item.suspicion_score or 0,
                'intent': item.intent or 'Unknown',
                'is_flagged': item.is_flagged or False
            })
        
        return jsonify(content_data), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch scraped content: {str(e)}'
        }), 500
