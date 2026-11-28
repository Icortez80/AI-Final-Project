
"""Card-template recognition.

This module loads labeled card images and recognizes one already-cropped,
perspective-corrected card. Live camera handling is in camera.py.
"""

from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

from cardtracker import find_card


class CardRecognizer:
    def __init__(self, card_folder="cards", image_size=(100, 100)):
        self.card_folder = Path(card_folder)
        self.image_size = image_size
        self.templates = []
        self.load_templates()

    def preprocess(self, image):
        """Extract and normalize the rank region from a card image."""
        height, width = image.shape[:2]

        rank_corner = image[
            int(height * 0.01):int(height * 0.35),
            int(width * 0.01):int(width * 0.20)
        ]

        gray = cv2.cvtColor(rank_corner, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(
            gray,
            self.image_size,
            interpolation=cv2.INTER_AREA
        )

        return cv2.normalize(
            gray,
            None,
            0,
            255,
            cv2.NORM_MINMAX
        )

    def image_paths(self):
        valid_extensions = {".jpg", ".jpeg", ".png"}

        return sorted(
            path for path in self.card_folder.iterdir()
            if path.suffix.lower() in valid_extensions
        )

    def load_templates(self):
        for image_path in self.image_paths():
            image = cv2.imread(str(image_path))

            if image is None:
                print(f"Could not load {image_path}")
                continue

            # Apply the same perspective correction used for live cards.
            detected_card, _ = find_card(image)

            if detected_card is None:
                print(f"Could not find card inside {image_path.name}")
                continue

            rank = image_path.stem.split("_")[0]
            processed_image = self.preprocess(detected_card)
            self.templates.append((rank, processed_image))

        print(f"Loaded {len(self.templates)} card templates.")

    def recognize_card(self, card_image, show_debug=False):
        if not self.templates:
            raise RuntimeError("No card templates were loaded.")

        processed_card = self.preprocess(card_image)

        if show_debug:
            cv2.imshow("Processed Rank", processed_card)

        scores_by_rank = defaultdict(list)

        for rank, template in self.templates:
            difference = (
                    processed_card.astype(float)
                    - template.astype(float)
            )

            score = np.mean(difference ** 2)
            scores_by_rank[rank].append(score)

        if not scores_by_rank:
            return None

        rank_scores = {
            rank: np.mean(sorted(scores)[:3])
            for rank, scores in scores_by_rank.items()
        }

        best_rank = min(rank_scores, key=rank_scores.get)
        best_score = rank_scores[best_rank]

        return best_rank, best_score
