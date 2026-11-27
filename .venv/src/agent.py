import random
import json
from pathlib import Path

class QLearningAgent:
    def __init__(self):
        self.q_table = {}
        self.alpha = 0.1
        self.gamma = 1.0
        self.epsilon = 1.0
        self.actions = ["hit", "stand"]

    def get_state(self, player, dealer_card):
        player_total = player.get_hand_value()

        # Determine the dealer's visible card value
        dealer_rank = dealer_card[0]

        if dealer_rank in ["J", "Q", "K"]:
            dealer_value = 10
        elif dealer_rank == "A":
            dealer_value = 11
        else:
            dealer_value = int(dealer_rank)

        # Calculate the player's total with all aces counted as 1
        low_total = 0

        for rank, suit in player.hand:
            if rank == "A":
                low_total += 1
            elif rank in ["J", "Q", "K"]:
                low_total += 10
            else:
                low_total += int(rank)

        # Check whether an ace is currently counted as 11
        usable_ace = player_total == low_total + 10

        return (player_total, dealer_value, usable_ace)
    
    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = {
                action: 0.0 for action in self.actions
            }

        return self.q_table[state]

    def choose_action(self, state):
        q_values = self.get_q_values(state)

        # Exploration: choose a random action
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        # Exploitation: choose the best known action
        max_q = max(q_values.values())

        best_actions = [
            action for action in self.actions
            if q_values[action] == max_q
        ]

        return random.choice(best_actions)

    def update(self, state, action, reward, next_state, done):
        q_values = self.get_q_values(state)
        current_q = q_values[action]

        # Check whether the round has ended
        if done:
            max_next_q = 0.0
        else:
            next_q_values = self.get_q_values(next_state)
            max_next_q = max(next_q_values.values())

        # Q-learning equation
        new_q = current_q + self.alpha * (
            reward + self.gamma * max_next_q - current_q
        )

        # Store the updated Q-value
        self.q_table[state][action] = new_q

    def save(self, filename="q_table.json"):
        path = Path(__file__).resolve().parent / filename

        data = {
            "epsilon": self.epsilon,
            "q_table": [
                {
                    "state": list(state),
                    "q_values": q_values
                }
                for state, q_values in self.q_table.items()
            ]
        }

        with open(path, "w") as file:
            json.dump(data, file, indent=4)

        print("Training saved to:", path)

    def load(self, filename="q_table.json"):
        path = Path(__file__).resolve().parent / filename

        if not path.exists():
            print("No saved training found. Starting fresh.")
            return False

        with open(path, "r") as file:
            data = json.load(file)

        self.epsilon = data["epsilon"]

        self.q_table = {
            tuple(entry["state"]): entry["q_values"]
            for entry in data["q_table"]
        }

        print("Previous training loaded.")
        print("States loaded:", len(self.q_table))

        return True


# TEMPORARY TESTING
if __name__ == "__main__":
    from player import Player

    agent = QLearningAgent()
    player = Player()

    player.add_card(("A", "Spades"))
    player.add_card(("6", "Hearts"))

    dealer_card = ("K", "Clubs")

    state = agent.get_state(player, dealer_card)

    print("Player's hand:", player.hand)
    print("Dealer's card:", dealer_card)
    print("State:", state)
    print("Q-values:", agent.get_q_values(state))
    print("Q-table:", agent.q_table)
    print("\nTesting exploration:")

    agent.epsilon = 1.0

    for i in range(10):
        print(agent.choose_action(state))

    print("\nTesting exploitation:")

    agent.epsilon = 0.0

    agent.q_table[state]["hit"] = -0.5
    agent.q_table[state]["stand"] = 0.8

    for i in range(5):
        print(agent.choose_action(state))

    print("\nTesting Q-learning update:")

    # Create a fresh agent for testing
    learning_agent = QLearningAgent()

    test_state = (20, 10, False)

    print("Before:", learning_agent.get_q_values(test_state))

    # Agent hits and busts
    learning_agent.update(
        test_state, "hit", -1, None, True
    )

    print("After loss:", learning_agent.get_q_values(test_state))

    # Agent stands and wins
    learning_agent.update(
        test_state, "stand", 1, None, True
    )

    print("After win:", learning_agent.get_q_values(test_state))