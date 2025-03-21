# 聊天室项目

本项目是一个基于 **Python Socket** + **Threading** 实现的简易多用户聊天系统，提供以下功能：

1. **访客 / 注册登录**  
   - 访客：随机分配一个用户名（如 `Guest1234`）  
   - 注册：输入用户名和密码，后续可复用此账号  
2. **世界频道**  
   - 所有用户默认加入世界频道  
   - 世界频道中发送的消息，所有在线用户均可见  
3. **私聊**  
   - 可以与指定的单个用户进行私聊  
4. **群聊**  
   - 用户可以创建群聊  
   - 可以加入群聊，并在群组内单独聊天  
5. **Tab 补全**  
   - 客户端支持在输入命令时按 **Tab** 键自动补全指令（`WORLD`, `PRIVATE`, `CREATEGROUP` 等）  

> **提示**：示例中对用户账号、密码等仅做了简单的内存存储，未做严谨的安全加密和持久化，适用于演示/学习场景。若要在生产环境中使用，请根据需求进行完善。

---

## 目录
1. [项目结构](#项目结构)
2. [环境依赖](#环境依赖)
3. [使用步骤](#使用步骤)
4. [客户端命令说明](#客户端命令说明)
5. [常见问题](#常见问题)
6. [可能的扩展方向](#可能的扩展方向)

---

## 项目结构

```
.
├── README.md            # 项目说明文档
├── server.py            # 服务器端源码
└── client.py            # 客户端源码
```

---

## 环境依赖

- **Python 3.7+**（建议 3.8 及以上版本）
- **readline**（或 `pyreadline3` 等第三方库，主要用于 Windows 环境下实现 Tab 自动补全）
  - 在 macOS / Linux 环境通常已内置 `readline`
  - 如果在 Windows 上出现无法使用 Tab 自动补全，可执行 `pip install pyreadline3` 或其他兼容版本

---

## 使用步骤

1. **安装依赖（可选）**  
   如果在 Windows 环境需要 Tab 自动补全，请安装 `pyreadline3`：
   ```bash
   pip install pyreadline3
   ```

2. **启动服务器**  
   在项目根目录下，打开一个终端，运行：
   ```bash
   python server.py
   ```
   若启动成功，会提示：  
   ```
   服务器已启动，正在监听 0.0.0.0:19090...
   ```

3. **启动客户端**  
   在另一个终端窗口执行：
   ```bash
   python client.py
   ```
   若连接成功，会提示：  
   ```
   已连接到服务器 localhost:19090
   可以输入以下命令进行操作：
   1) GUEST
   2) REGISTER user pass
   ...
   输入 quit 或 Ctrl+C 可退出。
   请输入操作：GUEST 或 REGISTER <username> <password>
   ```

4. **进行登录/注册**  
   - **访客登录**：输入 `GUEST`  
   - **注册账号**：输入 `REGISTER alice 123456`  
     （示例：注册一个用户名为 `alice`、密码为 `123456` 的新账号）  

5. **输入命令进行聊天**  
   - 按下 **Tab** 可以尝试自动补全输入的命令  
   - 发送各类消息（世界频道、私聊、群聊等），详见 [客户端命令说明](#客户端命令说明)

6. **退出客户端**  
   - 在客户端输入 `quit`  
   - 或者直接按下 `Ctrl + C`

---

## 客户端命令说明

登录成功后，可以使用以下命令进行聊天和管理操作：

1. **WORLD \<消息\>**  
   - 向世界频道发送消息，所有在线用户都可见  
   - 例如：`WORLD 大家好，我是新来的！`

2. **PRIVATE \<对方用户名\> \<消息\>**  
   - 向指定用户私聊  
   - 例如：`PRIVATE Tom 你好呀`

3. **CREATEGROUP \<群名\>**  
   - 创建一个新群聊，并自动加入该群  
   - 例如：`CREATEGROUP study_group`

4. **JOINGROUP \<群名\>**  
   - 加入已有的群聊  
   - 例如：`JOINGROUP study_group`

5. **GROUP \<群名\> \<消息\>**  
   - 在指定群聊内发送消息  
   - 例如：`GROUP study_group 大家晚上好！`

6. **quit**  
   - 退出客户端（也可使用 `Ctrl + C`）

---

## 常见问题

1. **在 Windows 下，Tab 键无法补全命令？**  
   - 确认是否已安装了 `pyreadline3` 或类似库：  
     ```bash
     pip install pyreadline3
     ```
   - 若仍无效，可能与终端环境或 Python 版本有关，可尝试使用 Git Bash 或 WSL。

2. **为什么提示用户名已存在？**  
   - 同一个服务器运行期间，如果已有用户注册了某个名称，再次注册会提示重复。  
   - 若要重新开始，可以重启服务器清空内存数据。

3. **为什么世界频道消息或私聊消息没有收到？**  
   - 确认服务器端是否报错或客户端是否断开。  
   - 若网络延迟或中断，也可能导致消息丢失或延迟。

---

## 可能的扩展方向

- **消息持久化**：将用户信息、聊天记录等存入数据库（如 SQLite / MySQL / Redis），重启后依然可用  
- **更完善的注册 / 登录验证**：对密码进行哈希加密，限制重复用户名，提供找回密码等功能  
- **命令解析**：使用更健壮的指令解析或前后端通信协议，而不仅仅是简单的 `split()`  
- **多房间 / 多频道**：除了世界频道，还可创建多个“房间”或“主题频道”  
- **文件传输 / 图片表情**：增加更丰富的消息类型  
- **GUI 客户端**：使用 `tkinter`、`PyQt` 或 `Electron` 等技术打造图形界面  
- **性能优化**：在高并发下可使用异步框架（如 `asyncio`）或更高效的网络库  

---
