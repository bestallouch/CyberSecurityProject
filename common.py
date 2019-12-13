import socket
import pickle
import math

def _rotate_left(val, r_bits, max_bits):
    v1 = (val << r_bits % max_bits) & (2 ** max_bits - 1)
    v2 = ((val & (2 ** max_bits - 1)) >> (max_bits - (r_bits % max_bits)))
    return v1 | v2


def _rotate_right(val, r_bits, max_bits):
    v1 = ((val & (2 ** max_bits - 1)) >> r_bits % max_bits)
    v2 = (val << (max_bits - (r_bits % max_bits)) & (2 ** max_bits - 1))
    return v1 | v2


def _expand_key(key, wordsize, rounds):
    # Pads _key so that it is aligned with the word size, then splits it into words
    def _align_key(key, align_val):
        while len(str(key)) % (align_val):
            key += b'\x00'  # Add 0 bytes until the _key length is aligned to the block size

        L = []
        for i in range(0, len(key), align_val):
            L.append(int.from_bytes(key[i:i + align_val], byteorder='little'))

        return L

    # generation function of the constants for the extend step
    def _const(w):
        if w == 16:
            return (0xB7E1, 0x9E37)  # Returns the value of P and Q
        elif w == 32:
            return (0xB7E15163, 0x9E3779B9)
        elif w == 64:
            return (0xB7E151628AED2A6B, 0x9E3779B97F4A7C15)

    # Generate pseudo-random list S
    def _extend_key(w, r):
        P, Q = _const(w)
        S = [P]
        t = 2 * (r + 1)
        for i in range(1, t):
            S.append((S[i - 1] + Q) % 2 ** w)

        return S

    def _mix(L, S, r, w, c):
        t = 2 * (r + 1)
        m = max(c, t)
        A = B = i = j = 0

        for k in range(3 * m):
            A = S[i] = _rotate_left(S[i] + A + B, 3, w)
            B = L[j] = _rotate_left(L[j] + A + B, A + B, w)

            i = (i + 1) % t
            j = (j + 1) % c

        return S

    aligned = _align_key(key, wordsize // 8)
    extended = _extend_key(wordsize, rounds)

    S = _mix(aligned, extended, rounds, wordsize, len(aligned))

    return S


def _encrypt_block(data, expanded_key, blocksize, rounds):
    w = blocksize // 2
    b = blocksize // 8
    mod = 2 ** w

    A = int.from_bytes(data[:b // 2], byteorder='little')
    B = int.from_bytes(data[b // 2:], byteorder='little')

    A = (A + expanded_key[0]) % mod
    B = (B + expanded_key[1]) % mod

    for i in range(1, rounds + 1):
        A = (_rotate_left((A ^ B), B, w) + expanded_key[2 * i]) % mod
        B = (_rotate_left((A ^ B), A, w) + expanded_key[2 * i + 1]) % mod

    res = A.to_bytes(b // 2, byteorder='little') + B.to_bytes(b // 2, byteorder='little')
    return res


def _decrypt_block(data, expanded_key, blocksize, rounds):
    w = blocksize // 2
    b = blocksize // 8
    mod = 2 ** w

    A = int.from_bytes(data[:b // 2], byteorder='little')
    B = int.from_bytes(data[b // 2:], byteorder='little')

    for i in range(rounds, 0, -1):
        B = _rotate_right(B - expanded_key[2 * i + 1], A, w) ^ A
        A = _rotate_right((A - expanded_key[2 * i]), B, w) ^ B

    B = (B - expanded_key[1]) % mod
    A = (A - expanded_key[0]) % mod

    res = A.to_bytes(b // 2, byteorder='little') + B.to_bytes(b // 2, byteorder='little')
    return res
from collections import defaultdict

all_suits = "CSHD"
values_dct = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9", 10: "10", 11: "J", 12: "Q", 13: "K",
              14: "A"}
hand_dct = {9: "straight-flush", 8: "four-of-a-kind", 7: "full-house", 6: "flush", 5: "straight", 4: "three-of-a-kind",
            3: "two-pairs", 2: "one-pair", 1: "highest-card"}


# A commutative encryption function
def encryptCard(val, key):
    key =(key).to_bytes(2, byteorder='little')
    expanded_key = _expand_key(key, 32, 4)
    val = (val).to_bytes(2, byteorder='little')
    return _encrypt_block(val, expanded_key, 32, 4)

# Complementary decryption function
def decryptCard(val, key):
    key =(key).to_bytes(2, byteorder='little')
    expanded_key = _expand_key(key, 32, 4)
    val = (val).to_bytes(2, byteorder='little')
    return _decrypt_block(val, expanded_key, 32, 4)


# Send Deck to connection
def sendDeck(connection, address, deck):
    data = pickle.dumps(deck, -1)
    connection.sendall(data)


# Set up server for messages
def setServer(host, port, num_connections):
    server = socket.socket()
    server.bind((host, port))
    server.listen(num_connections)
    return server


# Connect to server for messages
def connectToServer(host, port):
    client_sock = socket.socket()
    client_sock.connect((host, port))
    return client_sock


# Send Key value to other party in String format
def sendKey(connection, key):
    connection.send(key.encode('ascii'))


def get_card_by_num(card_num: int):
    return values_dct[card_num // 4 + 2], all_suits[card_num % 4]


def print_cards_in_lst(card_lst):
    print([" ".join(get_card_by_num(card_num)) for card_num in card_lst])


def get_hand_values(hand):
    return [num // 4 + 2 for num in hand]


def get_hand_suits(hand):
    return [get_card_by_num(num)[1] for num in hand]
