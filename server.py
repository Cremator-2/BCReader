import socket


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


if __name__ == "__main__":

    sock = socket.socket()

    print("IP: {}. Waiting connection...".format(get_ip_address()))
    sock.bind(("", 9090))
    sock.listen(1)

    conn, addr = sock.accept()

    try:
        print("Connection established:", addr)

        while True:
            client_mes = conn.recv(1024).decode()
            if not client_mes:
                break

            print("Client:", client_mes)

            server_mes = input("Server: ")
            conn.send(server_mes.encode())
            if server_mes == "Exit":
                break

        print("Connection closed")
    except Exception as err:
        print("Error: ", err)
    finally:
        conn.close()
