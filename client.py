from socket import *

serverName = "localhost"
serverPort = 12000

# create TCP socket on client to use for connecting to remote server.  
clientSocket = socket(AF_INET, SOCK_STREAM)

# open the TCP connection
clientSocket.connect((serverName,serverPort))

# interactively get user's line to be converted to upper case
sentence = input("Input lowercase sentence: ")

# send the user's line over the TCP connection
clientSocket.send(sentence.encode())

#output to console what is sent to the server
print ("Sent to Make Upper Case Server: ", sentence)

# get user's line back from server having been modified by the server
modifiedSentence = clientSocket.recv(1024)

# output the modified user's line
print ("From Server: ", modifiedSentence)

# close the TCP connection
clientSocket.close()