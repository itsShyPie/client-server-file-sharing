# File-sharing server: TCP
# March 2023

from socket import *
import hashlib

# RUN THIS CODE ON TWO SEPARATE COMPUTERS. OTHERWISE, ADD STRING TO DOWNLOADED FILES

def end():

    # Closes client connection
    print(f'[+] User {addr} Quit')
    connectionSocket.close()


def printList():

    # Initialise file variables
    securityFile = open("securityFile.txt", 'r')
    listOfFiles = ''

    # Append open and key matching files to a list
    for x in securityFile:
        lineItem = x.split()

        if lineItem[0] == key or lineItem[0] == "open":
            listOfFiles += lineItem[1] + "\n"

    # Send list of available files to Client
    if listOfFiles == '':
        sendData("[+] There are no files on this server")
    else:
        sendData(listOfFiles)

    # Receive 'y' or 'n' for file download
    ack = recvData()
    if ack == 'y':
        securityFile.close()
        download()
    else:
        end()


def upload():

    # Receive fileName and protectionState from client
    fileNameandProtState = recvData()
    fileName, protState = fileNameandProtState.split(":")

    # Add file to securityFile
    writeToSecurityFile(protState, fileName)

    while True:

        # Write data from client to file
        with open(fileName, "wb") as f:
            while True:
                bytesRead = recvFile()
                f.write(bytesRead)
                if len(bytesRead) < bufferSize:
                    f.close()
                    break

        # Get and Send serverHashTotal to Server
        serverHashTotal = hash_check(fileName)
        clientHashTotal = recvData()

        # Check for acknowledgement of hash function
        if clientHashTotal == serverHashTotal:
            print("Hash Success")
            sendData('ACK')
            break
        else:
            print("Hash Failed - Retrying")
            sendData('N-ACK')
            pass

def download():

    # Receive filename and key from client
    fileNameAndKey = recvData()
    fileName, key = fileNameAndKey.split(":")
    fileToSend = b''

    # Check if user has permission to download file
    permission = perm_check(fileName, key)
    sendData(permission)
    if permission == 'True':

        while True:

            # Send data to client
            with open(fileName, 'rb') as f:
                while True:
                    bytesRead = f.read(bufferSize)
                    if not bytesRead:
                        f.close()
                        break
                    sendFile(bytesRead)

            # Receive hash totals for server and client
            serverHashTotal = hash_check(fileName)
            sendData(serverHashTotal)

            # Check client and server hashes match
            acknowledgement = recvData()
            if acknowledgement == 'ACK':
                print("[+] Hash Success")
                break
            else:
                print("[+] Hash Failed - Retrying")

    else:
        pass


def writeToSecurityFile(protState, fileName):

    # Write upload file entry to security file for validation
    securityFile = open("securityFile.txt", 'w')

    if protState == 'o':
        securityFile.write("open " + fileName + "\n")
    else:
        securityFile.write(key + " " + fileName + "\n")

    securityFile.close()


def perm_check(filename, key):

    # Check through all entries in securityFile to see if client has permission to download
    secFile = open("securityFile.txt", "r")
    for x in secFile:
        pwd, name = x.split()
        if (pwd == key or pwd == 'open') and name == filename:
            return 'True'
    return 'False'


def hash_check(fileName):

    # Splits file to bufferSize and updates a cumulative hash value
    hashObj = hashlib.md5()
    with open(fileName, 'rb') as f:
        while True:
            ReadBytes = f.read(bufferSize)
            hashObj.update(ReadBytes)
            if not ReadBytes:
                break
    hashObj = str(hashObj.hexdigest())
    f.close()
    return hashObj


def sendData(dataToSend):

    # Sends a packet of information and receives a confirmation
    while True:
        connectionSocket.send(dataToSend.encode())
        ack = connectionSocket.recv(bufferSize).decode()
        if ack == 'ACK':
            break
        else:
            print('N-ACK')


def sendFile(dataToSend):

    # sendData without .encode
    while True:
        connectionSocket.send(dataToSend)
        ack = connectionSocket.recv(bufferSize).decode()
        if ack == 'ACK':
            break
        else:
            print('N-ACK')


def recvData():

    # recvData without .decode
    while True:
        bytesRead = connectionSocket.recv(bufferSize).decode()
        if not bytes:
            print("N-ACK")
        else:
            connectionSocket.send('ACK'.encode())
            return bytesRead


def recvFile():

    # Receives a packet of information and sends a confirmation
    while True:
        bytesRead = connectionSocket.recv(bufferSize)
        if not bytes:
            print("N-ACK")
        else:
            connectionSocket.send('ACK'.encode())
            return bytesRead


def main(option):

    if option == 'q':
        end()
    if option == 'l':
        printList()
    if option == 'u':
        upload()
    if option == 'd':
        download()


if __name__ == "__main__":

    # Initialise variables needed
    IP = "127.0.0.1"  # use this machine's network IP to accept clients on other devices
    Port = 4000  # port the server listens on
    bufferSize = 1024
    securityFile = open('securityFile.txt', "a")
    securityFile.close()
    string = ''
    string = 'Downloaded' # UNCOMMENT THIS LINE IF RUNNING ON ONE DEVICE

    # Start Server up (Listening)
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind((IP, Port))
    serverSocket.listen(1)
    print('[+] The server is ready to receive')

    while True:

        # Connect Client
        connectionSocket, addr = serverSocket.accept()
        print(f"[+] {addr} is Connected")

        # Get Option and key from user
        request = recvData()
        option, key = request.split(":")

        # Run main function
        main(option)