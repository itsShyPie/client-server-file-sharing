# File-sharing client: TCP
# March 2023

from socket import *
import hashlib
import re


def end():
    # Closes client connection
    print(f'[+] User Quit')
    clientSocket.close()


def printList():
    # Receive and print list of available files
    listOfFiles = recvData()
    print(listOfFiles)

    # Check if user would like to download a file from the list
    if listOfFiles != '[+] There are no files on the server':
        while True:

            downloadFileRequest = input('(y):Yes/(n):No. Would you like to'
                                        ' Download a File from the List: \n')
            if downloadFileRequest in ['y', 'n']:
                break
            else:
                print(listOfFiles)
                pass

        # Check for server response
        if downloadFileRequest == 'y':
            sendData(downloadFileRequest)
            download()

        else:
            pass


def upload():
    # Get fileName and protectionState to upload to server
    while True:
        fileName = input("Enter a file name: ")
        try:
            file = open(fileName, 'r')
            break
        except FileNotFoundError:
            pass

    while True:
        protState = input("Would you like the uploaded file to be Open(o)"
                          "or Protected(p): \n")
        if protState in ['o', 'p']:
            break
        else:
            pass

        # Send fileName and protectionState to Server
        sendData(f"{fileName}:{protState}")

    while True:

        # Send data to server
        with open(fileName, 'rb') as f:
            while True:
                bytesRead = f.read(bufferSize)
                if not bytesRead:
                    f.close()
                    break
                sendFile(bytesRead)

            # Receive hash totals for server and client
            clientHashTotal = hash_check(fileName)
            sendData(clientHashTotal)

            # Check for acknowledgement of hash function
            acknowledgement = recvData()
            if acknowledgement == 'ACK':
                print("[+] Hash Success")
                break
            else:
                print("[+] Hash Failed - Retrying")


def download():
    # Ask for filename and send to server with key
    fileName = input("Enter The Name of The File you Want to Download: \n")
    fileNameAndKey = f"{fileName}:{key}"
    sendData(fileNameAndKey)

    # Check if user has permission tto download file
    permission = recvData()
    if permission == 'True':

        while True:

            # Write data from server into file
            with open(fileName, "wb") as f:
                while True:
                    bytesRead = recvFile()
                    f.write(bytesRead)
                    if len(bytesRead) < bufferSize:
                        f.close()
                        break

            # Get and Send clientHashTotal to Server
            serverHashTotal = recvData()
            clientHashTotal = hash_check(fileName)

            # Check client and server hashes match
            if clientHashTotal == serverHashTotal:
                print("Hash Success")
                sendData('ACK')
                break
            else:
                print("Hash Failed - Retrying")
                sendData('N-ACK')

    else:
        print("You do not have the permissions to access this file")


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
        clientSocket.send(dataToSend.encode())
        ack = clientSocket.recv(bufferSize).decode()
        if ack == 'ACK':
            break
        else:
            print('N-ACK')


def sendFile(dataToSend):
    # sendData without .encode
    while True:
        clientSocket.send(dataToSend)
        ack = clientSocket.recv(bufferSize).decode()
        if ack == 'ACK':
            break
        else:
            print('N-ACK')


def recvFile():
    # recvData without .decode
    while True:
        bytesRead = clientSocket.recv(bufferSize)
        if not bytes:
            print("N-ACK")
        else:
            clientSocket.send('ACK'.encode())
            return bytesRead


def recvData():
    # Receives a packet of information and sends a confirmation
    while True:
        bytesRead = clientSocket.recv(bufferSize).decode()
        if not bytes:
            print("N-ACK")
        else:
            clientSocket.send('ACK'.encode())
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

    # Initialise packet size, IP and port
    bufferSize = 1024

    # Check if port number and IP are valid inputs
    while True:
        IP = input("Enter the IP: ")
        # if re.match('^[0-9]{3}.[0-9]{3}.[0-9]{3}.[0-9]{3}$', IP):
        while True:
            try:
                Port = int(input("Enter the host port number: "))
                break
            except ValueError:
                pass
        break

    # Connect to server
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((IP, Port))
    print(f"[+] Connected to {IP}:{Port}")

    # Get user key and option
    while True:
        try:
            key = int(input("Enter your Key: "))
            break
        except ValueError:
            pass
    while True:
        option = input("What would you like to do? \n(u): Upload a file \n(l): "
                       "List Files \n(d): Download a File \n(q): Quit \n") or 'd'
        if option in ['u', 'q', 'd', 'l']:
            break
        else:
            pass

    # Send option and key to server
    optionAndKey = f"{option}:{key}"
    sendData(optionAndKey)

    # Run main function
    main(option)
