from agent import QLearningAgent
from camera import CardCamera
from card_recognizer import CardRecognizer
from player import Player


def main():
    recognizer = CardRecognizer()
    camera = CardCamera(recognizer, camera_index=0)

    agent = QLearningAgent()
    agent.load()

    # Use the learned Q-table instead of random exploration
    agent.epsilon = 0.0

    # Temporary player hand
    player = Player()
    player.add_card(("8", "Unknown"))
    player.add_card(("7", "Unknown"))

    last_rank = None

    try:
        while True:
            observation = camera.read()

            if observation is None:
                print("Could not read camera frame.")
                break

            rank = observation["stable_rank"]

            if rank is not None and rank != last_rank:
                dealer_card = (rank, "Unknown")

                state = agent.get_state(
                    player,
                    dealer_card
                )

                action = agent.choose_action(state)

                print("Recognized dealer card:", rank)
                print("Agent state:", state)
                print("Agent action:", action)

                last_rank = rank

            if observation["frame"] is not None:
                import cv2

                cv2.imshow(
                    "Camera",
                    observation["frame"]
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    finally:
        camera.close()


if __name__ == "__main__":
    main()