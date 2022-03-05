# Import socket module
from socket import *
from urllib import request

def proxy():
        # Create a TCP server socket
    #(AF_INET is used for IPv4 protocols)
    #(SOCK_STREAM is used for TCP)

    serverSocket = socket(AF_INET, SOCK_STREAM)

    # Assign a port number
    serverPort = 8888

    # Bind the socket to server address and server port
    while(True):
        try:
            serverSocket.bind(("", serverPort))
            break
        except:
            serverPort+=1
            continue
    # Listen to at most 1 connection at a time
    serverSocket.listen(1)
    # Server should be up and running and listening to the incoming connections
    while True:
        print('listening on port {}'.format(serverPort))
        print('Ready to serve...')

        # Set up a new connection from the client
        connectionSocket, addr = serverSocket.accept()
        print("Accept Call from: {}".format(addr))
        # If an exception occurs during the execution of try clause
        # the rest of the clause is skipped
        # If the exception type matches the word after except
        # the except clause is executed
        # Receives the request message from the client
        message = b""
        co = 1
        while True:
            data = connectionSocket.recv(1)
            message += data
            co += 1
            if data == b'\r':
                data = connectionSocket.recv(3)
                if data == b'\n\r\n':
                    break
                else:
                    message += data
        # Check whether the required files exist in the cache
        # if yes,load the file and send a response back to the client
        # print('Read file from cache')
        try:
            # Extract the path of the requested object from the message
            # The path is the second part of HTTP header, identified by [1]
            filename = b""
            for x in message.split()[1].split(b"/")[2:]:
                filename += x

            # Because the extracted path of the HTTP request includes
            # a character '\', we read the path from the second character
            f = open(b"cached_"+filename)
            
            # Store the entire contenet of the requested file in a temporary buffer
            outputdata = f.read()
            print('Read file: {} from cache'.format(str(b"cached_"+filename)[1:]))
            # Send the HTTP response header line to the connection socket
            connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())
            
            # Send the content of the requested file to the connection socket
            for i in range(0, len(outputdata)):
                connectionSocket.send(outputdata[i].encode())
            connectionSocket.send("\r\n".encode())
            
            # Close the client connection socket
            connectionSocket.close()

        except IOError:
            # the file was not found
            # retrieve it from the webserver and put it in local storage

            webServerName = "localhost"
            webServerPort = 6789
            filename = str(filename)[1:-1]
            request = "GET /{} HTTP/1.1\r\nHost: {}:{}\r\n\r\n".format(str(filename)[1:], webServerName, webServerPort)
            print("Request:",request)
            # create TCP socket on client to use for connecting to remote server.  
            clientSocket = socket(AF_INET, SOCK_STREAM)
            # open the TCP connection
            clientSocket.connect((webServerName,webServerPort))
            # perform the http GET request on web server
            clientSocket.send(request.encode())
            # retrieve file
            webServerResp = clientSocket.recv(19)
            print ("Response: ", webServerResp)
            if(webServerResp.split()[1] == b"200"):
                # message = clientSocket.recv(102400)
                message = b""
                while True:
                    data = clientSocket.recv(1)
                    co += 1
                    if data == b"\r":
                        data = clientSocket.recv(1)
                        if data == b'\n':
                            break
                    else:
                        message += data
                print(message)
                connectionSocket.send("""HTTP/1.1 200 OK\r\n Content-Type: text/html\r\n\r\n""".encode())
                connectionSocket.send(message)
                connectionSocket.send("\r\n".encode())
                file = open("cached_"+filename[1:], 'w')
                file.write(message.decode())
                file.close()
            # connectionSocket.send(message.encode())
            # connectionSocket.send("\r\n".encode())
            # close the TCP connection
            connectionSocket.close()

def main():
    proxy()


if __name__ == '__main__':
    main()

