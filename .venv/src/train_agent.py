import io
from contextlib import redirect_stdout
from agent import QLearningAgent
from game import Game


def play_round(agent, training=True):
    game = Game()
    game.start_round()

    player = game.player
    dealer_card = game.dealer.hand[0]

    # Check for an initial blackjack
    if player.get_hand_value() == 21:
        if game.dealer.get_hand_value() == 21:
            return 0
        return 1

    if game.dealer.get_hand_value() == 21:
        return -1

    while True:
        state = agent.get_state(player, dealer_card)
        action = agent.choose_action(state)

        if action == "hit":
            card = game.gameDeck.deal_card()
            player.add_card(card)

            # Player busts
            if player.get_hand_value() > 21:
                if training:
                    agent.update(state, action, -1, None, True)
                return -1

            # Player can continue if below 21
            if player.get_hand_value() < 21:
                next_state = agent.get_state(player, dealer_card)

                if training:
                    agent.update(
                        state, action, 0, next_state, False
                    )

                continue

        # Player stands or reaches 21
        game.dealer_turn()

        player_total = player.get_hand_value()
        dealer_total = game.dealer.get_hand_value()

        # Determine the reward
        if dealer_total > 21:
            reward = 1
        elif player_total > dealer_total:
            reward = 1
        elif player_total < dealer_total:
            reward = -1
        else:
            reward = 0

        # Update the Q-table only during training
        if training:
            agent.update(state, action, reward, None, True)

        return reward


def train(episodes=100000):
    agent = QLearningAgent()
    agent.load()

    # Encourage exploration during additional training
    agent.epsilon = 0.2

    wins = 0
    losses = 0
    ties = 0

    # Training loop
    for episode in range(episodes):
        #reward = play_round(agent)
        with redirect_stdout(io.StringIO()):
            reward = play_round(agent)

        # Record the outcome
        if reward == 1:
            wins += 1
        elif reward == -1:
            losses += 1
        else:
            ties += 1

        # Gradually reduce exploration
        agent.epsilon = max(0.05, agent.epsilon * 0.99995)

        # Display progress every 1,000 rounds
        if (episode + 1) % 1000 == 0:
            print(f"Completed {episode + 1}/{episodes} rounds")

    # Display training results
    print("\n--- Training Results ---")
    print("Rounds played:", episodes)
    print("Wins:", wins)
    print("Losses:", losses)
    print("Ties:", ties)
    print(f"Win rate: {wins / episodes * 100:.2f}%")
    print(f"Loss rate: {losses / episodes * 100:.2f}%")
    print(f"Tie rate: {ties / episodes * 100:.2f}%")
    print("Final epsilon:", agent.epsilon)
    print("States learned:", len(agent.q_table))

    agent.save()
    
    return agent


if __name__ == "__main__":
    agent = train(100000)