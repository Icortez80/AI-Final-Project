import cv2
from pathlib import Path

camera = cv2.VideoCapture(2)

SAVE_FOLDER = Path("cards")
SAVE_FOLDER.mkdir(exist_ok=True)

card_rank = input("Enter the card rank being captured: ").strip()

# Continue numbering existing images for this rank
image_number = len(list(SAVE_FOLDER.glob(f"{card_rank}_*.jpg")))

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read frame.")
        break

    x1, y1 = 100, 100
    x2, y2 = 300, 350

    card_crop = frame[y1:y2, x1:x2]

    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.imshow("Camera", frame)
    cv2.imshow("Card Crop", card_crop)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("s"):
        filename = SAVE_FOLDER / f"{card_rank}_{image_number}.jpg"

        saved = cv2.imwrite(str(filename), card_crop)

        if saved:
            print(f"Saved cropped card image: {filename}")
            image_number += 1
        else:
            print("Could not save image.")

    elif key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()