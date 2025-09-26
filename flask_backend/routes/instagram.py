from flask import Blueprint, jsonify, request
from auth import require_auth, require_role
from services.instagram_scraper_db import get_instagram_scraper_db

instagram_bp = Blueprint('instagram', __name__)


@instagram_bp.route('/instagram/profile/<username>', methods=['GET'])
@require_auth
@require_role('Admin')
def scrape_profile(username):
	scraper = get_instagram_scraper_db()
	result = scraper.scrape_user_posts(username, max_posts=10)
	status = 200 if 'error' not in result else 400
	return jsonify(result), status


@instagram_bp.route('/instagram/hashtag/<tag>', methods=['GET'])
@require_auth
@require_role('Admin')
def scrape_hashtag(tag):
	limit = request.args.get('limit', default=10, type=int)
	scraper = get_instagram_scraper_db()
	result = scraper.scrape_hashtag_posts(tag, max_posts=limit)
	status = 200 if 'error' not in result else 400
	return jsonify(result), status


@instagram_bp.route('/instagram/post', methods=['GET'])
@require_auth
@require_role('Admin')
def scrape_post():
	post_url = request.args.get('url')
	if not post_url:
		return jsonify({"error": "Missing 'url' query parameter"}), 400
	scraper = get_instagram_scraper_db()
	# Extract shortcode from URL for comment scraping
	if '/p/' in post_url:
		shortcode = post_url.split('/p/')[1].split('/')[0]
		comments = scraper.get_post_comments(shortcode, max_comments=20)
		result = {'url': post_url, 'shortcode': shortcode, 'comments': comments, 'posts': []}
	else:
		result = {'error': 'Invalid Instagram post URL'}
	status = 200 if 'error' not in result else 400
	return jsonify(result), status

# Aliases without prefix in case blueprint is mounted at /api
@instagram_bp.route('/profile/<username>', methods=['GET'])
@require_auth
@require_role('Admin')
def scrape_profile_alias(username):
	return scrape_profile(username)


@instagram_bp.route('/hashtag/<tag>', methods=['GET'])
@require_auth
@require_role('Admin')
def scrape_hashtag_alias(tag):
	return scrape_hashtag(tag)


@instagram_bp.route('/post', methods=['GET'])
@require_auth
@require_role('Admin')
def scrape_post_alias():
	return scrape_post()
