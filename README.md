

# OPEN SELFBOT — Advanced Telegram Selfbot

A feature-rich Telegram selfbot with powerful automation, user management, and utility tools.
Created by #RADHEY

---

⚡ Features

🔧 Basic Commands

· .ping – Response time checker
· .afk / .unafk – Away-from-keyboard status with auto-reply
· .autoreply – Custom auto-reply messages
· .autoaccept – Auto-accept chat requests

👥 User Management

· .mute / .unmute – Auto-delete messages from specific users
· .ban / .unban – Block message delivery entirely
· .kick – Remove users from groups (reply)
· .block / .unblock – Telegram block/unblock
· .dmute – Mute with notifications
· .show – Fetch detailed user info

👥 Group & Broadcast Tools

· .mm – Create private group with a user
· .gc – Broadcast a message to all groups you're in
· .broad – Broadcast to all private chats
· .dmfrwd – Forward a message to all DMs
· .dm – Send direct messages via command

📊 Information Gathering

· .tinfo – Get Telegram user details (ID, username, bot status)
· .cinfo – Fetch phone number info (powered by external API)
· .iginfo / .insta – Scrape Instagram profile data
· .rst – Trigger Instagram password reset for a user
· .owner – Show creator info

🧹 Chat Management

· .del – Clear entire private chat history
· .purge N – Delete last N messages
· .close N – Auto-delete a group after N seconds

😴 Status Modifiers

· .asleep / .awake – Add/remove "~ asleep" to first name
· .busy / .free – Add/remove "~ Busy" to first name

🛠 Utility Commands

· .calc – Solve math expressions (via SymPy)
· .count / .countdown – Timer with message on finish
· .spam – Send repeated messages (limit 50)
· .adopt – Fun "adopt a user" message
· .note / .notes / .getnote / .delnote – Persistent note-taking system
· .qr – Generate QR codes from text

📜 Help System

· .help – Display full command list

---

📦 Requirements

Automatically installs missing dependencies on first run:

· requests, colorama, PySocks, pyfiglet, pystyle, telethon, sympy, instaloader, aiohttp, qrcode, pillow

---

🚀 Setup

1. Get API credentials from my.telegram.org
2. Edit API_ID and API_HASH in the script
3. Run the script and authenticate when prompted

```bash
python open_selfbot.py
```

---

⚠️ Disclaimer

· This is a selfbot – it uses your user account, not a bot account.
· Selfbots violate Telegram's Terms of Service. Use at your own risk.
· The developer is not responsible for account bans or restrictions.

---

🙏 Credits

Created by: #RADHEY
Inspiration & contributions: Open-source community, Telethon library maintainers

---

📁 Data Storage

Persistent data (muted users, banned users, notes) saved in selfbot_data.json

---

🧠 Note

Some commands (like .kick, .gc, .broad) require the account to be an admin or have appropriate permissions.

---

Let me know if you'd like a shorter version or a README.md file format instead.
