"""Test reading multiple fixed card slots from the camera."""

import cv2

from camera import CardCamera
from card_recognizer import CardRecognizer


def main():
    recognizer = CardRecognizer()
    camera = CardCamera(recognizer, camera_index=0)

    try:
        while True:
            observation = camera.read_table()

            if observation is None:
                print("Could not read camera frame.")
                break

            frame = camera.draw_table(observation)

            dealer_ranks = [
                card["stable_rank"]
                for card in observation["dealer_cards"]
            ]

            player_ranks = [
                card["stable_rank"]
                for card in observation["player_cards"]
            ]

            print(
                f"Dealer: {dealer_ranks} | "
                f"Player: {player_ranks}",
                end="\r",
                flush=True,
            )

            cv2.imshow("Blackjack Table", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.close()


if __name__ == "__main__":
    main()
