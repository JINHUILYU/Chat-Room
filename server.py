import socket
import threading
import random

# 全局数据结构：在实际应用中建议使用数据库或其他方式进行持久化
USERS = {}  # { username: {'socket': socket对象, 'groups': set() } }
GROUPS = {}  # { group_name: set of usernames }


def broadcast_world(message, exclude_username=None):
    """
    向所有在线用户广播世界消息。
    exclude_username: 如果不想把消息发给发送者本身，可以填写此用户名；否则设为None
    """
    for user, data in USERS.items():
        if user != exclude_username:
            try:
                data['socket'].sendall((f"[世界] {message}\n").encode())
            except:
                # 如果发送失败，可在此进行进一步处理
                pass


def broadcast_group(group_name, message, exclude_username=None):
    """
    向指定群组内的用户广播消息。
    """
    if group_name in GROUPS:
        for user in GROUPS[group_name]:
            if user != exclude_username:
                try:
                    USERS[user]['socket'].sendall((f"[群 {group_name}] {message}\n").encode())
                except:
                    pass


def handle_client(client_socket, addr):
    """
    处理与单个客户端的通信逻辑。
    """
    username = None
    try:
        # 提示用户进行访客或注册操作
        client_socket.sendall("请输入操作：GUEST 或 REGISTER <username> <password>\n".encode())
        data = client_socket.recv(1024).decode().strip()

        if not data:
            client_socket.sendall("未收到任何指令，断开连接。\n".encode())
            client_socket.close()
            return

        cmd_parts = data.split()
        cmd = cmd_parts[0].upper()

        if cmd == 'GUEST':
            # 分配一个随机用户名
            username = "Guest" + str(random.randint(1000, 9999))
            USERS[username] = {
                'socket': client_socket,
                'groups': set()
            }
            client_socket.sendall((f"欢迎你, {username}!\n").encode())

        elif cmd == 'REGISTER' and len(cmd_parts) == 3:
            # 注册用户（此示例仅做内存保存，不进行密码验证）
            reg_username = cmd_parts[1]
            reg_password = cmd_parts[2]  # 这里只是示意，实际可以进行验证或加密等

            # 判断用户名是否已存在
            if reg_username in USERS:
                client_socket.sendall("用户名已存在，请重新连接或使用其他用户名。\n".encode())
                client_socket.close()
                return
            else:
                username = reg_username
                USERS[username] = {
                    'socket': client_socket,
                    'groups': set()
                }
                client_socket.sendall((f"注册成功，欢迎你, {username}!\n").encode())

        else:
            client_socket.sendall("指令无效，断开连接。\n".encode())
            client_socket.close()
            return

        # 提示用户已进入世界频道
        client_socket.sendall("你已进入世界频道，可以输入 'WORLD <消息>' 发送世界消息。\n".encode())

        # 主循环：持续接收用户的指令
        while True:
            data = client_socket.recv(1024)
            if not data:
                break  # 客户端断开

            message = data.decode().strip()
            if not message:
                continue

            # 消息格式：
            # 1) WORLD <msg>              --> 发送世界频道消息
            # 2) PRIVATE <username> <msg> --> 私聊消息
            # 3) CREATEGROUP <groupname>  --> 创建群聊
            # 4) JOINGROUP <groupname>    --> 加入群聊
            # 5) GROUP <groupname> <msg>  --> 在群聊内发送消息

            parts = message.split(maxsplit=2)
            cmd = parts[0].upper()

            if cmd == 'WORLD':
                # 向世界频道发送消息
                if len(parts) >= 2:
                    # WORLD 后面全部当作消息
                    world_msg = parts[1] if len(parts) == 2 else parts[1] + " " + parts[2]
                    broadcast_world(f"{username}: {world_msg}", None)
                else:
                    client_socket.sendall("用法: WORLD <消息>\n".encode())

            elif cmd == 'PRIVATE':
                # 私聊
                if len(parts) < 3:
                    client_socket.sendall("用法: PRIVATE <username> <消息>\n".encode())
                else:
                    target_user = parts[1]
                    private_msg = parts[2]
                    if target_user in USERS:
                        USERS[target_user]['socket'].sendall((f"[私聊] {username}: {private_msg}\n").encode())
                    else:
                        client_socket.sendall(f"用户 {target_user} 不存在或未在线。\n".encode())

            elif cmd == 'CREATEGROUP':
                # 创建群聊
                if len(parts) < 2:
                    client_socket.sendall("用法: CREATEGROUP <groupname>\n".encode())
                else:
                    group_name = parts[1]
                    if group_name in GROUPS:
                        client_socket.sendall("该群已存在，无法重复创建。\n".encode())
                    else:
                        GROUPS[group_name] = {username}
                        USERS[username]['groups'].add(group_name)
                        client_socket.sendall((f"成功创建并加入群: {group_name}\n").encode())

            elif cmd == 'JOINGROUP':
                # 加入群聊
                if len(parts) < 2:
                    client_socket.sendall("用法: JOINGROUP <groupname>\n".encode())
                else:
                    group_name = parts[1]
                    if group_name not in GROUPS:
                        client_socket.sendall("该群不存在。\n".encode())
                    else:
                        GROUPS[group_name].add(username)
                        USERS[username]['groups'].add(group_name)
                        client_socket.sendall((f"成功加入群: {group_name}\n").encode())

            elif cmd == 'GROUP':
                # 在群聊内发消息
                if len(parts) < 3:
                    client_socket.sendall("用法: GROUP <groupname> <消息>\n".encode())
                else:
                    group_name = parts[1]
                    group_msg = parts[2]
                    # 判断用户是否在该群组内
                    if group_name in USERS[username]['groups']:
                        broadcast_group(group_name, f"{username}: {group_msg}", username)
                    else:
                        client_socket.sendall(f"你尚未加入该群: {group_name}\n".encode())

            else:
                # 未知指令
                client_socket.sendall("未知指令，请重新输入。\n".encode())

    except Exception as e:
        print(f"客户端 {addr} 出现错误: {e}")
    finally:
        # 用户断线或出错后，清理服务器端的用户数据
        if username and username in USERS:
            del USERS[username]
        client_socket.close()


def start_server(host='0.0.0.0', port=19090):
    """
    启动服务器并监听端口。
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"服务器已启动，正在监听 {host}:{port}...")

    while True:
        client_socket, addr = server.accept()
        print(f"接受到来自 {addr} 的连接")
        # 为每个客户端开启一个新线程处理
        t = threading.Thread(target=handle_client, args=(client_socket, addr))
        t.start()


if __name__ == '__main__':
    start_server()
