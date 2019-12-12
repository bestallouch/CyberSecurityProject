import socket
import pickle
import random
import time
from common import *

## Bob

def Main():
    ## Alice's server for initial reshuffling
    host_alice = '127.0.0.1'
    port_alice = 5006
    client_alice = socket.socket()
    client_alice.connect((host_alice, port_alice))

    print("Connected to Alice.\n")

    shuffled_deck_alice = client_alice.recv(4096)
    shuffled_deck_alice = pickle.loads(shuffled_deck_alice)

    num_cards = len(shuffled_deck_alice)
    bob_key = 2
    print("A deck of ",num_cards," cards received from Alice.")

    ## Deck encryption by bob
    deck_bob = list()
    for i in range(num_cards):
        deck_bob.append(encryptCard(shuffled_deck_alice[i], bob_key))

    ## Shuffle
    random.shuffle(deck_bob)

    print("Deck encrypted and shuffled.\n")
    shuffled_deck_bob = pickle.dumps(deck_bob, -1)
    client_alice.sendall(shuffled_deck_bob)
    print("Deck sent back to Alice.\n")

    shuffled_deck_bob = client_alice.recv(4096)
    shuffled_deck_bob = pickle.loads(shuffled_deck_bob)
    print("Deck received from Alice.")

    for i in range(num_cards):
        shuffled_deck_bob[i] = decryptCard(shuffled_deck_bob[i], bob_key)

    print("Deck decrypted.\n")

    print("Getting individual keys...")
    bob_individual_keys = random.sample(range(1,60),num_cards)
    for i in range(num_cards):
        shuffled_deck_bob[i] = encryptCard(shuffled_deck_bob[i], bob_individual_keys[i])
    print("Deck encrypted by individual keys.\n")


    shuffled_encrypted_cards = pickle.dumps(shuffled_deck_bob, -1)
    client_alice.sendall(shuffled_encrypted_cards)
    print("Deck sent to Alice.\n")


    print("Distributing cards...\n")

    bob_cards_keys2 = client_alice.recv(4096)
    bob_cards_keys2 = pickle.loads(bob_cards_keys2)

    bob_cards = []
    bob_cards_keys1 = []
    alice_cards_keys2 = []

    for i in range(1,num_cards,2):
        bob_cards.append(shuffled_deck_bob[i])
        bob_cards_keys1.append(bob_individual_keys[i])
    
    for i in range(0,num_cards,2):
        alice_cards_keys2.append(bob_individual_keys[i])

    print("A hand of ",num_cards//2," cards received.\n")
    print("Individual keys received.\n")
    print("Sending individual keys of Alice's cards...\n")

    alice_cards_keys2 = pickle.dumps(alice_cards_keys2, -1)
    client_alice.sendall(alice_cards_keys2)
    print('Sent.\n')

    print("Decrypting your cards...\n")
    bob_cards_decrypted = [0 for i in range(num_cards//2)]
    for i in range(num_cards//2):
        bob_cards_decrypted[i] = decryptCard(decryptCard(bob_cards[i],bob_cards_keys1[i]),bob_cards_keys2[i])

    print("Your cards are : ")
    print(bob_cards_decrypted)
    print("\n")

    print("We can start the game now..")
    print("Connecting to the servers...")

    host1 = '127.0.0.1'
    port1 = 5004

    host2 = "127.0.0.1"
    port2 = 5005 

    client_sock1 = socket.socket() # Server 1
    client_sock2 = socket.socket() # Server 2
    
    client_sock1.connect((host1, port1))

    packet = client_sock1.recv(4096)
    dicti = pickle.loads(packet)
    rand_no = dicti["rand_no"]
    public_key = dicti["public_key"]

    client_sock2.connect((host2, port2))

    print("Connected.\n")
    print("Bob! Throw your cards.\n")
    print("Enter the card index.")

    for i in range(5):
        ind = int(input())
        encrypted_sal = public_key.encrypt(bob_cards_decrypted[ind-1]*rand_no)
        data = pickle.dumps(encrypted_sal,-1)

        client_sock2.sendall(data)

        result = client_sock1.recv(1024).decode('ascii')
        print(result)

    ## Close all connections
    client_sock2.close()
    client_sock1.close()
    client_alice.close()
   

if __name__ == '__main__':
    Main()
