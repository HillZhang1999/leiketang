import socket


def ChatServer(port):
    """
    在指定端口开启一个聊天服务器（基于UDP）
    :param port:
    :return:
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    addr = ("127.0.0.1", port)
    udp_socket.bind(addr)

    print("udp server on %s: %s" % (addr[0], addr[1]))

    user = {}  # {addr: name}
    while True:
        try:
            # data是接收的数据，addr是对方的ip和端口
            data, addr = udp_socket.recvfrom(1024)
            if addr not in user:
                if user:
                    udp_socket.sendto(("直播间成员："+",".join([x for x in user.values()])).encode("utf-8"), addr)
                user[addr] = data.decode("utf-8")
                for address in user:
                    udp_socket.sendto(data + "进入聊天室...".encode("utf-8"), address)
                continue

            data_decoded = data.decode("utf-8")
            if "EXIT" in data_decoded:
                name = user[addr]
                user.pop(addr)
                for address in user:
                    udp_socket.sendto((name + "离开聊天室...").encode("utf-8"), address)
            else:
                if "已被踢出直播间" in data_decoded:
                    name = data_decoded.rstrip("*" * 6).lstrip("已被踢出直播间" + "*" * 6)
                    for key in user.keys():
                        if user[key] == name:
                            user.pop(key)
                print("%s: %s ---> %s" % (addr[0], addr[1], data.decode("utf-8")))
                for address in user:
                    udp_socket.sendto(data, address)

        except ConnectionResetError:
            print("someone left unexpect.")

    udp_socket.close()

if __name__ == "__main__":
    ChatServer(1234)