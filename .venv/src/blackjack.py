"""Executable entry point for the blackjack project.

Run this file to play. A future agent can be passed to Game.gameLoop() as an
action provider without changing the blackjack rules in game.py.
"""

from game import Game


def main():
    game = Game(number_of_decks=1)

    # For now, None makes the game read human input.
    # Later this can become: game.gameLoop(action_provider=agent.choose_action)
    game.gameLoop(action_provider=None)


if __name__ == "__main__":
    main()
