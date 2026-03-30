"""
Extended case module with image extraction, download, CV analysis, and score fusion.

This module keeps DB compatibility by storing image-analysis fields under:
Case.meta_data["content_image_analysis"][<content_id>] = {
  image_path, image_prediction, image_confidence, image_risk_score,
  text_risk_score, final_score, final_prediction
}
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests

from extensions import db
from models.case import Case
from models.content import Content
from services.case_image_analyzer import analyze_case_image

logger = logging.getLogger(__name__)

IMAGE_URL_RE = re.compile(
    r"(https?://[^\s\"'<>]+?\.(?:jpg|jpeg|png|webp|bmp|gif))(?:\?[^\s\"'<>]*)?",
    re.IGNORECASE,
)


class CaseModule:
    """Case-level image intelligence for linked scraped posts."""

    def __init__(self, image_dir: str = "case_images") -> None:
        self.image_dir = Path(image_dir)
        if not self.image_dir.is_absolute():
            self.image_dir = Path(__file__).parent.parent / self.image_dir
        self.image_dir.mkdir(parents=True, exist_ok=True)

    def extract_image_urls(self, content: Content) -> List[str]:
        """Extract image URLs from content.url and content.text."""
        urls: List[str] = []

        if content.url and self._looks_like_image_url(content.url):
            urls.append(content.url.strip())

        if content.text:
            for match in IMAGE_URL_RE.findall(content.text):
                clean = match.strip()
                if clean not in urls:
                    urls.append(clean)

        # Optional support for structured payloads in analysis_data.
        if content.analysis_data and isinstance(content.analysis_data, dict):
            data_urls = content.analysis_data.get("image_urls")
            if isinstance(data_urls, list):
                for u in data_urls:
                    if isinstance(u, str) and self._looks_like_image_url(u) and u not in urls:
                        urls.append(u)

        return urls

    def download_image(self, image_url: str, content_id: int) -> Optional[str]:
        """Download image URL to local case image directory."""
        try:
            parsed = urlparse(image_url)
            suffix = Path(parsed.path).suffix.lower() or ".jpg"
            local_path = self.image_dir / f"content_{content_id}{suffix}"

            response = requests.get(image_url, timeout=20)
            response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(response.content)

            return str(local_path)
        except Exception as exc:
            logger.warning("Failed to download image for content %s: %s", content_id, exc)
            return None

    def analyze_content_with_image(self, content: Content) -> Dict[str, float | str | None]:
        """
        Run CV analysis and fuse with existing text score.

        Fusion:
            final_score = (text_score * 0.6) + (image_score * 0.4)
            final_score > 0.5 => Drug-Related else Non-Drug
        """
        image_urls = self.extract_image_urls(content)
        image_path = None
        image_prediction = "Non-drug-related"
        image_confidence = 0.0
        image_risk_score = 0.0

        if image_urls:
            image_path = self.download_image(image_urls[0], content.id)
            if image_path:
                try:
                    image_result = analyze_case_image(image_path)
                    image_prediction = str(image_result["label"])
                    image_confidence = float(image_result["confidence"])
                    image_risk_score = float(image_result["risk_score"])
                except Exception as exc:
                    logger.warning("Image analysis failed for content %s: %s", content.id, exc)

        # Normalize text score to [0,1]
        text_score = float(content.suspicion_score or 0) / 100.0
        if content.risk_score is not None:
            text_score = max(text_score, float(content.risk_score) / 100.0)

        final_score = (text_score * 0.6) + (image_risk_score * 0.4)
        final_prediction = "Drug-Related" if final_score > 0.5 else "Non-Drug"

        return {
            "image_path": image_path,
            "image_prediction": image_prediction,
            "image_confidence": round(image_confidence, 6),
            "image_risk_score": round(image_risk_score, 6),
            "text_risk_score": round(text_score, 6),
            "final_score": round(final_score, 6),
            "final_prediction": final_prediction,
        }

    def store_case_image_analysis(self, case_id: int, content_id: int) -> Dict[str, float | str | None]:
        """
        Analyze one linked content item and store result in case metadata.
        """
        case = Case.query.get(case_id)
        if not case:
            raise ValueError(f"Case not found: {case_id}")

        content = Content.query.get(content_id)
        if not content:
            raise ValueError(f"Content not found: {content_id}")

        result = self.analyze_content_with_image(content)

        meta = case.meta_data or {}
        content_analysis = meta.get("content_image_analysis") or {}
        content_analysis[str(content_id)] = result
        meta["content_image_analysis"] = content_analysis
        case.meta_data = meta
        db.session.commit()

        return result

    @staticmethod
    def _looks_like_image_url(url: str) -> bool:
        lower = (url or "").lower()
        return any(lower.endswith(ext) or f"{ext}?" in lower for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"])


def example_usage(case_id: int, content_id: int) -> Dict[str, float | str | None]:
    """
    Example:
        from services.case_module import example_usage
        result = example_usage(case_id=1, content_id=73)
    """
    module = CaseModule()
    return module.store_case_image_analysis(case_id=case_id, content_id=content_id)

