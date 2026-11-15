#this file includes everything a player needs to play the game
# hand(s) & current hand score

# creates blueprint for blackjack player
class Player:
    # constructor: automatically runs whenever no player object created
    def __init__(self):
        # creates empty list for player's cards
        self.hand = []

    # creates method for player recieving card
    def add_card(self, card):
        # adds card to players hand
        self.hand.append(card)

    def get_hand_value(self):
        # initialize score
        total = 0
        aces = 0

        # examines each card
        for card in self.hand:
            rank = next(
                value for value in card
                if value in ["2", "3", "4", "5", "6", "7",
                            "8", "9", "10", "J", "Q", "K", "A"]
            )

            # assigns points
            if rank in ["J", "Q", "K"]:
                total += 10

            elif rank == "A":
                total += 11
                aces += 1

            else:
                total += int(rank)

        # adjusts aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1

        return total






    # TEMPORARY TESTING

# creates player, gives cards, prints hand
if __name__ == "__main__":
    player = Player()

    player.add_card({"A", "Spades"})
    player.add_card({"8", "Hearts"})
    player.add_card({"7", "Clubs"})


    print("Players hand: ", player.hand)
    print("Hand value: ", player.get_hand_value())