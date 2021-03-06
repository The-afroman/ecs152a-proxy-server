# Import socket module
from socket import *


def main():
    # Create a TCP server socket
    # (AF_INET is used for IPv4 protocols)
    # (SOCK_STREAM is used for TCP)
    serverSocket = socket(AF_INET, SOCK_STREAM)

    # Assign a port number
    serverPort = 8888

    # Bind the socket to server address and server port
    while(True):
        # try to bind socket to port
        try:
            serverSocket.bind(("", serverPort))
            break
        except:
            # increment port and try again
            serverPort += 1
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
        while True:
            data = connectionSocket.recv(1)
            message += data
            if data == b'\r':
                data = connectionSocket.recv(3)
                if not data:
                    break
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
            message_path = b""
            message = message.split()[1]
            message_file = message.split(b"/")
            for x in message_file[2:]:
                filename += b"_"
                filename += x
                message_path+=b"/"
                message_path+=x
            if message_path == b"" : message_path = b"/"

            # get server name and port
            message_path = message_path.split(b":")[0]
            message_file = message_file[1].split(b":")
            webServerName = str(message_file[0])[2:-1]
            if len(message_file) > 1:
                webServerPort = int(str(message_file[1])[2:-1])
            else:
                webServerPort = 80
            print(webServerName, webServerPort)

            # Because the extracted path of the HTTP request includes
            # a character '\', we read the path from the second character
            f = open("cached_{}{}".format(webServerName, filename.decode()))

            # Store the entire contenet of the requested file in a temporary buffer
            outputdata = f.read()
            print("Read file:", f.name)
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
            filename = str(filename)[1:-1]
            request = "GET {} HTTP/1.1\r\nHost: {}:{}\r\n\r\n".format(
                message_path.decode(), webServerName, webServerPort)
            print("Request:", request)
            # create TCP socket on client to use for connecting to remote server.
            clientSocket = socket(AF_INET, SOCK_STREAM)
            # open the TCP connection
            try:
                # connect to webserver
                clientSocket.connect((webServerName, webServerPort))
                # perform the http GET request on web server
                clientSocket.send(request.encode())
                # get response header
                webServerResp = b""
                while True:
                    data = clientSocket.recv(1)
                    if not data:
                        break
                    if data == b"\r":
                        webServerResp += data
                        data = clientSocket.recv(3)
                        if data == b"\n\r\n":
                            webServerResp += data
                            break
                        else:
                            webServerResp += data
                    else:
                        webServerResp += data

                print("Response: ", webServerResp.decode("utf-8"))
                # check status if not 200 OK then don't continue
                if(webServerResp.split()[1] == b"200"):
                    # send HTTP header to client
                    connectionSocket.send(
                        """HTTP/1.1 200 OK\r\n Content-Type: text/html\r\n\r\n""".encode())
                    # get document from webserver
                    message = b""
                    while True:
                        data = clientSocket.recv(1024)
                        if not data:
                            break
                        # send the document to client
                        connectionSocket.send(data)
                        print(data.decode("utf-8"), end='')
                        message += data
                    connectionSocket.send("\r\n".encode())
                    print("\n", end='')
                    # cache the document in local storage
                    file = open("cached_{}{}".format(
                        webServerName, filename[1:]), 'w')
                    file.write(message.decode())
                    file.close()
                    print("cached_{}{} written to cache\n".format(
                        webServerName, filename[1:]))
                else:
                    # error not found or other error, unable to retrieve file from destination
                    connectionSocket.send(
                        "HTTP/1.1 404 Not Found\r\n\r\n".encode())
                    connectionSocket.send(
                        "<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())

            except:
                # close the TCP webserver connection
                clientSocket.close()
            # close the TCP connection
            connectionSocket.close()


if __name__ == '__main__':
    main()
