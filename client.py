import socket
import threading

# 尝试导入 readline
try:
    import readline
except ImportError:
    print("警告: 当前环境不支持 'readline'，Tab 补全功能可能无法使用。")

# 定义可供补全的常用命令
COMMANDS = [
    "GUEST",
    "REGISTER",
    "WORLD",
    "PRIVATE",
    "CREATEGROUP",
    "JOINGROUP",
    "GROUP"
]

def completer(text, state):
    """
    readline 补全函数:
    - text: 当前已输入的内容（光标所在处之前的部分）
    - state: 第几次尝试匹配，0 表示首次
    返回匹配的字符串（或 None）
    """
    # 根据已输入的部分 text，在 COMMANDS 中查找所有匹配的项
    matches = [cmd for cmd in COMMANDS if cmd.startswith(text.upper())]
    if state < len(matches):
        return matches[state]
    else:
        return None

def receive_messages(sock):
    """
    子线程: 持续接收来自服务器的消息并打印到本地控制台。
    """
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                # 服务器断开或出错
                print("与服务器的连接已断开。")
                break
            print(data.decode(), end='\n')
        except:
            print("接收消息时出现错误，连接中断。")
            break

def main():
    host = 'localhost'  # 服务器 IP 或域名
    port = 19090        # 服务器端口

    # 若 readline 可用，则开启 tab 补全
    if 'readline' in globals():
        readline.set_completer(completer)
        # 在某些平台上，可能需要加上 "bind ^I" 或其他命令
        readline.parse_and_bind("tab: complete")

    # 建立与服务器的 TCP 连接
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"已连接到服务器 {host}:{port}")

    # 开启接收消息的线程
    t = threading.Thread(target=receive_messages, args=(sock,))
    t.daemon = True
    t.start()

    print("可以输入以下命令进行操作：")
    print("1) GUEST                   --> 以访客身份进入")
    print("2) REGISTER <user> <pass>  --> 注册账户（示例仅保存在服务器内存）")
    print("3) WORLD <消息>            --> 世界频道聊天")
    print("4) PRIVATE <用户名> <消息> --> 私聊")
    print("5) CREATEGROUP <群名>      --> 创建群聊")
    print("6) JOINGROUP <群名>        --> 加入群聊")
    print("7) GROUP <群名> <消息>     --> 在群聊内发送消息")
    print("输入 quit 或 Ctrl+C 可退出。")

    # 主循环：获取用户输入，发送给服务器
    while True:
        try:
            msg = input()
            if not msg:
                continue
            if msg.lower() == 'quit':
                break  # 用户主动退出
            sock.sendall(msg.encode())
        except KeyboardInterrupt:
            print("\n用户终止。")
            break
        except Exception as e:
            print(f"发送消息时出现错误: {e}")
            break

    # 退出时关闭套接字
    sock.close()
    print("客户端已退出。")

if __name__ == "__main__":
    main()
