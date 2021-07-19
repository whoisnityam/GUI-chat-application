import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 5678

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]
clients = {}

BroadcastName = "[SERVER]".encode('utf-8')
BroadcastNameHeader = f"{len(BroadcastName):<{HEADER_LENGTH}}".encode('utf-8')

def recieve_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return{"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False


while True:
    read_sockets, _, exception_sockets = select.select(
        sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = recieve_message(client_socket)
            for client_socket1 in clients.keys():
                BroadcastMsg = f'{user["data"].decode("utf-8")} Joined the Chat\n'.encode('utf-8')
                BroadcastMsgHeader = f"{len(BroadcastMsg):<{HEADER_LENGTH}}".encode('utf-8')
                if client_socket1 != notified_socket:
                    client_socket1.send(
                        BroadcastNameHeader + BroadcastName + BroadcastMsgHeader + BroadcastMsg)

            sockets_list.append(client_socket)
            clients[client_socket] = user
            print(
                f'Accepeted connection from {client_address[0]}:{client_address[1]} username: {user["data"].decode("utf-8")}')
            
        else:
            message = recieve_message(notified_socket)

            if message is False:
                user = clients[notified_socket]
                print(
                    f"Closed Connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                for client_socket1 in clients.keys():
                    BroadcastMsg = f'{user["data"].decode("utf-8")} Left the Chat\n'.encode('utf-8')
                    BroadcastMsgHeader = f"{len(BroadcastMsg):<{HEADER_LENGTH}}".encode('utf-8')
                    if client_socket1 != notified_socket:
                        client_socket1.send(
                            BroadcastNameHeader + BroadcastName + BroadcastMsgHeader + BroadcastMsg)
                continue

            user = clients[notified_socket]
            print(
                f"Message recieved from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for client_socket in clients.keys():
                if client_socket != notified_socket:
                    client_socket.send(
                        user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        user = clients[notified_socket]
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
        for client_socket1 in clients.keys():
            BroadcastMsg = f'{user["data"].decode("utf-8")} Left the Chat\n'.encode('utf-8')
            BroadcastMsgHeader = f"{len(BroadcastMsg):<{HEADER_LENGTH}}".encode('utf-8')
            if client_socket1 != notified_socket:
                client_socket1.send(BroadcastNameHeader + BroadcastName + BroadcastMsgHeader + BroadcastMsg)
