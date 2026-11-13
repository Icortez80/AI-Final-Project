#this should have everything a game needs to play
#number of decks -> card objects, current state of game, number of players
import random

#--------------- cards -----------------
SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]


#--------- end of cards section --------

#------------- Deck -------------------
class Deck:
    deck = []
    def __init__(self): #this initializer creates a shuffled deck
        for suit in SUITS:
            for rank in RANKS:
                card = {rank, suit}
                self.deck.append(card)

        random.shuffle(self.deck)

    def deal_hand(self, deck):
        card1 = self.deck.pop()
        card2 = self.deck.pop()
        return [card1, card2]

#----------- end of deck section -------------



#---------------- game ---------------------
start_deck = Deck()
hand = start_deck.deal_hand(start_deck)

print()
#------------ end of game section -----------

