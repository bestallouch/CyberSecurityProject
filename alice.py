import socket
import pickle
import _thread
import time
import random

from phe import paillier
from common import *

## Alice

def Main():
    ## Alice's server for initial reshuffling
    ## Set up server to connect to Bob
    server_alice = setServer('127.0.0.1', 5006, 2)

    print("Alice is up for the game.")
    print("Waiting for Bob to connect...\n")

    ## Connect with Bob to start shuffling the deck
    connection_from_bob, address_bob = server_alice.accept()
    print("Connected to Bob.\n")

    ## Set up initial game parameters
    num_cards = 52
    alice_key = random.randint(1,52)

    ## Deck has numbers from 0 to 51
    deck = list(range(num_cards))
    print("A deck of ", num_cards, " cards received.")

    ## Deck encryption by Alice
    for i in range(num_cards):
        deck[i] = encryptCard(deck[i], alice_key)
    
    ## Shuffle deck    
    random.shuffle(deck)
    print("Deck encrypted and shuffled.\n")

    ## Send deck to Bob
    sendDeck(connection_from_bob, address_bob, deck)
    print("Deck sent to Bob.\n")

    ## Receive encrypted and shuffled deck from Bob
    shuffled_deck_bob = connection_from_bob.recv(4096)
    shuffled_deck_bob = pickle.loads(shuffled_deck_bob)
    print("Deck received from Bob.")

    ## Decrypt deck before individual encryption
    for i in range(num_cards):
        shuffled_deck_bob[i] = decryptCard(shuffled_deck_bob[i], alice_key)

    print("Deck decrypted.\n")

    print("Getting individual keys...")
    alice_individual_keys = random.sample(range(1, 60), num_cards)
    ## Encrypt each card with its individual key
    for i in range(num_cards):
        shuffled_deck_bob[i] = encryptCard(shuffled_deck_bob[i], alice_individual_keys[i])
    print("Deck encrypted by individual keys.\n")

    ## Send deck to Bob for individual encryption
    sendDeck(connection_from_bob, address_bob, shuffled_deck_bob)
    print("Deck sent to Bob.\n")

    ## Receive final deck from Bob
    shuffled_encrypted_cards = connection_from_bob.recv(4096)
    shuffled_encrypted_cards = pickle.loads(shuffled_encrypted_cards)
    print("Deck received from Bob.")

    ## Distribute cards in half
    print("Distributing cards...\n")

    alice_cards = []
    alice_cards_keys1 = []
    bob_cards_keys2 = []

    ## Alice gets first two cards
    for i in range(2):
        alice_cards.append(shuffled_encrypted_cards[i])
        alice_cards_keys1.append(alice_individual_keys[i])
    
    ## Bob gets second two cards
    for i in range(2,4):
        bob_cards_keys2.append(alice_individual_keys[i])

    print("A hand of ", 2," cards received.\n")
    
    ## We need individual keys of both players for total decryption
    print("Sending individual keys of Bob's cards...\n")
    sendDeck(connection_from_bob, address_bob, bob_cards_keys2)
    print("Sent.")

    print("Requesting individual keys from Bob...")
    alice_cards_keys2 = connection_from_bob.recv(4096)
    alice_cards_keys2 = pickle.loads(alice_cards_keys2)
    print("Individual keys Received.\n")

    ## Decrypt to see the hand you are dealt
    print("Decrypting your cards...\n")
    alice_cards_decrypted = [ 0 for i in range(2) ]
    for i in range(2):
        alice_cards_decrypted[i] = decryptCard(decryptCard(alice_cards[i], alice_cards_keys1[i]), alice_cards_keys2[i])

    print("Your cards are : ")
    print(alice_cards_decrypted)
    print("\n")

    print("We can start the game now..")
    print("Connecting to the servers...")

    ## Connect to Server 1
    client_sock1 = connectToServer('127.0.0.1', 5004)

    packet = client_sock1.recv(4096)
    dicti = pickle.loads(packet)
    rand_no = dicti["rand_no"]
    public_key = dicti["public_key"]

    ## Connect to Server 2
    client_sock2 = connectToServer('127.0.0.1', 5005)

    print("Connected.\n")
    print("Alice! Throw your cards.\n")
    print("Enter the card index.")

    ## Send you cards based on indexing
    for i in range(5):
    	ind = int(input())
    	encrypted_card = public_key.encrypt(alice_cards_decrypted[ind-1] * rand_no)
    	data = pickle.dumps(encrypted_card, -1)
    	client_sock2.sendall(data)
    	result = client_sock1.recv(1024).decode('ascii')
    	print(result)

    
    ## Close all connections
    client_sock2.close()
    client_sock1.close()
    connection_from_bob.close()
    server_alice.close()


if __name__ == '__main__':
    Main()
