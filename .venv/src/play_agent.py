from agent import QLearningAgent
from game import Game


def play_game(agent):
    game = Game()
    game.start_round()

    player = game.player
    dealer_card = game.dealer.hand[0]

    print("\n--- New Blackjack Game ---")
    print("Player hand:", player.hand)
    print("Dealer visible card:", dealer_card)

    # Check for initial blackjack
    if player.get_hand_value() == 21:
        if game.dealer.get_hand_value() == 21:
            print("Push!")
        else:
            print("Blackjack! Agent wins!")
        return

    if game.dealer.get_hand_value() == 21:
        print("Dealer has blackjack. Agent loses.")
        return

    # Agent makes decisions using its training
    while player.get_hand_value() < 21:
        state = agent.get_state(player, dealer_card)
        action = agent.choose_action(state)

        print("\nPlayer total:", player.get_hand_value())
        print("State:", state)
        print("Q-values:", agent.get_q_values(state))
        print("Agent decision:", action.upper())

        if action == "stand":
            break

        card = game.gameDeck.deal_card()
        player.add_card(card)

        print("Card drawn:", card)
        print("Player hand:", player.hand)

        if player.get_hand_value() > 21:
            print("Agent busts! Dealer wins.")
            return

    # Dealer plays
    game.dealer_turn()

    player_total = player.get_hand_value()
    dealer_total = game.dealer.get_hand_value()

    print("\n--- Final Results ---")
    print("Player hand:", player.hand)
    print("Dealer hand:", game.dealer.hand)
    print("Player total:", player_total)
    print("Dealer total:", dealer_total)

    if dealer_total > 21 or player_total > dealer_total:
        print("Agent wins!")
    elif player_total < dealer_total:
        print("Dealer wins!")
    else:
        print("Push!")


if __name__ == "__main__":
    agent = QLearningAgent()

    if agent.load():
        agent.epsilon = 0.0

        while True:
            play_game(agent)

            answer = input("\nPlay another game? (y/n): ")

            if answer.lower() != "y":
                break
    else:
        print("Please train the agent first.")