# Import socket module
from socket import *

def main():
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
        while True:
            data = connectionSocket.recv(1)
            message += data
            if data == b'\r':
                data = connectionSocket.recv(3)
                if not data: break
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
            message = message.split()[1].split(b"/")
            for x in message[2:]:
                filename += x
            
            # get server name and port
            message = message[1].split(b":")
            webServerName = str(message[0])[2:-1]
            webServerPort = int(str(message[1])[2:-1])
            print(webServerName, webServerPort)

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
            filename = str(filename)[1:-1]
            request = "GET /{} HTTP/1.1\r\nHost: {}:{}\r\n\r\n".format(str(filename)[1:], webServerName, webServerPort)
            print("Request:",request)
            # create TCP socket on client to use for connecting to remote server.  
            clientSocket = socket(AF_INET, SOCK_STREAM)
            # open the TCP connection
            try:
                clientSocket.connect((webServerName,webServerPort))

                # perform the http GET request on web server
                clientSocket.send(request.encode())
                # retrieve file
                webServerResp = b""
                while True:
                        data = clientSocket.recv(1)
                        if not data: break
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
                # webServerResp = clientSocket.recv(19)
                print ("Response: ", webServerResp)
                if(webServerResp.split()[1] == b"200"):
                    # message = clientSocket.recv(102400)
                    message = b""
                    while True:
                        data = clientSocket.recv(1)
                        if not data: break
                        message += data
                    print(message)
                    connectionSocket.send("""HTTP/1.1 200 OK\r\n Content-Type: text/html\r\n\r\n""".encode())
                    connectionSocket.send(message)
                    connectionSocket.send("\r\n".encode())
                    file = open("cached_"+filename[1:], 'w')
                    file.write(message.decode())
                    file.close()
                else:
                    connectionSocket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
                    connectionSocket.send("<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n".encode())
                # close the TCP connection
            except:
                clientSocket.close()
            connectionSocket.close()

if __name__ == '__main__':
    main()

