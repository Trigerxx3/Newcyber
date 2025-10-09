"""
Instagram scraping service that persists data to the database
"""
import logging
from typing import Dict, List, Any
from datetime import datetime

try:
    import instaloader
except ImportError:
    instaloader = None

from extensions import db
from models.source import Source, PlatformType, SourceType
from models.user import User
from models.content import Content, ContentType, RiskLevel
from services.keyword_detector import KeywordDetector

logger = logging.getLogger(__name__)


class InstagramScraperDB:
    """Instagram scraper that saves data to the database"""

    def __init__(self):
        self.detector = KeywordDetector()
        if instaloader is not None:
            self.loader = instaloader.Instaloader(
                download_pictures=False,
                download_videos=False,
                download_video_thumbnails=False,
                download_geotags=False,
                save_metadata=False,
                compress_json=False,
                post_metadata_txt_pattern=""
            )
        else:
            self.loader = None

    def _ensure_instaloader(self):
        if self.loader is None:
            raise RuntimeError("Instaloader is not installed. Please install with: pip install instaloader")

    def _get_or_create_source(self, handle: str, name: str, source_type: SourceType) -> Source:
        source = Source.query.filter_by(source_handle=handle, platform=PlatformType.INSTAGRAM).first()
        if not source:
            source = Source(
                platform=PlatformType.INSTAGRAM,
                source_handle=handle,
                source_name=name,
                source_type=source_type,
                description=f"Auto-created for Instagram {source_type.value.lower()} {handle}",
                is_active=True,
            )
            db.session.add(source)
            db.session.flush()
        return source

    def _get_or_create_user(self, source: Source, username: str, full_name: str = None, bio: str = None) -> User:
        user = User.query.filter_by(source_id=source.id, username=username).first()
        if not user:
            user = User(
                source_id=source.id,
                username=username,
                full_name=full_name,
                bio=bio
            )
            db.session.add(user)
            db.session.flush()
        else:
            # Update user info
            if full_name:
                user.full_name = full_name
            if bio:
                user.bio = bio
        return user

    def _analyze_and_save_content(self, source: Source, text: str, author: str, url: str = None) -> Dict[str, Any]:
        # Analyze content for keywords and risk
        analysis = self.detector.analyze_content(text or "")
        suspicion_score = max(0, min(int(analysis.get("risk_score", 0)), 100))
        
        # Determine risk level
        if suspicion_score >= 50:
            risk_level = RiskLevel.CRITICAL
        elif suspicion_score >= 30:
            risk_level = RiskLevel.HIGH
        elif suspicion_score >= 15:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW

        # Save content to database
        content = Content(
            source_id=source.id,
            text=text or "",
            url=url or "",
            author=author or "Unknown",
            content_type=ContentType.TEXT,
            risk_level=risk_level,
            keywords=analysis.get("keywords", []),
            analysis_summary=analysis.get("analysis", ""),
            analysis_data={
                "suspicion_score": suspicion_score,
                "category_details": analysis.get("category_details", {}),
                "match_counts": analysis.get("match_counts", {}),
                "platform": "Instagram"
            }
        )
        db.session.add(content)
        db.session.flush()

        return {
            "content_id": content.id,
            "text_content": content.text,
            "suspicion_score": suspicion_score,
            "posted_at": datetime.utcnow().isoformat(),
            "analysis": analysis.get("analysis", "")
        }

    def scrape_user_posts(self, username: str, max_posts: int = 10) -> Dict[str, Any]:
        """Scrape Instagram user posts and save to database"""
        self._ensure_instaloader()
        
        try:
            logger.info(f"🔍 Scraping Instagram profile: {username}")
            
            # Get profile
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            if profile.is_private:
                return {
                    "error": "Private profile. Cannot scrape.",
                    "username": username,
                    "scraped_count": 0,
                    "posts": []
                }

            # Create or get source
            source = self._get_or_create_source(
                handle=username,
                name=profile.full_name or username,
                source_type=SourceType.PROFILE
            )

            # Create or update user
            user = self._get_or_create_user(
                source=source,
                username=username,
                full_name=profile.full_name,
                bio=profile.biography
            )

            # Scrape posts
            posts_data = []
            count = 0
            
            for post in profile.get_posts():
                if count >= max_posts:
                    break
                    
                try:
                    caption = post.caption or ""
                    post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                    
                    # Save content and get analysis
                    content_data = self._analyze_and_save_content(
                        source=source,
                        text=caption,
                        author=username,
                        url=post_url
                    )
                    posts_data.append(content_data)
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing post: {e}")
                    continue

            # Update source last scraped time
            source.last_scraped_at = datetime.utcnow()
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"✅ Successfully scraped {len(posts_data)} posts from @{username}")
            
            return {
                "source": {
                    "platform": "Instagram",
                    "source_handle": username,
                    "source_type": "Profile"
                },
                "user": {
                    "username": username,
                    "bio": profile.biography or "",
                    "full_name": profile.full_name or ""
                },
                "posts": posts_data,
                "scraped_count": len(posts_data)
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to scrape Instagram profile {username}: {e}")
            return {
                "error": str(e),
                "username": username,
                "scraped_count": 0,
                "posts": []
            }

    def scrape_hashtag_posts(self, hashtag: str, max_posts: int = 10) -> Dict[str, Any]:
        """Scrape Instagram hashtag posts and save to database"""
        self._ensure_instaloader()
        
        try:
            logger.info(f"🔍 Scraping Instagram hashtag: #{hashtag}")
            
            # Create or get source for hashtag
            handle = f"#{hashtag}"
            source = self._get_or_create_source(
                handle=handle,
                name=handle,
                source_type=SourceType.GROUP
            )

            # Scrape hashtag posts
            posts_data = []
            count = 0
            
            hashtag_obj = instaloader.Hashtag.from_name(self.loader.context, hashtag)
            
            for post in hashtag_obj.get_posts():
                if count >= max_posts:
                    break
                    
                try:
                    caption = post.caption or ""
                    author = post.owner_username
                    post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                    
                    # Save content and get analysis
                    content_data = self._analyze_and_save_content(
                        source=source,
                        text=caption,
                        author=author,
                        url=post_url
                    )
                    posts_data.append(content_data)
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing hashtag post: {e}")
                    continue

            # Update source last scraped time
            source.last_scraped_at = datetime.utcnow()
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"✅ Successfully scraped {len(posts_data)} posts from #{hashtag}")
            
            return {
                "source": {
                    "platform": "Instagram",
                    "source_handle": handle,
                    "source_type": "Hashtag"
                },
                "user": None,
                "posts": posts_data,
                "scraped_count": len(posts_data)
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to scrape Instagram hashtag #{hashtag}: {e}")
            return {
                "error": str(e),
                "hashtag": hashtag,
                "scraped_count": 0,
                "posts": []
            }

    def get_post_comments(self, shortcode: str, max_comments: int = 20) -> List[Dict[str, Any]]:
        """Get comments from a specific Instagram post"""
        # This is a placeholder - the existing method doesn't save to DB
        # For now, return empty list
        return []


# Global instance
instagram_scraper_db = InstagramScraperDB()

def get_instagram_scraper_db():
    """Get the global Instagram DB scraper instance"""
    return instagram_scraper_db


