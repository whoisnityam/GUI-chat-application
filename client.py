import os
import socket
import errno
import sys
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 5678

usrName = tkinter.Tk()
usrName.withdraw()

my_username = simpledialog.askstring("Username", "Please enter your username:", parent=usrName)

if my_username is None or type(my_username) is bool:
    exit()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode("utf-8")
client_socket.send(username_header + username)


def stop():
    os._exit(1)

def send_message(message="Default"):
    message = input_area.get('1.0', 'end')
    message = message.strip()
    if  message == '':
        return
    message = message + '\n'
    # print(repr(message))
    input_area.delete('1.0', 'end')
    
    text_area.config(state="normal")
    text_area.insert('end', "You" + ': ' + message)
    text_area.yview('end')
    text_area.config(state="disabled")

    message = message.encode("utf-8")
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode("utf-8")
    client_socket.send(message_header + message)


def recieve_message():
    while True:
        try:
            while True:
                username_header = client_socket.recv(HEADER_LENGTH)

                if not len(username_header):
                    print("Connection closed by the server")
                    sys.exit()

                username_length = int(username_header.decode("utf-8").strip())
                username = client_socket.recv(username_length).decode("utf-8")

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode("utf-8").strip())
                message = client_socket.recv(message_length).decode("utf-8")

                text_area.config(state="normal")
                text_area.insert('end', username + ': ' + message)
                text_area.yview('end')
                text_area.config(state="disabled")

                # print(f"{username} > {message}")

        except IOError as e:
            if e.errno == errno.ENOTSOCK:
                print("Connection Closed")
                os._exit(1)

            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print("Reading Error", str(e))
                os._exit(1)

            continue

        except Exception as e:
            print("General Error", str(e))
            os._exit(1)

    


win = tkinter.Tk()
win.configure(bg="black")

chat_label = tkinter.Label(win, text="CHATROOM", bg="black", foreground="white")
chat_label.pack(padx=20, pady=5)

text_area = tkinter.scrolledtext.ScrolledText(win, bg="#222222", foreground="#c5c5c5")
text_area.pack(padx=20, pady=5)
text_area.config(state="disabled")

message_label = tkinter.Label(win, text="message:", bg="black", foreground="white" )
message_label.pack(padx=20, pady=5)

input_area = tkinter.Text(win, height=1, bg="#222222", foreground="#c5c5c5")
input_area.pack(padx=20, pady=5)
input_area.bind('<Return>', send_message)

send_button = tkinter.Button(win, text="Send", command=send_message, borderwidth="5")
send_button.pack(padx=20, pady=5)

win.protocol("WM_DELETE_WINDOW", stop)

x = threading.Thread(target=recieve_message)
x.start()

win.mainloop()


