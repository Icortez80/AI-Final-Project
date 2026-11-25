import cv2
from pathlib import Path

CARD_FOLDER = Path("cards")

for image_path in sorted(CARD_FOLDER.glob("*.jpg")):
    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Could not load {image_path}")
        continue

    print(f"{image_path.name}: {image.shape}")

    cv2.imshow(image_path.name, image)

    key = cv2.waitKey(0) & 0xFF

    if key == ord("q"):
        break

cv2.destroyAllWindows()