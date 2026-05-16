_L="QR code generation requires 'qrcode' and 'pillow' libraries. Install with: pip install qrcode[pil]"
_K='selfbot_data.json'
_J='message'
_I='reason'
_H='notes'
_G='banned_users'
_F='since'
_E='muted_users'
_D=False
_C=True
_B='N/A'
_A='status'
print('\x1b[1;92m\x1b[38;5;50m OPEN SELFBOT BY #𝗥𝗔𝗗𝗛𝗘𝗬 \x1b[0m')
import os,sys,importlib,asyncio,re,json,time,random
from datetime import datetime
from uuid import uuid4
import requests,aiohttp,sympy,instaloader
from pyfiglet import figlet_format
from pystyle import Colors,Colorate
from telethon import TelegramClient,events,functions,types
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
required_packages=['requests','colorama','PySocks','pyfiglet','pystyle','telethon','sympy','instaloader','aiohttp','qrcode','pillow']
for pkg in required_packages:
	try:importlib.import_module(pkg)
	except ImportError:os.system(f"pip install {pkg}")
try:import qrcode;QRCODE_AVAILABLE=_C
except ImportError:QRCODE_AVAILABLE=_D
os.system('cls'if os.name=='nt'else'clear')
API_ID='ENTER_API_ID'
API_HASH='ENTER_HASH_API'
DEVELOPER='#RADHEY'
def load_data():
	try:
		with open(_K,'r')as A:return json.load(A)
	except(FileNotFoundError,json.JSONDecodeError):return{_E:[],_G:[],_H:{}}
def save_data(data):
	with open(_K,'w')as A:json.dump(data,A)
data=load_data()
muted_users=set(data.get(_E,[]))
banned_users=set(data.get(_G,[]))
notes=data.get(_H,{})
client=TelegramClient('selfbot',API_ID,API_HASH).start()
banner=figlet_format('SELFBOT',font='standard')
print(Colorate.Horizontal(Colors.green_to_blue,banner))
print(Colorate.Horizontal(Colors.red_to_yellow,f"Created by {DEVELOPER}\n"))
print(Colorate.Horizontal(Colors.blue_to_cyan,'Type .help for commands list\n'))
afk_data={_A:_D,_I:'',_F:0}
auto_reply_data={_A:_D,_J:''}
auto_accept_requests=_D
async def get_entity(user_or_id):
	A=user_or_id
	try:
		if isinstance(A,int):return await client.get_entity(A)
		if A.startswith('@'):return await client.get_entity(A)
		try:return await client.get_entity(int(A))
		except Exception:return await client.get_entity(A)
	except Exception:return
async def get_gc_ids():
	B=[]
	async for A in client.iter_dialogs():
		if A.is_group and not A.entity.bot:B.append(A.id)
	return B
async def get_all_user_ids():
	B=[]
	async for A in client.iter_dialogs():
		if A.is_user and not A.entity.bot:B.append(A.id)
	return B
def get_ig_info(username):
	try:B=instaloader.Instaloader();A=instaloader.Profile.from_username(B.context,username);C={'Username':A.username,'Name':A.full_name,'Bio':A.biography,'Followers':A.followers,'Following':A.followees,'Posts':A.mediacount,'Private':A.is_private,'Verified':A.is_verified,'Business':A.is_business_account,'Created Year':_B};return'\n'.join([f"{A}: {B}"for(A,B)in C.items()])
	except Exception as D:return f"Error: Could not get Instagram info. {str(D)}"
def send_instagram_reset(username):
	L='gzip';K='en-US,en;q=0.9';J='*/*';I='XMLHttpRequest';H='Accept-Language';G='User-Agent';B=username;D='yMUowsj3FvQttZHlOKhosY6h3wBcpyTW';M={G:'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36','Referer':'https://www.instagram.com/accounts/password/reset/','X-CSRFToken':D,'Content-Type':'application/x-www-form-urlencoded','X-Requested-With':I,'Accept':J,H:K};N='https://www.instagram.com/accounts/account_recovery_send_ajax/';O={'email_or_username':B,'recaptcha_challenge_field':''}
	try:
		E=requests.post(N,headers=M,data=O)
		if E.status_code!=200:return f"Failed initial request, status code {E.status_code}"
	except Exception as C:return f"Exception contacting Instagram: {C}"
	try:A=B.split('@gmail.com')[0]
	except Exception:A=B
	P=f"https://www.instagram.com/api/v1/users/web_profile_info/?username={A}";Q={'accept':J,'accept-encoding':L,'accept-language':K,'referer':f"https://www.instagram.com/{A}",'sec-fetch-dest':'empty','sec-fetch-mode':'cors','sec-fetch-site':'same-origin','x-ig-app-id':'936619743392459','x-ig-www-claim':'0','x-requested-with':I}
	try:R=requests.get(P,headers=Q).json();S=R['data']['user']['id']
	except Exception:return f"Failed to get Instagram user id for @{A}"
	T='https://i.instagram.com/api/v1/accounts/send_password_reset/';U={G:'Instagram 6.12.1 Android (30/11; 480dpi; 1080x2004; HONOR; ANY-LX2; HNANY-Q1; qcom; ar_EG_#u-nu-arab)',H:'ar-EG, en-US','X-IG-Connection-Type':'MOBILE(LTE)','X-IG-Capabilities':'AQ==','Accept-Encoding':L,'Cookie':f"mid=aIBuegABAAFd5CI1o2zCPTQJaoEt; csrftoken={D}",'Cookie2':'$Version=1'};V={'user_id':S,'device_id':str(uuid4())}
	try:
		W=requests.post(T,headers=U,data=V).json();F=W.get('obfuscated_email')
		if F:return f"Password reset link sent to @{A} at {F}"
		else:return f"Failed to send password reset to @{A}"
	except Exception as C:return f"Exception sending password reset: {C}"
async def get_phone_info(number):
	B=f"https://bot.toxictanji.com/kreji.php?num={number}"
	try:
		async with aiohttp.ClientSession()as C:
			async with C.get(B)as A:
				if A.status==200:D=await A.text();return D
				else:return f"API request failed with status {A.status}"
	except Exception as E:return f"Error fetching phone info: {E}"
async def generate_qr(text,filename='qrcode.png'):
	B=filename
	if not QRCODE_AVAILABLE:return _L
	try:A=qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_L,box_size=10,border=4);A.add_data(text);A.make(fit=_C);C=A.make_image(fill_color='black',back_color='white');C.save(B);return B
	except Exception as D:return f"Error generating QR code: {str(D)}"
@client.on(events.NewMessage(outgoing=_C))
async def cmd_handler(event):
	t=' ~ Busy';s='~ Busy';r=' ~ asleep';q='~ asleep';p='Invalid seconds!';o='.unmute';i='username';h=None;R='User not found.';G=' ';A=event;global muted_users,banned_users,notes,afk_data,auto_reply_data,auto_accept_requests;F=A.raw_text.strip();D=F.lower()
	if D=='.ping':u=time.time();O=await A.reply('Pong!');v=time.time();await O.edit(f"Pong! `{round((v-u)*1000,3)}ms`");await A.delete();return
	elif D.startswith('.afk'):j=F[5:]if len(F)>4 else'AFK';afk_data={_A:_C,_I:j,_F:time.time()};await A.reply(f"🟢 I'm now AFK: {j}");await A.delete();return
	elif D=='.unafk':
		if afk_data[_A]:w=time.time()-afk_data[_F];x,y=divmod(w,3600);z,L=divmod(y,60);A0=f"{int(x)}h {int(z)}m {int(L)}s";afk_data={_A:_D,_I:'',_F:0};await A.reply(f"🔴 No longer AFK. Was away for {A0}")
		else:await A.reply("I'm not AFK.")
		await A.delete();return
	elif D.startswith('.autoreply'):
		if D=='.autoreply off':auto_reply_data={_A:_D,_J:''};await A.reply('Auto-reply disabled')
		else:O=F[11:]if len(F)>10 else"I'm busy right now. I'll reply later.";auto_reply_data={_A:_C,_J:O};await A.reply(f"Auto-reply enabled: {O}")
		await A.delete();return
	elif D=='.autoaccept':auto_accept_requests=not auto_accept_requests;A1='enabled'if auto_accept_requests else'disabled';await A.reply(f"Auto-accept chat requests {A1}");await A.delete();return
	elif D.startswith('.dmute ')or D.startswith('.dmute')and A.is_reply:
		if A.is_reply:E=await A.get_reply_message();B=await client.get_entity(E.sender_id)
		else:H=F.split(G,1)[1].strip();B=await get_entity(H)
		if not B:await A.reply(R);await A.delete();return
		muted_users.add(B.id);data[_E]=list(muted_users);save_data(data);await A.reply(f"🔕 Muted {B.first_name or B.username or B.id}.");await A.delete();return
	elif D.startswith('.unmute ')or D.startswith(o)and A.is_reply:
		if A.is_reply:E=await A.get_reply_message();B=await client.get_entity(E.sender_id)
		else:H=F.split(G,1)[1].strip();B=await get_entity(H)
		if not B:await A.reply(R);await A.delete();return
		muted_users.discard(B.id);data[_E]=list(muted_users);save_data(data);await A.reply(f"Unmuted {B.first_name or B.username or B.id}. Messages from them will no longer be auto-deleted.");await A.delete();return
	elif D.startswith('.calc '):
		k=F[6:]
		try:A2=sympy.sympify(k);await A.reply(f"{k} = {A2}")
		except Exception:await A.reply('Invalid math expression.')
		await A.delete();return
	elif D.startswith('.iginfo ')or D.startswith('.insta '):H=F.split(G,1)[1].replace('@','');b=asyncio.get_event_loop();V=await b.run_in_executor(h,get_ig_info,H);await A.reply(V);await A.delete();return
	elif D.startswith('.block ')or D.startswith('.unblock '):
		A3,H=F.split(G,1);S=await get_entity(H.strip())
		if not S:await A.reply(R);await A.delete();return
		if A3=='.block':await client(functions.contacts.BlockRequest(S.id));await A.reply(f"Blocked {H}")
		else:await client(functions.contacts.UnblockRequest(S.id));await A.reply(f"Unblocked {H}")
		await A.delete();return
	elif D.startswith('.countdown'):
		async def l(ev,seconds,message,receiver):
			A=seconds;B=await ev.reply(f"Countdown: {A} seconds")
			for C in range(A-1,0,-1):
				await asyncio.sleep(1)
				try:await B.edit(f"Countdown: {C} seconds")
				except Exception:pass
			await asyncio.sleep(1)
			try:await B.delete()
			except Exception:pass
			await client.send_message(receiver,message)
		if A.is_reply:
			E=await A.get_reply_message();C=F.split();L=10
			if len(C)>1:
				try:L=int(C[1])
				except Exception:await A.reply(p);return
			O=E.text or'Countdown finished!';A4=E.sender_id;await A.delete();await l(A,L,O,A4)
		else:
			C=F.split(G,2)
			if len(C)<3:await A.reply('Usage: `.countdown <seconds> <message>` or reply with `.countdown <seconds>`');await A.delete();return
			try:L=int(C[1])
			except Exception:await A.reply(p);await A.delete();return
			O=C[2];await A.delete();await l(A,L,O,A.chat_id)
		return
	elif D.startswith('.gc'):
		if A.is_reply:
			E=await A.get_reply_message();A5=await get_gc_ids();J=0
			for A6 in A5:
				try:await client.send_message(A6,f"{E.text}");J+=1;await asyncio.sleep(1)
				except Exception:continue
			await A.reply(f"Sent to {J} groups.")
		else:await A.reply('Reply to a message with `.gc` to broadcast.')
		await A.delete();return
	elif D.startswith('.broad'):
		if A.is_reply:
			E=await A.get_reply_message();A7=await get_all_user_ids();J=0
			for A8 in A7:
				try:await client.send_message(A8,f"{E.text}");J+=1;await asyncio.sleep(1)
				except Exception:continue
			await A.reply(f"Broadcasted to {J} users.")
		else:await A.reply('Reply to a message with `.broad` to broadcast to users.')
		await A.delete();return
	elif D.startswith('.dmfrwd'):
		C=F.split()
		if A.is_reply:
			E=await A.get_reply_message();W=[]
			if len(C)>=2 and C[1].startswith('@'):
				S=await get_entity(C[1])
				if S:W=[S.id]
				else:W=await get_all_user_ids()
			else:W=await get_all_user_ids()
			J=0
			for A9 in W:
				try:await client.forward_messages(A9,E);J+=1;await asyncio.sleep(1)
				except Exception:continue
			await A.reply(f"Forwarded to {J} DMs!")
		else:await A.reply('Reply to a message with `.dmfrwd @username` or just `.dmfrwd` to all.')
		await A.delete();return
	elif D.startswith('.dm'):
		T=F[3:].strip();X=h;Y=''
		if A.is_reply:E=await A.get_reply_message();X=E.sender_id;Y=T
		else:
			C=T.split()
			if C and C[0].startswith('@'):
				H=C[0];Y=G.join(C[1:]);B=await get_entity(H)
				if not B:await A.reply('Invalid username.');await A.delete();return
				X=B.id
			else:await A.reply('Usage: `.dm @username message` or reply `.dm message`');await A.delete();return
		if X and Y:await client.send_message(X,f"{Y}")
		await A.delete();return
	elif D.startswith('.adopt'):
		if A.is_reply:E=await A.get_reply_message();U=await client.get_entity(E.sender_id);c=await client.get_me();d=U.first_name or U.username or str(U.id);AA=c.first_name or c.username or str(c.id);await A.reply(f"🎉 𝗖𝗼𝗻𝗴𝗿𝗮𝘁𝘀 {d} (@{U.username if hasattr(U,i)and U.username else _B}) 𝙄𝙨 𝙣𝙤𝙬 {AA}'s 𝙉𝙚𝙬 𝙨𝙤𝙣")
		else:await A.reply('Reply to a user with `.adopt` to adopt them.')
		await A.delete();return
	elif D.startswith('.show'):
		if A.is_reply:E=await A.get_reply_message();B=await client.get_entity(E.sender_id);d=B.first_name or _B;AB=B.id;H=f"@{B.username}"if hasattr(B,i)and B.username else _B;AC=_B;e=f"Name: {d}\nID: {AB}\nUsername: {H}\nPast usernames: {AC}";await A.reply(e)
		else:await A.reply('Reply to a user with `.show` to get info.')
		await A.delete();return
	elif D.startswith('.mm'):
		if A.is_reply:
			E=await A.get_reply_message();P=await client.get_entity(E.sender_id)
			try:await client(functions.messages.CreateChatRequest(users=[P.id],title=f"MM Chat with {P.first_name or P.username or P.id}"));await A.reply(f"𝐆𝐫𝐨𝐮𝐩 𝐜𝐫𝐞𝐚𝐭𝐞𝐝 {P.first_name or P.username or P.id}.")
			except Exception as I:await A.reply(f"Error creating group: {I}")
		else:await A.reply('Reply to a user with `.mm` to create private group.')
		await A.delete();return
	elif D.startswith('.owner'):M=await client.get_me();AD=f"𝐎𝐰𝐧𝐞𝐫 𝐢𝐧𝐟𝐨 ✨\n𝐁𝐨𝐭 𝐜𝐫𝐞𝐚𝐭𝐞𝐝 𝐛𝐲 : [#𝗥𝗔𝗗𝗛𝗘𝗬](t.me/sunradhey)\n𝐂𝐡𝐚𝐭 𝐈𝐝 : {M.id}\n𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞 : @{M.username if M.username else _B}";await A.reply(AD);await A.delete();return
	elif D.startswith('.mute'):
		if A.is_reply:E=await A.get_reply_message();B=await client.get_entity(E.sender_id)
		else:
			C=F.split(G,1)
			if len(C)<2:await A.reply('Specify username to mute or reply to user.');await A.delete();return
			B=await get_entity(C[1])
		if not B:await A.reply(R);await A.delete();return
		muted_users.add(B.id);data[_E]=list(muted_users);save_data(data);await A.reply(f"🔕 Muted user {B.first_name or B.username or B.id}");await A.delete();return
	elif D.startswith(o):
		if A.is_reply:E=await A.get_reply_message();B=await client.get_entity(E.sender_id)
		else:
			C=F.split(G,1)
			if len(C)<2:await A.reply('Specify username to unmute or reply to user.');await A.delete();return
			B=await get_entity(C[1])
		if not B:await A.reply(R);await A.delete();return
		muted_users.discard(B.id);data[_E]=list(muted_users);save_data(data);await A.reply(f"🗣️ Unmuted user {B.first_name or B.username or B.id}.");await A.delete();return
	elif D.startswith('.ban'):
		if A.is_reply:E=await A.get_reply_message();B=await client.get_entity(E.sender_id)
		else:
			C=F.split(G,1)
			if len(C)<2:await A.reply('Specify username to ban or reply to user.');await A.delete();return
			B=await get_entity(C[1])
		if not B:await A.reply(R);await A.delete();return
		banned_users.add(B.id);data[_G]=list(banned_users);save_data(data);await A.reply(f"❌ Banned user {B.first_name or B.username or B.id}.");await A.delete();return
	elif D.startswith('.unban'):
		if A.is_reply:E=await A.get_reply_message();B=await client.get_entity(E.sender_id)
		else:
			C=F.split(G,1)
			if len(C)<2:await A.reply('Specify username to unban or reply to user.');await A.delete();return
			B=await get_entity(C[1])
		if not B:await A.reply(R);await A.delete();return
		banned_users.discard(B.id);data[_G]=list(banned_users);save_data(data);await A.reply(f"✅ Unbanned user {B.first_name or B.username or B.id}.");await A.delete();return
	elif D.startswith('.kick'):
		if A.is_group:
			if A.is_reply:
				E=await A.get_reply_message();Z=await client.get_entity(E.sender_id)
				try:await client.kick_participant(A.chat_id,Z.id);await A.reply(f"🦵 Kicked {Z.first_name or Z.username or Z.id}")
				except Exception as I:await A.reply(f"Failed to kick: {I}")
			else:await A.reply('Reply to the user to kick.')
		else:await A.reply('This command works only in groups.')
		await A.delete();return
	elif D.startswith('.asleep'):
		M=await client.get_me();N=M.first_name or''
		if q not in N:
			Q=N+r
			try:await client(functions.account.UpdateProfileRequest(first_name=Q));await A.reply("Added '~ asleep' to your first name.")
			except Exception as I:await A.reply(f"Failed to update name: {I}")
		else:await A.reply('Already marked as asleep.')
		await A.delete();return
	elif D.startswith('.awake'):
		M=await client.get_me();N=M.first_name or''
		if q in N:
			Q=N.replace(r,'')
			try:await client(functions.account.UpdateProfileRequest(first_name=Q));await A.reply("Removed '~ asleep' from your first name.")
			except Exception as I:await A.reply(f"Failed to update name: {I}")
		else:await A.reply('You are not marked as asleep.')
		await A.delete();return
	elif D.startswith('.busy'):
		M=await client.get_me();N=M.first_name or''
		if s not in N:
			Q=N+t
			try:await client(functions.account.UpdateProfileRequest(first_name=Q));await A.reply("Added '~ Busy' to your first name.")
			except Exception as I:await A.reply(f"Failed to update name: {I}")
		else:await A.reply('Already marked as busy.')
		await A.delete();return
	elif D.startswith('.free'):
		M=await client.get_me();N=M.first_name or''
		if s in N:
			Q=N.replace(t,'')
			try:await client(functions.account.UpdateProfileRequest(first_name=Q));await A.reply("Removed '~ Busy' from your first name.")
			except Exception as I:await A.reply(f"Failed to update name: {I}")
		else:await A.reply('You are not marked as busy.')
		await A.delete();return
	elif D.startswith('.rst'):
		f=F.split(G,1)
		if len(f)<2 or not f[1].strip():await A.reply('Usage: .rst <instagram_username>');await A.delete();return
		H=f[1].strip();b=asyncio.get_event_loop();V=await b.run_in_executor(h,send_instagram_reset,H);await A.reply(V);await A.delete();return
	elif D.startswith('.tinfo '):
		H=F.split(G,1)[1].strip();B=await get_entity(H)
		if B:e=f"👤 𝐍𝐚𝐦𝐞 : {B.first_name or _B}\n🆔 𝐂𝐡𝐚𝐭 𝐈𝐝 : {B.id}\n🌌 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞 : @{B.username if hasattr(B,i)and B.username else _B}\n🤖 𝐒𝐭𝐚𝐭𝐮𝐬 𝐛𝐨𝐭 : {B.bot if hasattr(B,'bot')else _B}";await A.reply(e)
		else:await A.reply('𝗨𝘀𝗲𝗿 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱')
		await A.delete();return
	elif D.startswith('.count '):
		C=F.split(G,1)
		if len(C)<2 or not C[1].strip().isdigit():await A.reply('Usage: .count <seconds>');await A.delete();return
		L=int(C[1].strip())
		if L<1 or L>300:await A.reply('Enter countdown between 1 and 300 seconds.');await A.delete();return
		m=await A.reply(f"𝘾𝙤𝙪𝙣𝙩𝙙𝙤𝙬𝙣 : {L} 𝙎𝙚𝙘𝙤𝙣𝙙𝙨")
		for AE in range(L-1,-1,-1):
			await asyncio.sleep(1)
			try:await m.edit(f"Countdown: {AE} seconds")
			except Exception:pass
		try:await m.delete()
		except Exception:pass
		await A.delete();return
	elif D.startswith('.spam '):
		C=F.split(G,2)
		if len(C)<3 or not C[1].isdigit():await A.reply('Usage: `.spam <count> <message>`');await A.delete();return
		J=int(C[1]);O=C[2]
		if J>50:await A.reply('Count too high! Limit is 50.');await A.delete();return
		for _ in range(J):await client.send_message(A.chat_id,O);await asyncio.sleep(.8)
		await A.delete();return
	elif D=='.del':
		if not A.is_private:await A.reply('This command only works in private chats.');await A.delete();return
		try:g=await client.get_messages(A.chat_id,limit=1000);AF=[A.id for A in g];await client.delete_messages(A.chat_id,AF,revoke=_C);await A.respond('🧹 𝐂𝐥𝐞𝐚𝐫𝐞𝐝 𝐜𝐡𝐚𝐭 𝐡𝐢𝐬𝐭𝐨𝐫𝐲')
		except Exception as I:await A.reply(f"Failed to delete chat: {I}")
		await A.delete();return
	elif D.startswith('.purge '):
		C=F.split(G,1)
		try:J=int(C[1])
		except Exception:await A.reply('Invalid count.');await A.delete();return
		g=await client.get_messages(A.chat_id,limit=J+1);AG=[A.id for A in g]
		try:await client.delete_messages(A.chat_id,AG);await A.reply(f"𝐏𝐮𝐫𝐠𝐞𝐝 {J}")
		except Exception as I:await A.reply(f"Failed to delete messages: {I}")
		await A.delete();return
	elif D.startswith('.close '):
		if not A.is_group:await A.reply('This command only works in groups.');await A.delete();return
		C=F.split(G,1)
		try:n=int(C[1])
		except Exception:await A.reply('Invalid time in seconds.');await A.delete();return
		await A.reply(f"𝐆𝐫𝐨𝐮𝐩 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐝𝐞𝐥𝐞𝐭𝐞𝐝 𝐢𝐧 {n} 𝗦𝗲𝗰𝗼𝗻𝗱𝘀");await asyncio.sleep(n)
		try:await client.delete_dialog(A.chat_id)
		except Exception as I:await A.reply(f"Failed to delete group: {I}")
		return
	elif D.startswith('.cinfo '):
		C=F.split(G,1)
		if len(C)<2 or not re.match('^\\+?\\d+$',C[1].strip()):await A.reply('Usage: .cinfo {number} (e.g., .cinfo +911234567890)');await A.delete();return
		AH=C[1].strip();AI=await get_phone_info(AH);await A.reply(AI);await A.delete();return
	elif D.startswith('.note '):
		C=F.split(G,2)
		if len(C)<3:await A.reply('Usage: .note <name> <content>');await A.delete();return
		K=C[1].strip();AJ=C[2].strip();notes[K]=AJ;data[_H]=notes;save_data(data);await A.reply(f"Note '{K}' saved.");await A.delete();return
	elif D=='.notes':
		if not notes:await A.reply('No notes saved.')
		else:AK='\n'.join([f"{A+1}. {B}"for(A,B)in enumerate(notes.keys())]);await A.reply(f"Saved notes:\n{AK}")
		await A.delete();return
	elif D.startswith('.getnote '):
		C=F.split(G,1)
		if len(C)<2:await A.reply('Usage: .getnote <name>');await A.delete();return
		K=C[1].strip()
		if K in notes:await A.reply(f"Note '{K}': {notes[K]}")
		else:await A.reply(f"Note '{K}' not found.")
		await A.delete();return
	elif D.startswith('.delnote '):
		C=F.split(G,1)
		if len(C)<2:await A.reply('Usage: .delnote <name>');await A.delete();return
		K=C[1].strip()
		if K in notes:del notes[K];data[_H]=notes;save_data(data);await A.reply(f"Note '{K}' deleted.")
		else:await A.reply(f"Note '{K}' not found.")
		await A.delete();return
	elif D.startswith('.qr '):
		if not QRCODE_AVAILABLE:await A.reply(_L);await A.delete();return
		T=F[4:].strip()
		if not T:await A.reply('Usage: .qr <text>');await A.delete();return
		a=f"qr_{int(time.time())}.png";V=await generate_qr(T,a)
		if os.path.exists(a):await client.send_file(A.chat_id,a,caption=f"QR code for: {T}");os.remove(a)
		else:await A.reply(V)
		await A.delete();return
	elif D=='.help':AL='\n🤖 **SELFBOT COMMANDS** 🤖\n\n**Basic Commands**\n`.ping` - Check bot response time\n`.afk [reason]` - Set AFK status\n`.unafk` - Remove AFK status\n`.autoreply [message]` - Set auto-reply message\n`.autoreply off` - Disable auto-reply\n`.autoaccept` - Toggle auto-accept chat requests\n\n**User Management**\n`.mute @user` - Mute a user (auto-delete their messages)\n`.unmute @user` - Unmute a user\n`.ban @user` - Ban a user (auto-delete their messages)\n`.unban @user` - Unban a user\n`.kick` (reply) - Kick user from group\n`.block @user` - Block a user\n`.unblock @user` - Unblock a user\n`.dmute @user` - Mute a user (with notification)\n`.show` (reply) - Show user info\n\n**Group Management**\n`.mm` (reply) - Create private group with user\n`.gc` (reply) - Broadcast to all groups\n`.broad` (reply) - Broadcast to all users\n`.dmfrwd` (reply) - Forward to all DMs\n`.dm @user message` - Send direct message\n`.purge N` - Delete last N messages\n`.close N` - Delete group after N seconds\n\n**Status Commands**\n`.asleep` - Add "~ asleep" to your name\n`.awake` - Remove "~ asleep" from your name\n`.busy` - Add "~ Busy" to your name\n`.free` - Remove "~ Busy" from your name\n\n**Information Commands**\n`.owner` - Show owner info\n`.tinfo @user` - Get Telegram user info\n`.cinfo +1234567890` - Get phone number info\n`.iginfo @user` - Get Instagram info\n`.rst @user` - Send Instagram password reset\n\n**Utility Commands**\n`.calc 2+2` - Calculate math expression\n`.count N` - Countdown timer\n`.spam N message` - Spam message N times\n`.del` - Clear private chat history\n`.adopt` (reply) - Adopt a user (fun)\n`.note name content` - Save a note\n`.notes` - List all notes\n`.getnote name` - Get a note\n`.delnote name` - Delete a note\n`.qr text` - Generate QR code\n\n**Note:** Some commands require replying to a message.\n';await A.reply(AL);await A.delete();return
@client.on(events.NewMessage(incoming=_C))
async def incoming_handler(event):
	A=event;global muted_users,banned_users,afk_data,auto_reply_data,auto_accept_requests
	if A.sender_id==(await client.get_me()).id:return
	if auto_accept_requests and isinstance(A,events.ChatAction):
		if A.user_added and(await client.get_me()).id in A.user_ids:await A.reply('Thanks for adding me!')
	if A.sender_id in banned_users:
		try:await A.delete()
		except Exception:pass
		return
	if A.sender_id in muted_users:
		try:await A.delete()
		except Exception:pass
		return
	if afk_data[_A]and A.is_private:B=time.time()-afk_data[_F];C,D=divmod(B,3600);E,F=divmod(D,60);G=f"{int(C)}h {int(E)}m {int(F)}s";H=f"🚫 I'm AFK: {afk_data[_I]}\n⏰ Since: {G} ago";await A.reply(H);return
	if auto_reply_data[_A]and A.is_private:await A.reply(auto_reply_data[_J]);return
if __name__=='__main__':print(Colorate.Horizontal(Colors.green_to_blue,'SELFBOT is running...'));client.run_until_disconnected()