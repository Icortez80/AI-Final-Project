"""Executable entry point for the blackjack project.

Run this file to play. A future agent can be passed to Game.gameLoop() as an
action provider without changing the blackjack rules in game.py.
"""
from game import Game
from agent import QLearningAgent


def main():
    game = Game(number_of_decks=1)

    agent = QLearningAgent()
    agent.load()

    # Use the learned policy instead of random exploration
    agent.epsilon = 0.0

    def agent_action(game, hand_index):
        # Get the current player hand
        player = game.player_hands[hand_index]

        # The dealer's first card is the visible card
        dealer_card = game.dealer.hand[0]

        # Convert the game information into the agent's state format
        state = agent.get_state(player, dealer_card)

        # Ask the agent what to do
        action = agent.choose_action(state)

        print(
            f"Agent state: {state} | "
            f"Q-values: {agent.get_q_values(state)} | "
            f"Action: {action}"
        )

        return action

    game.gameLoop(action_provider=agent_action)


if __name__ == "__main__":
    main()