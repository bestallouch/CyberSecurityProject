import socket
import pickle
import random
import time
import gmpy2
from common import *
from pocker import *


# Bob

def main():
    # Alice's server for initial reshuffling
    host_alice = '192.168.31.160'
    port_alice = 5006
    client_alice = socket.socket()
    client_alice.connect((host_alice, port_alice))

    print("Connected to Alice.\n")

    # Init game parameters
    alice_money = 1000
    all_alice_bet = 0

    bob_money = 1000
    all_bob_bet = 0

    bank = 0

    while True:
        shuffled_deck_alice = client_alice.recv(1024)
        shuffled_deck_alice = pickle.loads(shuffled_deck_alice)

        num_cards = len(shuffled_deck_alice)
        state = gmpy2.random_state(456)
        c, b = generate_keys(PRIME, state)
        print("c, b", c, b)
        print("A deck of ", num_cards, " cards received from Alice.")

        # Deck encryption by bob
        deck_bob = list()
        for i in range(num_cards):
            deck_bob.append(encrypt_card(shuffled_deck_alice[i], c))

        # Shuffle
        random.shuffle(deck_bob)

        print("Deck encrypted and shuffled.\n")
        shuffled_deck_bob = pickle.dumps(deck_bob, -1)
        client_alice.sendall(shuffled_deck_bob)
        print("Deck sent back to Alice.\n")

        shuffled_deck_bob = client_alice.recv(1024)
        shuffled_deck_bob = pickle.loads(shuffled_deck_bob)
        print ("shuffled_deck_bob", shuffled_deck_bob)
        print("Deck received from Alice.")

        for i in range(num_cards):
            shuffled_deck_bob[i] = decrypt_card(shuffled_deck_bob[i], b)

        print("Deck decrypted.\n")
        bob_individual_keys_c = [0] * num_cards
        bob_individual_keys = [0] * num_cards
        print("Getting individual keys...")

        for i in range(num_cards):
            bob_individual_keys_c[i], bob_individual_keys[i] = generate_keys(PRIME, state)

        for i in range(num_cards):
            shuffled_deck_bob[i] = encrypt_card(shuffled_deck_bob[i], bob_individual_keys_c[i])
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
            table_cards.append(
                decrypt_card(decrypt_card(table_cards_encrypted[i], table_cards_keys1[i]), table_cards_keys2[i]))

        print("Table are:")
        print()
        print_cards_in_lst(table_cards)
        print("\n")



        # Time to make a bet
        alice_bet = client_alice.recv(4096)
        alice_bet = pickle.loads(alice_bet)

        alice_money -= alice_bet
        all_alice_bet += alice_bet
        bank += alice_bet

        bob_bet = 2 * alice_bet
        print("You are the 2 player. Your bet is ", bob_bet, "\n")

        bob_money -= bob_bet
        all_bob_bet += bob_bet
        bank += bob_bet

        print("You have ", bob_money, "$")

        current_card_in_deck = 7
        isFold = False
        data = pickle.dumps(bob_bet, -1)
        client_alice.sendall(data)
        while current_card_in_deck < 10 and not isFold:
            first_turn = True
            while (all_alice_bet != all_bob_bet or first_turn) and not isFold:
                # Get Alice bet
                print("Wait for your opponent")
                command = client_alice.recv(4096)
                command = pickle.loads(command)
                if "fold" in command:
                    bob_money += bank
                    bank = 0
                    print("You win. You have", bob_money, "$")
                    isFold = True
                    break
                if "raise" in command:
                    alice_bet = int(command.split()[1])
                    all_alice_bet += alice_bet
                    alice_money -= alice_bet
                    bank += alice_bet
                    print("Opponent RAISE on", alice_bet)
                if "call" in command:
                    alice_bet = all_bob_bet - all_alice_bet
                    alice_money -= alice_bet
                    all_alice_bet += alice_bet
                    bank += alice_bet
                    print("Opponent CALL on", alice_bet)
                if "check" in command:
                    print("Opponent CHECK")

                if not isFold:
                    first_turn = False
                    print("Opponent: stack -", alice_money, ",", "pot -", all_alice_bet)
                    print("Time to make a bet. Enter help for more information")
                    print("You: stack -", bob_money, ",", "pot -", all_bob_bet)
                    while True:
                        command = input()
                        print("\n")
                        if command == "help":
                            print("To FOLD enter \"fold\" ")
                            print("To CHECK enter \"check\"")
                            print("To RAISE enter \"raise x\", where x is your bet")
                            print("To CALL enter \"call\"\n")
                        else:
                            if "fold" in command:
                                alice_money += bank
                                bank = 0
                                data = pickle.dumps(command, -1)
                                client_alice.sendall(data)
                                print("You lose. You have", bob_money, "$")
                                isFold = True
                                break
                            if "check" in command:
                                data = pickle.dumps(command, -1)
                                client_alice.sendall(data)
                                break
                            if "raise" in command:
                                bob_bet = int(command.split()[1])
                                bob_money -= bob_bet
                                all_bob_bet += bob_bet
                                bank += bob_bet
                                data = pickle.dumps(command, -1)
                                client_alice.sendall(data)
                                break
                            if "call" in command:
                                bob_bet = all_alice_bet - all_bob_bet
                                bob_money -= bob_bet
                                all_bob_bet += bob_bet
                                bank += bob_bet
                                data = pickle.dumps(command, -1)
                                client_alice.sendall(data)
                                break


            if current_card_in_deck < 9 and not isFold:
                # Open one more card
                key_from_bob = bob_individual_keys[current_card_in_deck]
                data = pickle.dumps(key_from_bob, -1)
                client_alice.sendall(data)

                key_from_alice = client_alice.recv(4096)
                key_from_alice = pickle.loads(key_from_alice)

                table_cards.append(decrypt_card(decrypt_card(shuffled_encrypted_cards[current_card_in_deck], key_from_bob), key_from_alice))
                print("Table are:")
                print_cards_in_lst(table_cards)
                print("\n")
            current_card_in_deck += 1

        if not isFold:
            # Compute results
            alice_cards_keys = client_alice.recv(4096)
            alice_cards_keys = pickle.loads(alice_cards_keys)

            data = pickle.dumps(bob_cards_keys1, -1)
            client_alice.sendall(data)

            alice_cards = []
            for i in range(2):
                alice_cards.append(decrypt_card(decrypt_card(shuffled_encrypted_cards[i], bob_individual_keys[i]), alice_cards_keys[i]))

            print("Table are:")
            print_cards_in_lst(table_cards)

            print("Your cards are:")
            print_cards_in_lst(bob_cards_decrypted)

            print("Opponent cards are:")
            print_cards_in_lst(alice_cards)
            result = choose_winner(alice_cards, bob_cards_decrypted, table_cards)
            print("Result =", result)

        print("To exit enter \"exit\"")
        command = input()
        if "exit" in command:
            break
    # Close connection
    client_alice.close()


if __name__ == '__main__':
    main()