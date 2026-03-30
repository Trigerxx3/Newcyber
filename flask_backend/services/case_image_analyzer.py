"""
Computer-vision helper for case image analysis.

Uses pretrained ResNet50 to infer an image-level risk signal and returns:
- label
- confidence
- risk_score
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

from PIL import Image

try:
    import torch
    from torchvision.models import ResNet50_Weights, resnet50
    TORCH_AVAILABLE = True
except Exception as import_exc:
    TORCH_AVAILABLE = False
    torch = None  # type: ignore[assignment]
    ResNet50_Weights = None  # type: ignore[assignment]
    resnet50 = None  # type: ignore[assignment]
    logger = logging.getLogger(__name__)
    logger.warning("PyTorch/torchvision not available; CV analyzer will use fallback mode: %s", import_exc)

logger = logging.getLogger(__name__)


class CaseImageAnalyzer:
    """Image analyzer built on top of pretrained ResNet50."""

    def __init__(self) -> None:
        self._torch_enabled = TORCH_AVAILABLE
        self._weights = None
        self._preprocess = None
        self._categories = []
        self._model = None

        if self._torch_enabled:
            self._weights = ResNet50_Weights.DEFAULT
            self._preprocess = self._weights.transforms()
            self._categories = self._weights.meta.get("categories", [])
            self._model = resnet50(weights=self._weights)
            self._model.eval()

        # Heuristic ImageNet category keywords that can weakly correlate with drug-content imagery.
        self._suspicious_keywords = [
            "pill",
            "syringe",
            "medicine",
            "bottle",
            "packet",
            "powder",
            "capsule",
        ]

    def analyze_case_image(self, image_path: str) -> Dict[str, float | str]:
        """
        Analyze a local image and produce drug-related likelihood proxies.

        Returns:
            {
              "label": "Drug-related" | "Non-drug-related",
              "confidence": float [0,1],
              "risk_score": float [0,1]
            }
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Fallback mode keeps API routes healthy even if torch isn't installed.
        if not self._torch_enabled or self._model is None or self._preprocess is None:
            return {
                "label": "Non-drug-related",
                "confidence": 0.5,
                "risk_score": 0.0,
            }

        img = Image.open(path).convert("RGB")
        tensor = self._preprocess(img).unsqueeze(0)

        with torch.no_grad():
            logits = self._model(tensor)
            probs = torch.softmax(logits, dim=1)[0]

        suspicious_prob = 0.0
        for idx, label in enumerate(self._categories):
            lower_label = str(label).lower()
            if any(keyword in lower_label for keyword in self._suspicious_keywords):
                suspicious_prob = max(suspicious_prob, float(probs[idx].item()))

        prediction_label = "Drug-related" if suspicious_prob > 0.5 else "Non-drug-related"
        confidence = suspicious_prob if prediction_label == "Drug-related" else (1.0 - suspicious_prob)

        return {
            "label": prediction_label,
            "confidence": round(float(confidence), 6),
            "risk_score": round(float(suspicious_prob), 6),
        }


_global_analyzer: CaseImageAnalyzer | None = None


def analyze_case_image(image_path: str) -> Dict[str, float | str]:
    """
    Convenience function required by the case module integration.
    """
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = CaseImageAnalyzer()
    return _global_analyzer.analyze_case_image(image_path)

