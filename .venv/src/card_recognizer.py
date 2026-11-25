import cv2
import numpy as np
from pathlib import Path

CARD_FOLDER = Path("cards")

# Change these if your card images have a different shape
IMAGE_SIZE = (200, 200)

templates = []


def preprocess(image):
    height, width = image.shape[:2]

    # Adjust these percentages after viewing your crop
    rank_corner = image[
        int(height * 0.10):int(height * 0.45),
        int(width * 0.08):int(width * 0.40)
    ]

    gray = cv2.cvtColor(rank_corner, cv2.COLOR_BGR2GRAY)

    # Reduce lighting differences
    gray = cv2.equalizeHist(gray)

    gray = cv2.resize(gray, IMAGE_SIZE)

    return gray


def load_templates():
    for image_path in sorted(CARD_FOLDER.glob("*.jpg")):
        image = cv2.imread(str(image_path))

        if image is None:
            print(f"Could not load {image_path}")
            continue

        # Gets the rank from names such as 8_0.jpg or A_1.jpg
        rank = image_path.stem.split("_")[0]

        processed_image = preprocess(image)
        templates.append((rank, processed_image))

        print(f"Loaded {image_path.name} as rank {rank}")

    print(f"Loaded {len(templates)} templates.")


def recognize_card(card_image):
    processed_card = preprocess(card_image)

    best_rank = None
    best_score = float("inf")

    for rank, template in templates:
        difference = processed_card.astype(float) - template.astype(float)
        score = np.mean(difference ** 2)

        if score < best_score:
            best_score = score
            best_rank = rank

    return best_rank, best_score


load_templates()

camera = cv2.VideoCapture(2)

if not camera.isOpened():
    print("Could not open camera.")
    exit()

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read frame.")
        break

    # Adjust these coordinates to surround the card
    x1, y1 = 100, 100
    x2, y2 = 300, 400

    card_crop = frame[y1:y2, x1:x2]

    rank, score = recognize_card(card_crop)

    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.putText(
        frame,
        f"Recognized: {rank}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Score: {score:.0f}",
        (30, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("Card Recognition", frame)
    cv2.imshow("Card Crop", card_crop)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()