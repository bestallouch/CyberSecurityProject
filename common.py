import socket
import pickle
from collections import defaultdict

all_suits = "CSHD"
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
    return values_dct[card_num // 4 + 2], all_suits[card_num % 4]


def print_cards_in_lst(card_lst):
    print([" ".join(get_card_by_num(card_num)) for card_num in card_lst])


def get_hand_values(hand):
    return [num // 4 + 2 for num in hand]


def get_hand_suits(hand):
    return [get_card_by_num(num)[1] for num in hand]


def check_straight_flush(hand):
    if check_flush(hand) and check_straight(hand):
        return True
    else:
        return False


def check_four_of_a_kind(hand):
    values = get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1
    if 4 in value_counts.values():
        return True
    return False


def check_full_house(hand):
    values = get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1
    if 2 in value_counts.values() and 3 in value_counts.values():
        return True
    return False


def check_flush(hand):
    suits = get_hand_suits(hand)
    if len(set(suits)) == 1:
        return True
    else:
        return False


# in progress
def check_straight(hand):
    values = get_hand_values(hand)
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1
    value_range = max(values) - min(values)
    if value_range == 4:
        return True
    else:
        # check straight with low Ace
        if set(values) == set(["A", "2", "3", "4", "5"]):
            return True
        return False


def check_three_of_a_kind(hand):
    values = [i[0] for i in hand]
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1
    if set(value_counts.values()) == set([3, 1]):
        return True
    else:
        return False


def check_two_pairs(hand):
    values = [i[0] for i in hand]
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1
    if sorted(value_counts.values()) == [1, 2, 2]:
        return True
    else:
        return False


def check_one_pairs(hand):
    values = [i[0] for i in hand]
    value_counts = defaultdict(lambda: 0)
    for v in values:
        value_counts[v] += 1
    if 2 in value_counts.values():
        return True
    else:
        return False


def check_hand(hand):
    # TODO: add royal flush
    if check_straight_flush(hand):
        return 9
    if check_four_of_a_kind(hand):
        return 8
    if check_full_house(hand):
        return 7
    if check_flush(hand):
        return 6
    if check_straight(hand):
        return 5
    if check_three_of_a_kind(hand):
        return 4
    if check_two_pairs(hand):
        return 3
    if check_one_pairs(hand):
        return 2
    # TODO: implement same combinations compression
    # always return highest card if no higher hands are found
    return 1
