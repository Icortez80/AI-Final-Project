
"""Camera interface for reading one or more blackjack cards."""

from collections import Counter, deque

import cv2

from cardtracker import find_card


class CardCamera:
    """Read cards from fixed dealer and player areas."""

    # Example coordinates for a 640x480 camera view.
    # Adjust these to match your physical table.
    DEFAULT_SLOTS = {
        "dealer": [
            (50, 20, 210, 250),
            (220, 20, 380, 250),
        ],
        "player": [
            (50, 260, 210, 480),
            (220, 260, 380, 480),
            (390, 260, 550, 480),
            (560, 260, 640, 480),
        ],
    }

    def __init__(
            self,
            recognizer,
            camera_index=2,
            history_size=12,
            table_slots=None,
    ):
        self.recognizer = recognizer
        self.camera = cv2.VideoCapture(camera_index)
        self.table_slots = table_slots or self.DEFAULT_SLOTS

        self.slot_histories = {
            (area, index): deque(maxlen=history_size)
            for area, boxes in self.table_slots.items()
            for index in range(len(boxes))
        }

        if not self.camera.isOpened():
            raise RuntimeError(
                f"Could not open camera with index {camera_index}."
            )

    def _read_slot(self, frame, area, slot_index, box):
        """Read one card slot and return None if it is empty."""
        x1, y1, x2, y2 = box
        roi = frame[y1:y2, x1:x2]
        card, local_corners = find_card(roi)

        history = self.slot_histories[(area, slot_index)]

        if card is None:
            history.clear()
            return None

        recognition = self.recognizer.recognize_card(card)

        if recognition is None:
            history.clear()
            return None

        rank, score = recognition
        history.append(rank)
        stable_rank, stable_count = Counter(history).most_common(1)[0]

        # Convert ROI coordinates into full-frame coordinates.
        corners = local_corners.astype("float32")
        corners[:, 0] += x1
        corners[:, 1] += y1

        return {
            "rank": rank,
            "stable_rank": stable_rank,
            "stable_count": stable_count,
            "score": score,
            "card": card,
            "corners": corners,
            "box": box,
            "area": area,
            "slot_index": slot_index,
        }

    def read_table(self):
        """Read all configured dealer and player card slots."""
        success, frame = self.camera.read()

        if not success:
            return None

        observation = {
            "frame": frame,
            "dealer_cards": [],
            "player_cards": [],
            "detections": [],
        }

        for area, boxes in self.table_slots.items():
            for slot_index, box in enumerate(boxes):
                detection = self._read_slot(
                    frame,
                    area,
                    slot_index,
                    box,
                )

                if detection is None:
                    continue

                observation[f"{area}_cards"].append(detection)
                observation["detections"].append(detection)

        return observation

    def draw_table(self, observation):
        """Draw slot outlines and recognized ranks on the current frame."""
        frame = observation["frame"]

        for boxes in self.table_slots.values():
            for x1, y1, x2, y2 in boxes:
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (255, 0, 0),
                    2,
                )

        for detection in observation["detections"]:
            x1, y1, _, _ = detection["box"]
            text = (
                f"{detection['stable_rank']} "
                f"({detection['stable_count']})"
            )

            cv2.putText(
                frame,
                text,
                (x1 + 5, y1 + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

            cv2.polylines(
                frame,
                [detection["corners"].astype("int32")],
                True,
                (0, 255, 0),
                2,
            )

        return frame
