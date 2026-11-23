"""Blackjack game rules and round management."""

import random

from player import Player


SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


class Deck:
    def __init__(self, number_of_decks=1):
        self.cards = [
            (rank, suit)
            for _ in range(number_of_decks)
            for suit in SUITS
            for rank in RANKS
        ]
        random.shuffle(self.cards)

    def deal_card(self):
        if not self.cards:
            raise RuntimeError("The deck is empty.")
        return self.cards.pop()

    def deal_hand(self):
        return [self.deal_card(), self.deal_card()]


class Game:
    """Controls one blackjack round at a time."""

    def __init__(self, number_of_decks=1):
        self.gameDeck = Deck(number_of_decks)
        self.dealer = Player()
        self.player_hands = []
        self.gameOver = False

    @property
    def player(self):
        """The first hand, kept for compatibility with the original code."""
        return self.player_hands[0]

    def start_round(self):
        self.gameOver = False
        self.dealer = Player()
        self.player_hands = [Player()]
        self.dealer.hand = self.gameDeck.deal_hand()
        self.player.hand = self.gameDeck.deal_hand()

    @staticmethod
    def card_value(card):
        rank = card[0]
        if rank in ["J", "Q", "K"]:
            return 10
        if rank == "A":
            return 11
        return int(rank)

    def can_split(self, hand):
        """Allow splitting pairs and ten-value face-card pairs."""
        return (
            len(hand.hand) == 2
            and self.card_value(hand.hand[0]) == self.card_value(hand.hand[1])
        )

    def split_hand(self, hand_index):
        hand = self.player_hands[hand_index]
        if not self.can_split(hand):
            return False

        first_card, second_card = hand.hand
        first_hand = Player()
        second_hand = Player()
        first_hand.add_card(first_card)
        second_hand.add_card(second_card)
        first_hand.add_card(self.gameDeck.deal_card())
        second_hand.add_card(self.gameDeck.deal_card())
        self.player_hands[hand_index:hand_index + 1] = [first_hand, second_hand]
        return True

    def show_initial_hands(self):
        print("\nPlayer's hand:", self.player.hand)
        print("Player value:", self.player.get_hand_value())
        print("Dealer shows:", self.dealer.hand[0])

    def player_turn(self, hand_index, action_provider=None):
        """Play one hand until stand, bust, blackjack, or split.

        A future agent can be supplied as action_provider. It receives
        (game, hand_index) and returns "hit", "stand", or "split".
        """
        hand = self.player_hands[hand_index]

        while hand.get_hand_value() < 21:
            if action_provider is None:
                choice = input(
                    f"Hand {hand_index + 1} - Hit (1), Stand (0), Split (2): "
                ).strip()
                action = {"1": "hit", "0": "stand", "2": "split"}.get(choice)
            else:
                action = action_provider(self, hand_index)

            if action == "split":
                if self.can_split(hand):
                    self.split_hand(hand_index)
                    print("Hand split.")
                    return "split"
                print("That hand cannot be split.")
                continue

            if action == "hit":
                card = self.gameDeck.deal_card()
                hand.add_card(card)
                print("You drew:", card)
                print("Hand:", hand.hand)
                print("Value:", hand.get_hand_value())
                continue

            if action == "stand":
                return "stand"

            print("Please choose 1, 0, or 2.")

        return "finished"

    def dealer_turn(self):
        while self.dealer.get_hand_value() < 17:
            card = self.gameDeck.deal_card()
            self.dealer.add_card(card)
            print("Dealer draws:", card)

    def settle_hand(self, hand):
        player_value = hand.get_hand_value()
        dealer_value = self.dealer.get_hand_value()
        print("\nPlayer hand:", hand.hand, "Value:", player_value)
        print("Dealer hand:", self.dealer.hand, "Value:", dealer_value)

        if player_value > 21:
            return "Dealer wins - player busts."
        if dealer_value > 21:
            return "Player wins - dealer busts."
        if player_value > dealer_value:
            return "Player wins."
        if player_value < dealer_value:
            return "Dealer wins."
        return "Push - tie game."

    def gameLoop(self, action_provider=None):
        """Run one complete round."""
        print("** BLACKJACK **")
        self.start_round()
        self.show_initial_hands()

        player_value = self.player.get_hand_value()
        dealer_value = self.dealer.get_hand_value()
        if player_value == 21:
            print("Blackjack! Player wins.")
            return
        if dealer_value == 21:
            print("Dealer has blackjack. Dealer wins.")
            return

        hand_index = 0
        while hand_index < len(self.player_hands):
            result = self.player_turn(hand_index, action_provider)
            if result == "split":
                # The current index now contains the first split hand.
                continue
            hand_index += 1

        self.dealer_turn()
        for hand in self.player_hands:
            print(self.settle_hand(hand))
        self.gameOver = True
