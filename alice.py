import socket
import pickle
import _thread
import time
import random
import gmpy2

from common import *
from pocker import *


# Alice

def main():
    # Alice's server for initial reshuffling
    # Set up server to connect to Bob
    server_alice = set_server('0.0.0.0', 5006, 2)

    print("Alice is up for the game.")
    print("Waiting for Bob to connect...\n")

    # Connect with Bob to start shuffling the deck
    connection_from_bob, address_bob = server_alice.accept()
    print("Connected to Bob.\n")

    # Init game parameters
    alice_money = 1000
    all_alice_bet = 0

    bob_money = 1000
    all_bob_bet = 0

    bank = 0

    while True:
        # Set up initial game parameters
        state = gmpy2.random_state(387)
        e, d = generate_keys(PRIME, state)
        print("e, d", e, d)
        num_cards = 52

        # Deck has numbers from 0 to 51
        deck = list(range(2, num_cards + 2))
        print("A deck of ", num_cards, " cards received.")

        # Deck encryption by Alice
        for i in range(num_cards):
            deck[i] = encrypt_card(deck[i], e)

        # Shuffle deck
        random.shuffle(deck)
        print("Deck encrypted and shuffled.\n")

        # Send deck to Bob
        send_deck(connection_from_bob, address_bob, deck)
        print("Deck sent to Bob.\n")

        # Receive encrypted and shuffled deck from Bob
        shuffled_deck_bob = connection_from_bob.recv(4096)
        shuffled_deck_bob = pickle.loads(shuffled_deck_bob)
        print("Deck received from Bob.")

        # Decrypt deck before individual encryption
        for i in range(num_cards):
            shuffled_deck_bob[i] = decrypt_card(shuffled_deck_bob[i], d)
        print("shuffled_deck_bob", shuffled_deck_bob)

        print("Deck decrypted.\n")
        alice_individual_keys_e = [0] * num_cards
        alice_individual_keys = [0] * num_cards
        print(alice_individual_keys_e)
        print("Getting individual keys...")

        for i in range(num_cards):
            alice_individual_keys_e[i], alice_individual_keys[i] = generate_keys(PRIME, state)

        # Encrypt each card with its individual key
        for i in range(num_cards):
            shuffled_deck_bob[i] = encrypt_card(shuffled_deck_bob[i], alice_individual_keys_e[i])
        print("Deck encrypted by individual keys.\n")

        # Send deck to Bob for individual encryption
        send_deck(connection_from_bob, address_bob, shuffled_deck_bob)
        print("Deck sent to Bob.\n")

        # Receive final deck from Bob
        shuffled_encrypted_cards = connection_from_bob.recv(4096)
        shuffled_encrypted_cards = pickle.loads(shuffled_encrypted_cards)
        print("Deck received from Bob.")

        # Distribute cards in half
        print("Distributing cards...\n")

        alice_cards = []
        alice_cards_keys1 = []
        bob_cards_keys2 = []

        # Alice gets first two cards
        for i in range(2):
            alice_cards.append(shuffled_encrypted_cards[i])
            alice_cards_keys1.append(alice_individual_keys[i])

        # Bob gets second two cards
        for i in range(2, 4):
            bob_cards_keys2.append(alice_individual_keys[i])

        print("A hand of ", 2, " cards received.\n")

        # We need individual keys of both players for total decryption
        print("Sending individual keys of Bob's cards...\n")
        send_deck(connection_from_bob, address_bob, bob_cards_keys2)
        print("Sent.")

        print("Requesting individual keys from Bob...")
        alice_cards_keys2 = connection_from_bob.recv(4096)
        alice_cards_keys2 = pickle.loads(alice_cards_keys2)
        print("Individual keys Received.\n")

        # Decrypt to see the hand you are dealt
        print("Decrypting your cards...\n")
        alice_cards_decrypted = [0 for i in range(2)]
        for i in range(2):
            alice_cards_decrypted[i] = decrypt_card(decrypt_card(alice_cards[i], alice_cards_keys1[i]),
                                                    alice_cards_keys2[i])

        print("Your cards are : ")

        print_cards_in_lst(alice_cards_decrypted)
        print("\n")

        print("We can start the game now..")
        while True:
            print("Enter \"yes\" if you are ready:")
            if input() == "yes":
                break

        print("Starting the game...")

        # Send table cards to Bob
        table_cards_keys1 = []
        table_cards_encrypted = []
        for i in range(4, 7):
            table_cards_keys1.append(alice_individual_keys[i])
            table_cards_encrypted.append(shuffled_encrypted_cards[i])

        send_deck(connection_from_bob, address_bob, table_cards_keys1)

        # Receive table cards from Bob
        table_cards_keys2 = connection_from_bob.recv(4096)
        table_cards_keys2 = pickle.loads(table_cards_keys2)

        # Decrypt table cards
        table_cards = []
        for i in range(3):
            table_cards.append(
                decrypt_card(decrypt_card(table_cards_encrypted[i], table_cards_keys1[i]), table_cards_keys2[i]))

        print("Board is:")
        print_cards_in_lst(table_cards)
        print("\n")

        # Time to make a bet
        alice_bet = 50
        alice_money -= alice_bet
        all_alice_bet += alice_bet
        print("You are the 1 player. Your bet is", alice_bet, "\n")
        print("You have ", alice_money, "$")

        send_deck(connection_from_bob, address_bob, alice_bet)
        bob_bet = connection_from_bob.recv(4096)
        bob_bet = pickle.loads(bob_bet)

        bob_money -= bob_bet
        all_bob_bet += bob_bet
        bank += bob_bet

        current_card_in_deck = 7
        isFold = False
        is_call = False
        # Time to make a bet
        while current_card_in_deck < 10 and not isFold:
            first_turn = True
            while (all_alice_bet != all_bob_bet or first_turn) and not isFold:
                first_turn = False
                print("Time to make a bet. Enter help for more information")
                print("You: stack -", alice_money, ",", "pot -", bank, ",", "your total bet -", all_alice_bet)
                while True:
                    command = input()
                    print("\n")
                    if command == "help":
                        print("To FOLD enter \"fold\" ")
                        print("To CHECK enter \"check\"")
                        print("To RAISE enter \"raise x\", where x is your bet")
                        print("To CALL enter \"call\"\n")
                    else:
                        if command == "fold":
                            bob_money += bank
                            bank = 0
                            send_deck(connection_from_bob, address_bob, command)
                            print("You lose. You have", alice_money, "$")
                            isFold = True
                            break
                        if command == "check":
                            send_deck(connection_from_bob, address_bob, command)
                            break
                        if "raise" in command:
                            alice_bet = int(command.split()[1])
                            alice_money -= alice_bet
                            all_alice_bet += alice_bet
                            bank += alice_bet
                            send_deck(connection_from_bob, address_bob, command)
                            break
                        if command == "call":
                            alice_bet = all_bob_bet - all_alice_bet
                            alice_money -= alice_bet
                            all_alice_bet += alice_bet
                            bank += alice_bet
                            is_call = True
                            send_deck(connection_from_bob, address_bob, command)
                            break

                if not isFold and not is_call:
                    # Get Bob bet
                    print("Waiting for your opponent")
                    command = connection_from_bob.recv(4096)
                    command = pickle.loads(command)
                    print("Opponent made a bet")

                    if "fold" in command:
                        alice_money += bank
                        bank = 0
                        print("You win. You have", alice_money, "$")
                        isFold = True
                        break
                    if "raise" in command:
                        bob_bet = int(command.split()[1])
                        bob_money -= bob_bet
                        all_bob_bet += bob_bet
                        bank += bob_bet
                        print("Opponent raise on", bob_bet)
                    if "call" in command:
                        bob_bet = all_alice_bet - all_bob_bet
                        bob_money -= bob_bet
                        all_bob_bet += bob_bet
                        bank += bob_bet
                        print("Opponent call on", bob_bet)
                        break
                    if "check" in command:
                        print("Opponent check")
                    print("Opponent: stack -", bob_money, ",", "pot -", bank, "opponent total bet -", all_bob_bet)

            if current_card_in_deck < 9 and not isFold:
                # Open one more card
                key_from_alice = alice_individual_keys[current_card_in_deck]
                send_deck(connection_from_bob, address_bob, key_from_alice)

                key_from_bob = connection_from_bob.recv(4096)
                key_from_bob = pickle.loads(key_from_bob)

                table_cards.append(
                    decrypt_card(decrypt_card(shuffled_encrypted_cards[current_card_in_deck], key_from_bob),
                                 key_from_alice))
                print("Board are:")
                print_cards_in_lst(table_cards)
                print("\n")
            current_card_in_deck += 1

        if not isFold:
            # Compute results
            send_deck(connection_from_bob, address_bob, alice_cards_keys1)
            bob_cards_keys = connection_from_bob.recv(4096)
            bob_cards_keys = pickle.loads(bob_cards_keys)

            bob_cards = []
            for i in range(2):
                bob_cards.append(
                    decrypt_card(decrypt_card(shuffled_encrypted_cards[i + 2], alice_individual_keys[i + 2]),
                                 bob_cards_keys[i]))

            print("Board is:")
            print_cards_in_lst(table_cards)

            print("Your cards are:")
            print_cards_in_lst(alice_cards_decrypted)

            print("Opponent cards are:")
            print_cards_in_lst(bob_cards)
            result = choose_winner(alice_cards_decrypted, bob_cards, table_cards)

            if result[0]:
                print("You won!")
                alice_money += bank

            else:
                if result[1]:
                    print("Opponent won!")
                    bob_money += bank
                else:
                    print("Split!")
                    bob_money += bank / 2
                    alice_money += bank / 2
            bank = 0
            all_bob_bet = 0
            all_alice_bet = 0

            print("Result =", result)

        print("To exit enter \"exit\"")
        command = input()
        if "exit" in command:
            break

    # Close all connections
    connection_from_bob.close()
    server_alice.close()


if __name__ == '__main__':
    main()
