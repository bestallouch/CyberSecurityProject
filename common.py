import socket
import pickle

## A commutative encryption function
def encryptCard(val, key):
    return val ^ key


## Complementary decryption function
def decryptCard(val, key):
    return val ^ key


## Send Deck to connection
def sendDeck(connection, address, deck):
    data = pickle.dumps(deck, -1)
    connection.sendall(data)

## Set up server for messages
def setServer(host, port, num_connections):
    server = socket.socket()
    server.bind((host, port))
    server.listen(num_connections)
    return server


## Connect to server for messages
def connectToServer(host, port):
    client_sock = socket.socket()
    client_sock.connect((host, port))
    return client_sock


## Send Key value to other party in String format
def sendKey(connection, key):
    connection.send(key.encode('ascii'))

