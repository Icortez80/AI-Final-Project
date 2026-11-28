import cv2
import numpy as np


def order_points(points):
    points = points.reshape(4, 2)

    ordered = np.zeros((4, 2), dtype="float32")

    sums = points.sum(axis=1)
    ordered[0] = points[np.argmin(sums)]  # top-left
    ordered[2] = points[np.argmax(sums)]  # bottom-right

    differences = np.diff(points, axis=1)
    ordered[1] = points[np.argmin(differences)]  # top-right
    ordered[3] = points[np.argmax(differences)]  # bottom-left

    return ordered


def find_card(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    threshold_images = []

    # Try several brightness thresholds
    for threshold_value in [80, 110, 140, 170, 200]:
        _, binary = cv2.threshold(
            blurred,
            threshold_value,
            255,
            cv2.THRESH_BINARY
        )

        threshold_images.append(binary)

    # Helps with uneven lighting
    adaptive = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        5
    )

    threshold_images.append(adaptive)

    frame_area = frame.shape[0] * frame.shape[1]
    kernel = np.ones((5, 5), np.uint8)

    for threshold in threshold_images:

        threshold = cv2.morphologyEx(
            threshold,
            cv2.MORPH_CLOSE,
            kernel
        )

        contours, _ = cv2.findContours(
            threshold,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in sorted(
            contours,
            key=cv2.contourArea,
            reverse=True
        ):
            area = cv2.contourArea(contour)

            if area < frame_area * 0.05:
                continue

            perimeter = cv2.arcLength(contour, True)

            corners = cv2.approxPolyDP(
                contour,
                0.02 * perimeter,
                True
            )

            if len(corners) != 4:
                continue

            points = order_points(corners)

            output_width = 200
            output_height = 300

            destination = np.array([
                [0, 0],
                [output_width - 1, 0],
                [output_width - 1, output_height - 1],
                [0, output_height - 1]
            ], dtype="float32")

            transform = cv2.getPerspectiveTransform(
                points,
                destination
            )

            card = cv2.warpPerspective(
                frame,
                transform,
                (output_width, output_height)
            )

            return card, points

    return None, None