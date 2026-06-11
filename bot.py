

import os, re, json, time, asyncio, random, requests
from uuid import uuid4
from telethon import TelegramClient, events, functions, types
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import DeleteHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest

# ── Optional deps ─────────────────────────────────────────────────────────────
try:
    import aiohttp
    AIOHTTP_OK = True
except ImportError:
    AIOHTTP_OK = False

try:
    import sympy
    SYMPY_OK = True
except ImportError:
    SYMPY_OK = False

try:
    import instaloader
    INSTA_OK = True
except ImportError:
    INSTA_OK = False

# ── Credentials ───────────────────────────────────────────────────────────────
API_ID   = int(os.environ.get("API_ID",   "38165687"))
API_HASH = os.environ.get("API_HASH",     "1d6adcf8aed67d7f981d8e6089030158")
PHONE    = os.environ.get("PHONE",        "+919797590308")
OWNER_ID = 8192070400
SESSION  = "selfbot_radhey"

# ── Persistent data ───────────────────────────────────────────────────────────
DATA_FILE = "selfbot_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"muted_users": [], "banned_users": []}

def save_data(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f)

data         = load_data()
muted_users  = set(data.get("muted_users", []))
banned_users = set(data.get("banned_users", []))

# ── Runtime state ─────────────────────────────────────────────────────────────
auto_reply_data    = {"status": False, "message": ""}
auto_accept_active = False

# ── Client ────────────────────────────────────────────────────────────────────
client = TelegramClient(SESSION, API_ID, API_HASH)

# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════

async def get_entity(val):
    try:
        if isinstance(val, int): return await client.get_entity(val)
        if val.startswith("@"):  return await client.get_entity(val)
        try: return await client.get_entity(int(val))
        except Exception: return await client.get_entity(val)
    except Exception:
        return None

async def get_admin_group_ids():
    """Only groups/channels where we are admin — safe for broadcast."""
    ids = []
    async for d in client.iter_dialogs():
        if d.is_group or d.is_channel:
            try:
                perms = d.entity
                # Check admin rights via participants_count trick / rights attr
                if hasattr(perms, 'admin_rights') and perms.admin_rights:
                    ids.append(d.id)
                    continue
                # For megagroups / channels, fetch full info
                if hasattr(perms, 'megagroup') or hasattr(perms, 'broadcast'):
                    full = await client(GetFullChannelRequest(d.id))
                    chat = full.chats[0]
                    if getattr(chat, 'admin_rights', None):
                        ids.append(d.id)
            except Exception:
                pass
    return ids

async def get_all_group_ids():
    """All groups/channels (for .gc)."""
    ids = []
    async for d in client.iter_dialogs():
        if d.is_group or d.is_channel:
            ids.append(d.id)
    return ids

async def get_dm_ids():
    ids = []
    async for d in client.iter_dialogs():
        try:
            if d.is_user and not d.entity.bot:
                ids.append(d.id)
        except Exception:
            pass
    return ids

# ── Safe flood delay — randomised to avoid Telegram ban ──────────────────────
async def safe_sleep(count):
    """Randomised delay: 5–10s normally, 40s break every 15 messages."""
    if count > 0 and count % 15 == 0:
        await asyncio.sleep(40)
    else:
        await asyncio.sleep(random.uniform(5, 10))

# ── Instagram info ────────────────────────────────────────────────────────────
def _ig_info(username: str) -> str:
    username = username.lstrip("@").strip()

    # Method 1 — instaloader (most complete)
    if INSTA_OK:
        try:
            L = instaloader.Instaloader()
            p = instaloader.Profile.from_username(L.context, username)
            return (
                f"📸 **Instagram — @{p.username}**\n\n"
                f"✓ **Name:** `{p.full_name or 'N/A'}`\n"
                f"✓ **Username:** @{p.username}\n"
                f"✓ **Followers:** `{p.followers:,}`\n"
                f"✓ **Following:** `{p.followees:,}`\n"
                f"✓ **Posts:** `{p.mediacount:,}`\n"
                f"✓ **Private:** `{'Yes' if p.is_private else 'No'}`\n"
                f"✓ **Verified:** `{'Yes' if p.is_verified else 'No'}`\n"
                f"✓ **Business:** `{'Yes' if p.is_business_account else 'No'}`\n"
                f"✓ **Bio:** `{p.biography or 'None'}`\n"
                f"✓ **Link:** https://instagram.com/{p.username}"
            )
        except Exception:
            pass  # fall through to web API

    # Method 2 — Instagram web API scrape
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Mobile Safari/537.36"
            ),
            "x-ig-app-id": "936619743392459",
            "x-requested-with": "XMLHttpRequest",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "*/*",
            "Referer": f"https://www.instagram.com/{username}/",
        }
        r = requests.get(
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}",
            headers=headers, timeout=15
        )
        if r.status_code == 200:
            u = r.json()["data"]["user"]
            return (
                f"📸 **Instagram — @{u['username']}**\n\n"
                f"✓ **Name:** `{u.get('full_name') or 'N/A'}`\n"
                f"✓ **IG ID:** `{u['id']}`\n"
                f"✓ **Followers:** `{u['edge_followed_by']['count']:,}`\n"
                f"✓ **Following:** `{u['edge_follow']['count']:,}`\n"
                f"✓ **Posts:** `{u['edge_owner_to_timeline_media']['count']:,}`\n"
                f"✓ **Private:** `{'Yes' if u['is_private'] else 'No'}`\n"
                f"✓ **Verified:** `{'Yes' if u['is_verified'] else 'No'}`\n"
                f"✓ **Business:** `{'Yes' if u.get('is_business_account') else 'No'}`\n"
                f"✓ **Bio:** `{u.get('biography') or 'None'}`\n"
                f"✓ **External URL:** `{u.get('external_url') or 'None'}`\n"
                f"✓ **Link:** https://instagram.com/{u['username']}"
            )
        if r.status_code == 404:
            return f"❌ @{username} doesn't exist or is banned."
        if r.status_code == 401:
            return f"❌ Instagram blocked the request (rate limited). Try again in a few minutes."
        return f"❌ Instagram API returned status {r.status_code}."
    except requests.exceptions.Timeout:
        return "❌ Request timed out. Instagram may be slow, try again."
    except Exception as e:
        return f"❌ Failed to fetch info: {e}"

# ── Instagram password reset ──────────────────────────────────────────────────
def _ig_reset(username: str) -> str:
    username = username.lstrip("@").strip()
    # Strip email domain if user passed full email
    clean = username.split("@")[0] if "@" in username else username

    session = requests.Session()
    csrf = ""

    # Step 1 — get CSRF token
    try:
        init = session.get(
            "https://www.instagram.com/accounts/password/reset/",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=12
        )
        csrf = init.cookies.get("csrftoken", "")
        if not csrf:
            m = re.search(r'"csrf_token"\s*:\s*"([^"]+)"', init.text)
            csrf = m.group(1) if m else ""
    except Exception as e:
        return f"❌ Could not reach Instagram: {e}"

    if not csrf:
        return "❌ Could not get CSRF token from Instagram. They may be blocking requests."

    # Step 2 — web reset endpoint
    try:
        resp = session.post(
            "https://www.instagram.com/accounts/account_recovery_send_ajax/",
            headers={
                "User-Agent"       : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                     "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
                "Referer"          : "https://www.instagram.com/accounts/password/reset/",
                "X-CSRFToken"      : csrf,
                "X-Requested-With" : "XMLHttpRequest",
                "Content-Type"     : "application/x-www-form-urlencoded",
                "Origin"           : "https://www.instagram.com",
                "Accept-Language"  : "en-US,en;q=0.9",
            },
            data={
                "email_or_username"       : username,
                "recaptcha_challenge_field": "",
                "flow"                    : "fxcal",
            },
            timeout=12
        )
        if resp.status_code == 200:
            d = resp.json()
            if d.get("status") == "ok":
                return f"✅ Reset email/SMS sent for `{username}`!"
    except Exception:
        pass  # fall through to mobile API

    # Step 3 — get IG user ID for mobile API
    try:
        uid_resp = requests.get(
            f"https://www.instagram.com/api/v1/users/web_profile_info/?username={clean}",
            headers={
                "x-ig-app-id"     : "936619743392459",
                "x-requested-with": "XMLHttpRequest",
                "User-Agent"      : "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
                                    "AppleWebKit/537.36 Chrome/124.0.0.0 Mobile Safari/537.36",
                "Referer"         : f"https://www.instagram.com/{clean}/",
            },
            timeout=12
        ).json()
        uid = uid_resp["data"]["user"]["id"]
    except Exception:
        return (
            f"❌ Couldn't find IG user `@{clean}`.\n"
            "Make sure the username is correct and the account is public."
        )

    # Step 4 — mobile API reset
    try:
        mob = requests.post(
            "https://i.instagram.com/api/v1/accounts/send_password_reset/",
            headers={
                "User-Agent"     : "Instagram 275.0.0.27.98 Android (30/11; 420dpi; 1080x2400; samsung; SM-G991B; o1s; exynos2100; en_US; 458229258)",
                "Accept-Encoding": "gzip",
                "Cookie"         : f"csrftoken={csrf}",
                "X-CSRFToken"    : csrf,
                "Accept-Language": "en-US",
            },
            data={"user_id": uid, "device_id": str(uuid4())},
            timeout=12
        ).json()
        obf = mob.get("obfuscated_email") or mob.get("obfuscated_phone")
        if obf:
            return f"✅ Reset link sent to `{obf}` for @{clean}"
        status = mob.get("message") or mob.get("status") or str(mob)
        return f"⚠️ Request sent for @{clean} but got: `{status}`"
    except Exception as e:
        return f"❌ Mobile API failed: {e}"

# ── Translate via MyMemory (no key needed) ────────────────────────────────────
def _translate(text: str, target_lang: str) -> str:
    try:
        r = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text, "langpair": f"auto|{target_lang}"},
            timeout=10
        )
        data = r.json()
        if data.get("responseStatus") == 200:
            translated = data["responseData"]["translatedText"]
            return f"🌐 **[{target_lang.upper()}]** {translated}"
        return f"❌ Translation failed: {data.get('responseDetails', 'unknown error')}"
    except Exception as e:
        return f"❌ Translation error: {e}"

# ═════════════════════════════════════════════════════════════════════════════
# OUTGOING COMMANDS
# ═════════════════════════════════════════════════════════════════════════════

@client.on(events.NewMessage(outgoing=True))
async def cmd_handler(event):
    global muted_users, banned_users, auto_reply_data, auto_accept_active

    raw  = event.raw_text.strip()
    text = raw.lower()

    if not text.startswith("."):
        return

    # ── .ping ─────────────────────────────────────────────────────────────────
    if text == ".ping":
        t0  = time.time()
        msg = await event.edit("🏓 Pong!")
        ms  = round((time.time() - t0) * 1000, 2)
        await msg.edit(f"🏓 Pong! `{ms}ms`")

    # ── .help / .cmd ──────────────────────────────────────────────────────────
    elif text in (".help", ".cmd"):
        await event.edit(
            "🗿 [**𝗦𝗘𝗟𝗙𝗕𝗢𝗧 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦**](https://t.me/sayradhey)\n\n"

            "**⚡ Basic**\n"
            "`.ping` — latency check\n"
            "`.autoreply [msg]` — set auto-reply message\n"
            "`.autoreply off` — disable auto-reply\n"
            "`.autoaccept` — toggle auto-accept chat requests\n\n"

            "**👤 User Management**\n"
            "`.mute` / `.unmute` — mute/unmute (reply or @user)\n"
            "`.ban` / `.unban` — ban/unban user (auto-delete msgs)\n"
            "`.block` / `.unblock` — block/unblock user\n"
            "`.kick` (reply) — kick from group\n\n"

            "**📢 Broadcast** _(use in groups where you're admin)_\n"
            "`.dmfrwd` (reply) — forward to ALL DMs\n"
            "`.gc` (reply) — forward to ALL groups (admin-only)\n"
            "`.broad` (reply) — send text to ALL users\n"
            "`.frwdall` (reply) — forward DMs + admin groups\n"
            "`.dm @user msg` — send single DM\n\n"

            "**📋 Info**\n"
            "`.tinfo` (reply/@user) — full Telegram user info\n"
            "`.show` (reply) — quick user info\n"
            "`.owner` — show owner info\n"
            "`.chatinfo` — current chat/group info\n"
            "`.id` (reply/alone) — get user or chat ID\n\n"

            "**📸 Instagram**\n"
            "`.insta @user` — Instagram profile info\n"
            "`.rst @user` — send IG password reset\n\n"

            "**🔧 Utility**\n"
            "`.calc expr` — calculator (e.g. `.calc 2+2`)\n"
            "`.count N` — countdown timer (1–300s)\n"
            "`.spam N msg` — spam message N times (max 50)\n"
            "`.del` — clear private chat history\n"
            "`.purge N` — delete last N messages\n"
            "`.close N` — leave/delete group after N sec\n"
            "`.tr lang text` — translate (e.g. `.tr hi hello`)\n"
            "`.mm` (reply) — open #𝗥𝗔𝗗𝗛𝗘𝗬'S MIDDLEMAN SERVICE group\n"
            "`.tag` — tag all members in a group\n\n"

            "**🎭 Fun**\n"
            "`.mrityu` — owner intro\n"
            "`.say text` — echo text (then deletes command)\n"
            "`.reverse text` — reverse a string\n"
            "`.upper text` / `.lower text` — change case\n\n"

            "[𝗝𝗢𝗜𝗡](https://t.me/sayradhey) | by #𝗥𝗔𝗗𝗛𝗘𝗬"
        )

    # ── .mrityu ───────────────────────────────────────────────────────────────
    elif text == ".mrityu":
        lines = [
            "🗿 **[𝗢𝘄𝗻𝗲𝗿 𝗜𝗻𝘁𝗿𝗼](tg://openmessage?user_id=8192070400)**",
            "• Username: [@sayradhey](https://t.me/sayradhey)",
            "• Multi-talented | Full-Time Bakchod",
            "• Bot crafted with 💙 by #𝗥𝗔𝗗𝗛𝗘𝗬",
            "**Catch Me:** [𝗧𝗘𝗟𝗘𝗚𝗥𝗔𝗠](https://t.me/sayradhey)",
        ]
        msg = await event.edit("Typing...")
        out = ""
        for line in lines:
            out += line + "\n"
            await msg.edit(out)
            await asyncio.sleep(0.8)

    # ── .autoreply ────────────────────────────────────────────────────────────
    elif text.startswith(".autoreply"):
        if text == ".autoreply off":
            auto_reply_data = {"status": False, "message": ""}
            await event.edit("🔕 Auto-reply disabled.")
        else:
            msg = raw[11:].strip() if len(raw) > 10 else "I'm busy, will reply later."
            auto_reply_data = {"status": True, "message": msg}
            await event.edit(f"✅ Auto-reply set: `{msg}`")

    # ── .autoaccept ───────────────────────────────────────────────────────────
    elif text == ".autoaccept":
        auto_accept_active = not auto_accept_active
        state = "enabled ✅" if auto_accept_active else "disabled 🔕"
        await event.edit(f"Auto-accept chat requests {state}")

    # ── .owner ────────────────────────────────────────────────────────────────
    elif text.startswith(".owner"):
        me = await client.get_me()
        await event.edit(
            f"**Owner ✨**\n"
            f"**By:** [#𝗥𝗔𝗗𝗛𝗘𝗬](https://t.me/sayradhey)\n"
            f"**ID:** `{me.id}`\n"
            f"**Username:** @{me.username or 'N/A'}"
        )

    # ── .tinfo ────────────────────────────────────────────────────────────────
    elif text.startswith(".tinfo"):
        target = raw[7:].strip() if len(raw) > 6 else None
        try:
            if target:
                uf = await client(GetFullUserRequest(target))
            elif event.is_reply:
                reply = await event.get_reply_message()
                uf    = await client(GetFullUserRequest(reply.sender_id))
            else:
                await event.edit("❌ Reply to a user or: `.tinfo @username`")
                return
            u = uf.users[0] if hasattr(uf, "users") else uf.user
            dc_map = {1:"DC1 Miami",2:"DC2 Amsterdam",3:"DC3 Miami",4:"DC4 Amsterdam",5:"DC5 Singapore"}
            dc = dc_map.get(getattr(u, 'dc_id', 0), f"DC{getattr(u,'dc_id','?')}")
            await event.edit(
                f"**👤 Telegram Info**\n\n"
                f"✓ **Name:** `{(u.first_name or '')} {(u.last_name or '')}`.strip()\n"
                f"✓ **First Name:** `{u.first_name or 'N/A'}`\n"
                f"✓ **Last Name:** `{u.last_name or 'N/A'}`\n"
                f"✓ **Username:** @{u.username or 'N/A'}\n"
                f"✓ **User ID:** `{u.id}`\n"
                f"✓ **Phone:** `{u.phone or 'N/A'}`\n"
                f"✓ **Bot:** `{'Yes' if u.bot else 'No'}`\n"
                f"✓ **Verified:** `{'Yes' if getattr(u,'verified',False) else 'No'}`\n"
                f"✓ **Premium:** `{'Yes' if getattr(u,'premium',False) else 'No'}`\n"
                f"✓ **DC:** `{dc}`\n"
                f"✓ **Last Seen:** `{u.status.__class__.__name__ if u.status else 'Hidden'}`"
            )
        except Exception as e:
            await event.edit(f"❌ Error: {e}")

    # ── .show ─────────────────────────────────────────────────────────────────
    elif text.startswith(".show"):
        if not event.is_reply:
            await event.edit("❌ Reply to a user.")
            return
        reply = await event.get_reply_message()
        u     = await client.get_entity(reply.sender_id)
        uname = f"@{u.username}" if u.username else "N/A"
        await event.edit(
            f"**👤 User Info**\n"
            f"**Name:** `{u.first_name or 'N/A'} {u.last_name or ''}`\n"
            f"**ID:** `{u.id}`\n"
            f"**Username:** {uname}\n"
            f"**Bot:** `{'Yes' if u.bot else 'No'}`"
        )

    # ── .id ───────────────────────────────────────────────────────────────────
    elif text == ".id":
        if event.is_reply:
            reply = await event.get_reply_message()
            u     = await client.get_entity(reply.sender_id)
            await event.edit(f"🆔 **User ID:** `{u.id}`")
        else:
            await event.edit(f"🆔 **Chat ID:** `{event.chat_id}`")

    # ── .chatinfo ─────────────────────────────────────────────────────────────
    elif text.startswith(".chatinfo"):
        try:
            chat = await event.get_chat()
            if hasattr(chat, 'title'):
                members = getattr(chat, 'participants_count', 'N/A')
                ctype = "Channel" if getattr(chat,'broadcast',False) else "Group/Supergroup"
                await event.edit(
                    f"**💬 Chat Info**\n\n"
                    f"✓ **Title:** `{chat.title}`\n"
                    f"✓ **ID:** `{chat.id}`\n"
                    f"✓ **Type:** `{ctype}`\n"
                    f"✓ **Username:** @{getattr(chat,'username','N/A') or 'N/A'}\n"
                    f"✓ **Members:** `{members}`\n"
                    f"✓ **Verified:** `{'Yes' if getattr(chat,'verified',False) else 'No'}`"
                )
            else:
                me = await client.get_me()
                await event.edit(
                    f"**💬 Chat Info**\n\n"
                    f"✓ **Type:** `Private Chat`\n"
                    f"✓ **Your ID:** `{me.id}`\n"
                    f"✓ **Chat ID:** `{event.chat_id}`"
                )
        except Exception as e:
            await event.edit(f"❌ {e}")

    # ── .insta / .iginfo ──────────────────────────────────────────────────────
    elif text.startswith(".insta") or text.startswith(".iginfo"):
        parts = raw.split(None, 1)
        if len(parts) < 2:
            await event.edit("❌ Usage: `.insta @username`")
            return
        uname = parts[1].strip().lstrip("@")
        await event.edit(f"🔍 Fetching Instagram info for **@{uname}**...")
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _ig_info, uname)
        await event.edit(result)

    # ── .rst / .reset (Instagram password reset) ──────────────────────────────
    elif text.startswith(".rst") or text.startswith(".reset"):
        parts = raw.split(None, 1)
        if len(parts) < 2:
            await event.edit("❌ Usage: `.rst @username` or `.rst username`")
            return
        uname = parts[1].strip()
        await event.edit(f"🔄 Sending IG password reset for `{uname}`...")
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _ig_reset, uname)
        await event.edit(result)

    # ── .mute ─────────────────────────────────────────────────────────────────
    elif text.startswith(".mute") and not text.startswith(".unmute"):
        u = None
        if event.is_reply:
            reply = await event.get_reply_message()
            u     = await client.get_entity(reply.sender_id)
        else:
            parts = raw.split(None, 1)
            if len(parts) > 1:
                u = await get_entity(parts[1].strip())
        if not u:
            await event.edit("❌ User not found. Reply to a user or provide @username.")
            return
        muted_users.add(u.id)
        data["muted_users"] = list(muted_users)
        save_data(data)
        await event.edit(f"🔕 Muted `{u.first_name or u.id}` — their messages will be deleted.")

    # ── .unmute ───────────────────────────────────────────────────────────────
    elif text.startswith(".unmute"):
        u = None
        if event.is_reply:
            reply = await event.get_reply_message()
            u     = await client.get_entity(reply.sender_id)
        else:
            parts = raw.split(None, 1)
            if len(parts) > 1:
                u = await get_entity(parts[1].strip())
        if not u:
            await event.edit("❌ User not found.")
            return
        muted_users.discard(u.id)
        data["muted_users"] = list(muted_users)
        save_data(data)
        await event.edit(f"🗣️ Unmuted `{u.first_name or u.id}`")

    # ── .ban ──────────────────────────────────────────────────────────────────
    elif text.startswith(".ban") and not text.startswith(".unban"):
        u = None
        if event.is_reply:
            reply = await event.get_reply_message()
            u     = await client.get_entity(reply.sender_id)
        else:
            parts = raw.split(None, 1)
            if len(parts) > 1:
                u = await get_entity(parts[1].strip())
        if not u:
            await event.edit("❌ User not found.")
            return
        banned_users.add(u.id)
        data["banned_users"] = list(banned_users)
        save_data(data)
        await event.edit(f"🚫 Banned `{u.first_name or u.id}` — their messages will be deleted.")

    # ── .unban ────────────────────────────────────────────────────────────────
    elif text.startswith(".unban"):
        u = None
        if event.is_reply:
            reply = await event.get_reply_message()
            u     = await client.get_entity(reply.sender_id)
        else:
            parts = raw.split(None, 1)
            if len(parts) > 1:
                u = await get_entity(parts[1].strip())
        if not u:
            await event.edit("❌ User not found.")
            return
        banned_users.discard(u.id)
        data["banned_users"] = list(banned_users)
        save_data(data)
        await event.edit(f"✅ Unbanned `{u.first_name or u.id}`")

    # ── .block ────────────────────────────────────────────────────────────────
    elif text.startswith(".block") and not text.startswith(".unblock"):
        target_id = None
        if event.is_private:
            target_id = event.chat_id
        else:
            parts = raw.split(None, 1)
            if len(parts) > 1:
                u = await get_entity(parts[1].strip())
                if u: target_id = u.id
        if target_id:
            await client(functions.contacts.BlockRequest(id=target_id))
            await event.edit(f"🚫 Blocked `{target_id}`")
        else:
            await event.edit("❌ Use in a private chat, or: `.block @username`")

    # ── .unblock ──────────────────────────────────────────────────────────────
    elif text.startswith(".unblock"):
        target_id = None
        if event.is_private:
            target_id = event.chat_id
        else:
            parts = raw.split(None, 1)
            if len(parts) > 1:
                u = await get_entity(parts[1].strip())
                if u: target_id = u.id
        if target_id:
            await client(functions.contacts.UnblockRequest(id=target_id))
            await event.edit(f"✅ Unblocked `{target_id}`")
        else:
            await event.edit("❌ Use in a private chat, or: `.unblock @username`")

    # ── .kick ─────────────────────────────────────────────────────────────────
    elif text.startswith(".kick"):
        if not event.is_group:
            await event.edit("❌ Groups only.")
            return
        if not event.is_reply:
            await event.edit("❌ Reply to the user you want to kick.")
            return
        reply = await event.get_reply_message()
        u     = await client.get_entity(reply.sender_id)
        try:
            await client.kick_participant(event.chat_id, u.id)
            await event.edit(f"🦵 Kicked `{u.first_name or u.id}`")
        except Exception as e:
            await event.edit(f"❌ {e}")

    # ── .dm ───────────────────────────────────────────────────────────────────
    elif text.startswith(".dm") and not text.startswith(".dmfrwd"):
        content = raw[3:].strip()
        if event.is_reply:
            reply = await event.get_reply_message()
            if content:
                await client.send_message(reply.sender_id, content)
                await event.edit("✅ DM sent.")
            else:
                await event.edit("❌ Provide a message: `.dm message`")
        else:
            parts = content.split(None, 1)
            if len(parts) < 2 or not parts[0].startswith("@"):
                await event.edit("❌ Usage: `.dm @username message`")
                return
            u = await get_entity(parts[0])
            if u:
                await client.send_message(u.id, parts[1])
                await event.edit(f"✅ DM sent to @{u.username or u.id}")
            else:
                await event.edit("❌ User not found.")

    # ── .dmfrwd — forward to ALL DMs with safe anti-ban delay ─────────────────
    elif text.startswith(".dmfrwd"):
        if not event.is_reply:
            await event.edit("⚠️ Reply to the message you want to forward.")
            return
        replied  = await event.get_reply_message()
        dm_ids   = await get_dm_ids()
        total    = len(dm_ids)
        await event.edit(f"📨 Forwarding to {total} DMs... (anti-ban mode, be patient)")
        sent, failed = 0, 0
        for uid in dm_ids:
            try:
                await client.forward_messages(uid, replied)
                sent += 1
            except Exception:
                failed += 1
            await safe_sleep(sent)
        await event.edit(f"✅ Forwarded to **{sent}** DMs. Failed: {failed}")

    # ── .gc — forward to groups where you are ADMIN ───────────────────────────
    elif text.startswith(".gc"):
        if not event.is_reply:
            await event.edit("⚠️ Reply to the message you want to broadcast.")
            return
        replied   = await event.get_reply_message()
        await event.edit("🔍 Finding groups where you're admin...")
        group_ids = await get_admin_group_ids()
        if not group_ids:
            # fallback: just use all groups if admin detection fails
            group_ids = await get_all_group_ids()
        total = len(group_ids)
        await event.edit(f"📢 Broadcasting to {total} groups (admin mode, anti-ban)...")
        sent, failed = 0, 0
        for gid in group_ids:
            try:
                await client.forward_messages(gid, replied)
                sent += 1
            except Exception:
                failed += 1
            await safe_sleep(sent)
        await event.edit(f"✅ Broadcasted to **{sent}** groups. Failed: {failed}")

    # ── .broad — send text to ALL users ───────────────────────────────────────
    elif text.startswith(".broad"):
        if not event.is_reply:
            await event.edit("⚠️ Reply to the message you want to broadcast.")
            return
        replied = await event.get_reply_message()
        dm_ids  = await get_dm_ids()
        total   = len(dm_ids)
        await event.edit(f"📣 Broadcasting to {total} users... (anti-ban mode)")
        sent, failed = 0, 0
        for uid in dm_ids:
            try:
                await client.send_message(uid, replied.text or "")
                sent += 1
            except Exception:
                failed += 1
            await safe_sleep(sent)
        await event.edit(f"✅ Broadcasted to **{sent}** users. Failed: {failed}")

    # ── .frwdall — forward DMs + admin groups ─────────────────────────────────
    elif text.startswith(".frwdall"):
        if not event.is_reply:
            await event.edit("⚠️ Reply to the message you want to forward.")
            return
        replied   = await event.get_reply_message()
        await event.edit("🔍 Collecting targets...")
        dm_ids    = await get_dm_ids()
        group_ids = await get_admin_group_ids()
        all_ids   = dm_ids + group_ids
        total     = len(all_ids)
        await event.edit(f"🚀 Forwarding to {total} targets (anti-ban mode, takes time)...")
        sent, failed = 0, 0
        for target_id in all_ids:
            try:
                await client.forward_messages(target_id, replied)
                sent += 1
            except Exception:
                failed += 1
            await safe_sleep(sent)
        await event.edit(f"✅ Done! Forwarded to **{sent}** targets. Failed: {failed}")

    # ── .mm — #𝗥𝗔𝗗𝗛𝗘𝗬'S MIDDLEMAN SERVICE ────────────────────────────────────
    elif text.startswith(".mm"):
        if not event.is_reply:
            await event.edit("❌ Reply to a user with `.mm`")
            return
        reply = await event.get_reply_message()
        u     = await client.get_entity(reply.sender_id)
        try:
            await client(functions.messages.CreateChatRequest(
                users=[u.id],
                title="#𝗥𝗔𝗗𝗛𝗘𝗬'S MIDDLEMAN SERVICE"
            ))
            await event.edit(
                f"✅ **#𝗥𝗔𝗗𝗛𝗘𝗬'S MIDDLEMAN SERVICE**\n"
                f"Group created with `{u.first_name or u.id}`"
            )
        except Exception as e:
            await event.edit(f"❌ {e}")

    # ── .tag — tag all members in current group ───────────────────────────────
    elif text.startswith(".tag"):
        if not event.is_group:
            await event.edit("❌ Groups only.")
            return
        custom_msg = raw[4:].strip() or "👋"
        await event.edit("🔍 Collecting members...")
        try:
            participants = await client.get_participants(event.chat_id, limit=50)
            tags = " ".join(
                [f"[{p.first_name or 'user'}](tg://user?id={p.id})"
                 for p in participants if not p.bot and p.id != (await client.get_me()).id]
            )
            if tags:
                await client.send_message(event.chat_id, f"{custom_msg}\n{tags}")
                await event.delete()
            else:
                await event.edit("❌ No members found.")
        except Exception as e:
            await event.edit(f"❌ {e}")

    # ── .del ──────────────────────────────────────────────────────────────────
    elif text == ".del":
        if not event.is_private:
            await event.edit("❌ Private chats only.")
            return
        try:
            await client(DeleteHistoryRequest(peer=event.chat_id, max_id=0, revoke=True))
            msg = await event.respond("🧹 Chat history cleared.")
            await asyncio.sleep(3)
            await msg.delete()
        except Exception as e:
            await event.respond(f"❌ {e}")

    # ── .purge ────────────────────────────────────────────────────────────────
    elif text.startswith(".purge"):
        parts = raw.split(None, 1)
        try:
            n = int(parts[1])
        except Exception:
            await event.edit("❌ Usage: `.purge N`")
            return
        msgs = await client.get_messages(event.chat_id, limit=n + 1)
        ids  = [m.id for m in msgs]
        try:
            await client.delete_messages(event.chat_id, ids)
            conf = await event.respond(f"✅ Purged {n} messages.")
            await asyncio.sleep(3)
            await conf.delete()
        except Exception as e:
            await event.respond(f"❌ {e}")

    # ── .close ────────────────────────────────────────────────────────────────
    elif text.startswith(".close"):
        if not event.is_group:
            await event.edit("❌ Groups only.")
            return
        parts = raw.split(None, 1)
        try:
            sec = int(parts[1])
        except Exception:
            await event.edit("❌ Usage: `.close N`")
            return
        await event.edit(f"💣 Leaving group in {sec} seconds.")
        await asyncio.sleep(sec)
        try:
            await client.delete_dialog(event.chat_id)
        except Exception as e:
            await event.respond(f"❌ {e}")

    # ── .spam ─────────────────────────────────────────────────────────────────
    elif text.startswith(".spam"):
        parts = raw.split(None, 2)
        if len(parts) < 3 or not parts[1].isdigit():
            await event.edit("❌ Usage: `.spam N message`")
            return
        n   = int(parts[1])
        msg = parts[2]
        if n > 50:
            await event.edit("❌ Max 50 messages.")
            return
        await event.delete()
        for _ in range(n):
            await client.send_message(event.chat_id, msg)
            await asyncio.sleep(0.8)

    # ── .count ────────────────────────────────────────────────────────────────
    elif text.startswith(".count"):
        parts = raw.split(None, 1)
        try:
            sec = int(parts[1])
            assert 1 <= sec <= 300
        except Exception:
            await event.edit("❌ Usage: `.count N` (1–300)")
            return
        m = await event.edit(f"⏳ `{sec}`s")
        for i in range(sec - 1, -1, -1):
            await asyncio.sleep(1)
            try: await m.edit(f"⏳ `{i}`s")
            except Exception: pass
        try: await m.delete()
        except Exception: pass

    # ── .calc ─────────────────────────────────────────────────────────────────
    elif text.startswith(".calc"):
        expr = raw[6:].strip()
        if not expr:
            await event.edit("❌ Usage: `.calc 2+2` or `.calc sqrt(144)`")
            return
        try:
            if SYMPY_OK:
                result = sympy.sympify(expr)
            else:
                result = eval(expr, {"__builtins__": {}}, {})
            await event.edit(f"🧮 `{expr}` = `{result}`")
        except Exception:
            await event.edit("❌ Invalid expression.")

    # ── .tr / .translate ──────────────────────────────────────────────────────
    elif text.startswith(".tr") or text.startswith(".translate"):
        # Usage: .tr hi Hello world  OR  .tr en (reply)
        cmd_end = 3 if text.startswith(".tr") else 10
        rest    = raw[cmd_end:].strip()

        if not rest and event.is_reply:
            await event.edit("❌ Provide target language: `.tr hi` (while replying)")
            return

        parts = rest.split(None, 1)
        if len(parts) < 1:
            await event.edit("❌ Usage: `.tr hi text` or reply + `.tr hi`")
            return

        lang = parts[0].lower()

        if len(parts) >= 2:
            content = parts[1]
        elif event.is_reply:
            reply   = await event.get_reply_message()
            content = reply.text or ""
        else:
            await event.edit("❌ Provide text or reply to a message. Usage: `.tr hi Hello`")
            return

        if not content.strip():
            await event.edit("❌ No text to translate.")
            return

        await event.edit("🌐 Translating...")
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _translate, content, lang)
        await event.edit(result)

    # ── .say ──────────────────────────────────────────────────────────────────
    elif text.startswith(".say"):
        content = raw[4:].strip()
        if not content:
            await event.edit("❌ Usage: `.say hello world`")
            return
        await event.delete()
        await client.send_message(event.chat_id, content)

    # ── .reverse ──────────────────────────────────────────────────────────────
    elif text.startswith(".reverse"):
        content = raw[8:].strip()
        if not content and event.is_reply:
            reply   = await event.get_reply_message()
            content = reply.text or ""
        if not content:
            await event.edit("❌ Usage: `.reverse text`")
            return
        await event.edit(f"🔁 `{content[::-1]}`")

    # ── .upper ────────────────────────────────────────────────────────────────
    elif text.startswith(".upper"):
        content = raw[6:].strip()
        if not content and event.is_reply:
            reply   = await event.get_reply_message()
            content = reply.text or ""
        if not content:
            await event.edit("❌ Usage: `.upper text`")
            return
        await event.edit(content.upper())

    # ── .lower ────────────────────────────────────────────────────────────────
    elif text.startswith(".lower"):
        content = raw[6:].strip()
        if not content and event.is_reply:
            reply   = await event.get_reply_message()
            content = reply.text or ""
        if not content:
            await event.edit("❌ Usage: `.lower text`")
            return
        await event.edit(content.lower())


# ═════════════════════════════════════════════════════════════════════════════
# INCOMING HANDLER — mute / ban / auto-reply
# ═════════════════════════════════════════════════════════════════════════════

@client.on(events.NewMessage(incoming=True))
async def incoming_handler(event):
    global muted_users, banned_users, auto_reply_data

    me = await client.get_me()
    if event.sender_id == me.id:
        return

    if event.sender_id in banned_users:
        try: await event.delete()
        except Exception: pass
        return

    if event.sender_id in muted_users:
        try: await event.delete()
        except Exception: pass
        return

    if auto_reply_data["status"] and event.is_private:
        await event.reply(auto_reply_data["message"])


# ═════════════════════════════════════════════════════════════════════════════
# RENDER KEEP-ALIVE WEB SERVER
# ═════════════════════════════════════════════════════════════════════════════

async def web_server():
    if not AIOHTTP_OK:
        print("[WEB] aiohttp not installed — no health endpoint. Run: pip install aiohttp")
        return
    from aiohttp import web as aw
    app = aw.Application()
    app.router.add_get("/",       lambda r: aw.Response(text="✅ Selfbot @sayradhey running!"))
    app.router.add_get("/health", lambda r: aw.Response(text="OK"))
    runner = aw.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await aw.TCPSite(runner, "0.0.0.0", port).start()
    print(f"[WEB] Health server running on port {port}")


# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

async def main():
    await client.start(phone=PHONE)
    me = await client.get_me()
    print(f"\n✅  Logged in as: {me.first_name} (@{me.username}) | ID: {me.id}")
    print("📡  Selfbot by #𝗥𝗔𝗗𝗛𝗘𝗬 — @sayradhey  |  v5.0")
    print("💬  Type .help in Telegram for full command list\n")
    await web_server()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
