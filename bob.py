import socket
import pickle
import random
import time
from common import *


# Bob

def main():
    # Alice's server for initial reshuffling
    host_alice = '127.0.0.1'
    port_alice = 5006
    client_alice = socket.socket()
    client_alice.connect((host_alice, port_alice))

    print("Connected to Alice.\n")

    shuffled_deck_alice = client_alice.recv(1024)
    shuffled_deck_alice = pickle.loads(shuffled_deck_alice)

    num_cards = len(shuffled_deck_alice)
    bob_key = random.randint(1, 52)
    print("A deck of ", num_cards, " cards received from Alice.")

    # Deck encryption by bob
    deck_bob = list()
    for i in range(num_cards):
        deck_bob.append(encrypt_card(shuffled_deck_alice[i], bob_key))

    # Shuffle
    random.shuffle(deck_bob)

    print("Deck encrypted and shuffled.\n")
    shuffled_deck_bob = pickle.dumps(deck_bob, -1)
    client_alice.sendall(shuffled_deck_bob)
    print("Deck sent back to Alice.\n")

    shuffled_deck_bob = client_alice.recv(1024)
    shuffled_deck_bob = pickle.loads(shuffled_deck_bob)
    print("Deck received from Alice.")

    for i in range(num_cards):
        shuffled_deck_bob[i] = decrypt_card(shuffled_deck_bob[i], bob_key)

    print("Deck decrypted.\n")

    print("Getting individual keys...")
    bob_individual_keys = random.sample(range(1, 60), num_cards)
    for i in range(num_cards):
        shuffled_deck_bob[i] = encrypt_card(shuffled_deck_bob[i], bob_individual_keys[i])
    print("Deck encrypted by individual keys.\n")

    data = pickle.dumps(shuffled_deck_bob, -1)
    client_alice.sendall(data)
    shuffled_encrypted_cards = shuffled_deck_bob
    print("Deck sent to Alice.\n")

    print("Distributing cards...\n")

    bob_cards_keys2 = client_alice.recv(4096)
    bob_cards_keys2 = pickle.loads(bob_cards_keys2)

    bob_cards = []
    bob_cards_keys1 = []
    alice_cards_keys2 = []

    for i in range(2, 4):
        bob_cards.append(shuffled_deck_bob[i])
        bob_cards_keys1.append(bob_individual_keys[i])

    for i in range(2):
        alice_cards_keys2.append(bob_individual_keys[i])

    print("A hand of ", 2, " cards received.\n")
    print("Individual keys received.\n")
    print("Sending individual keys of Alice's cards...\n")

    alice_cards_keys2 = pickle.dumps(alice_cards_keys2, -1)
    client_alice.sendall(alice_cards_keys2)
    print('Sent.\n')

    print("Decrypting your cards...\n")
    bob_cards_decrypted = [0 for i in range(2)]
    for i in range(2):
        bob_cards_decrypted[i] = decrypt_card(decrypt_card(bob_cards[i], bob_cards_keys1[i]), bob_cards_keys2[i])

    print("Your cards are : ")
    print_cards_in_lst(bob_cards_decrypted)
    print("\n")

    print("We can start the game now..")
    while True:
        print("Enter \"yes\" if you are ready:")
        if input() == "yes":
            break

    print("Starting the game...")

    # Receive table cards from Alice

    table_cards_keys2 = client_alice.recv(4096)
    table_cards_keys2 = pickle.loads(table_cards_keys2)

    # Send table cards to Alice
    table_cards_keys1 = []
    table_cards_encrypted = []
    for i in range(4, 7):
        table_cards_keys1.append(bob_individual_keys[i])
        table_cards_encrypted.append(shuffled_encrypted_cards[i])

    data = pickle.dumps(table_cards_keys1, -1)
    client_alice.sendall(data)


    # Decrypt table cards
    table_cards = []
    for i in range(3):
        table_cards.append(decryptCard(decryptCard(table_cards_encrypted[i], table_cards_keys1[i]), table_cards_keys2[i]))

    print("Table are:")
    print()
    print_cards_in_lst(table_cards)
    print("\n")

    # Money
    alice_money = 1000
    bob_money = 1000
    bank = 0

    # Time to make a bet
    alice_bet = client_alice.recv(4096)
    alice_bet = pickle.loads(alice_bet)

    alice_money -= alice_bet
    bank += alice_bet

    bob_bet = 2 * alice_bet
    print("You are the 2 player. Your bet is ", bob_bet,"\n")

    bob_money -= bob_bet
    bank += bob_bet

    print("You have ", bob_money, "$")

    data = pickle.dumps(bob_bet, -1)
    client_alice.sendall(data)

    while True:
        alice_bet = client_alice.recv(4096)
        alice_bet = pickle.loads(alice_bet)
        if alice_bet == "f":
            bob_money += bank
            bank = 0
            print("You are a winner. You have ", bob_money, "$")
            break
        if input == "ch":
            sendDeck(connection_from_bob, address_bob, input)
            break
        if input[0] == "r":
            alice_bet = int(input[2:])
            alice_money -= alice_bet
            bank += alice_bet
            sendDeck(connection_from_bob, address_bob, input)
            break
        if input == "call":
            alice_bet = bob_bet - alice_bet
            alice_money -= alice_bet
            bank += alice_bet
            sendDeck(connection_from_bob, address_bob, input)
            break

    # Close connection
    client_alice.close()


if __name__ == '__main__':
    main()
