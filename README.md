# CipherTalk

> A terminal-based, end-to-end encrypted chat and file-sharing application
> with support for private and group conversations via a lightweight local relay.

---

## Table of Contents

* Overview
* Features
* Requirements
* Installation
* Quickstart

  1. Launch & Set Nickname
  2. Main Menu Options
  3. Private Chat
  4. Group Chat
  5. Sending Files
* Data & Logs
* Directory Structure

---

## Overview

CipherTalk uses a simple local TCP relay (on port 9000) to deliver AES-GCM–encrypted messages and files between peers and groups. Users identify themselves with compact ID codes (Base58 strings bundling nickname, IP, port, and public key) for zero-configuration friend discovery.

---

## Features

• ID codes for frictionless friend discovery
• Private chats (text & `/send_file`)
• Group chats with per-group keys and auto-generated names
• Live online status (🟢/⚪) in your friend list
• Server panel showing active sessions & packet counts
• Quick-setup guide for IP discovery, port forwarding, and firewall

---

## Requirements

• Python 3.7+
• PyNaCl ≥ 1.4.0
• pycryptodome ≥ 3.9.0
• SQLAlchemy ≥ 1.3.0

Install with:

```
pip install -r requirements.txt
```

---

## Installation

1. Clone the repo
   git clone [https://github.com/your-org/ciphertalk.git](https://github.com/your-org/ciphertalk.git)
   cd ciphertalk

2. Install dependencies
   pip install -r requirements.txt

---

## Quickstart

### 1) Launch & Set Nickname

Run:

```
python run.py
```

You'll see something like:

```
[Device] Identity already initialized.  
🔑 Enter your nickname:  alice  
[ServerService] Listening on port 9000  
```

This starts your local relay on port 9000 and begins pinging friends every 30 seconds for online status.

---

### 2) Main Menu Options

After entering your nickname, you’ll see:

```
=== Main Menu ===  
1) Generate ID code  
2) Add friend  
3) Friend list  
4) Chats  
5) Create group chat  
6) Server panel  
7) Setup  
8) Exit  
Select [1–8]:
```

Option descriptions:

1. **Generate ID code**
   Produce your Base58 ID (nickname, IP, port, public key). Share it so friends can add you.

2. **Add friend**
   Paste a friend’s ID code to register them locally.

3. **Friend list**
   View all friends (sorted) with 🟢/⚪ online indicators.

4. **Chats**
   Choose a friend and enter a private chat loop.

5. **Create group chat**
   Pick multiple friends; auto-name group by joining nicknames; distribute per-group key.

6. **Server panel**
   Display your relay’s active sessions and packet counts.

7. **Setup**
   Show quick-start guide (IP lookup, port forwarding, firewall).

8. **Exit**
   Quit CipherTalk.

---

### 3) Private Chat

After choosing option 4, select a friend:

```
Your Friends:  
  🟢 bob @ 203.0.113.42:9000  
  ⚪ carol @ 198.51.100.17:9000  

Enter friend username (blank to cancel): bob  
```

In the chat loop you can:

• Type any message and press Enter
• Send a file with
/send\_file /full/path/to/file.ext
• Exit back to Main Menu with
/exit

All payloads are end-to-end encrypted and relayed via your local server.

---

### 4) Group Chat

1. Choose **5) Create group chat**
2. Enter a comma-separated list of friend usernames, e.g.
   alice,bob,charlie
3. CipherTalk will generate a random 256-bit group key, auto-name the group by joining member nicknames (e.g. alice\_bob\_charlie), and distribute the key securely to each member.

As the owner you’ll relay group messages/files to all members; as a participant you’ll receive and decrypt them.

---

### 5) Sending Files

• **Private Chat**: use `/send_file` inside the chat loop.
• **Group Chat**: after selecting your group chat in the group-chat loop, use the same `/send_file` syntax to share files.

---

## Data & Logs

• Media folder: `~/cipher_talk/media/` (incoming files)
• Logs folder: `~/.cipher_talk/logs/`
– `private/<friend>.log` (encrypted private history)
– `groups/<group_id>.log` (encrypted group history)

---

Happy chatting!
