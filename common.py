import socket
import pickle
import itertools
from pocker import check_hand

all_suits = [u"\u2660".encode('utf-8'),  # spades
             u"\u2764".encode('utf-8'),  # hearts
             u"\u2666".encode('utf-8'),  # diamonds
             u"\u2663".encode('utf-8')  # clubs
             ]

values_dct = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10", 11: "J", 12: "Q", 13: "K",
              14: "A"}
hand_dct = {9: "straight-flush", 8: "four-of-a-kind", 7: "full-house", 6: "flush", 5: "straight", 4: "three-of-a-kind",
            3: "two-pairs", 2: "one-pair", 1: "highest-card"}


# A commutative encryption function
def encrypt_card(val, key):
    return val ^ key


# Complementary decryption function
def decrypt_card(val, key):
    return val ^ key


# Send Deck to connection
def send_deck(connection, address, deck):
    data = pickle.dumps(deck, -1)
    connection.sendall(data)


# Set up server for messages
def set_server(host, port, num_connections):
    server = socket.socket()
    server.bind((host, port))
    server.listen(num_connections)
    return server


# Connect to server for messages
def connect_to_server(host, port):
    client_sock = socket.socket()
    client_sock.connect((host, port))
    return client_sock


# Send Key value to other party in String format
def send_key(connection, key):
    connection.send(key.encode('ascii'))


def get_card_by_num(card_num: int):
    return values_dct[card_num // 4 + 2], (all_suits[card_num % 4]).decode("utf-8")


def print_cards_in_lst(card_lst):
    print([" ".join(get_card_by_num(card_num)) for card_num in card_lst])


def get_hand_values(hand):
    return [num // 4 + 2 for num in hand]


def get_hand_suits(hand):
    return [get_card_by_num(num)[1] for num in hand]

