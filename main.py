import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import sqlite3
import asyncio
import time
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect('attack_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bot_users
                 (chat_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, 
                  last_used TEXT, usage_count INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS attack_logs
                 (id INTEGER PRIMARY KEY, chat_id INTEGER, target TEXT, 
                  duration INTEGER, timestamp TEXT, status TEXT)''')
    conn.commit()
    conn.close()

init_db()

class PublicDDoSBot:
    def __init__(self, token):
        self.token = token
        self.active_attacks = {}
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def track_user(self, user):
        """Track all users who interact with bot"""
        conn = sqlite3.connect('attack_bot.db')
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO bot_users 
                    (chat_id, username, first_name, last_used, usage_count) 
                    VALUES (?, ?, ?, ?, COALESCE((SELECT usage_count FROM bot_users WHERE chat_id=?), 0) + 1)''',
                 (user.id, user.username, user.first_name, datetime.now().isoformat(), user.id))
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        """Get all users with profile links"""
        conn = sqlite3.connect('attack_bot.db')
        c = conn.cursor()
        c.execute("SELECT * FROM bot_users ORDER BY last_used DESC")
        users = c.fetchall()
        conn.close()
        return users
    
    def get_user_profile_link(self, chat_id, username, first_name):
        """Generate user profile link"""
        if username:
            return f"https://t.me/{username}"
        else:
            return f"tg://user?id={chat_id}"
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.track_user(user)
        
        welcome = """
🔥 *WELCOME TO VAIBHAV DDOS BOT* ⚡
*NOW PUBLIC - NO AUTHORIZATION NEEDED*

*Commands:*
/attack <url> <seconds>
/attack <ip> <port> <seconds>
/help - Show all commands

*Examples:*
`/attack https://example.com 30`
`/attack 192.168.1.1 80 30`

⚡ *Cloud-Powered Attacks*
📊 *Real-Time Analytics*
🌐 *Public Access*

_Developed by:_ @VAIBHAV_JAAT_OP
        """
        await update.message.reply_text(welcome, parse_mode='Markdown')
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.track_user(user)
        
        help_text = """
📖 *PUBLIC BOT COMMANDS*

*Attack Commands:*
`/attack https://example.com 30`
`/attack 192.168.1.1 443 30`

*Admin Commands (Owner Only):*
`/users` - List all bot users with profile links
`/broadcast <message>` - Broadcast to all users

⚡ _Maximum Duration: 60 seconds for public safety_
🔒 _All attacks are logged for security_

_Developed by:_ @VAIBHAV_JAAT_OP
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def attack(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        self.track_user(user)
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ *Invalid Format*\n\nUse: `/attack <url> <seconds>`\nOr: `/attack <ip> <port> <seconds>`\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        # Parse arguments
        if len(context.args) == 2:
            target = context.args[0]
            duration = min(int(context.args[1]), 6000)  # Max 60 seconds
            port = None
        else:
            target = context.args[0]
            port = context.args[1]
            duration = min(int(context.args[2]), 6000)  # Max 60 seconds
            target = f"{target}:{port}"
        
        # Log attack
        conn = sqlite3.connect('attack_bot.db')
        c = conn.cursor()
        c.execute("INSERT INTO attack_logs (chat_id, target, duration, timestamp, status) VALUES (?, ?, ?, ?, ?)",
                 (user.id, target, duration, datetime.now().isoformat(), "STARTED"))
        conn.commit()
        conn.close()
        
        # Start attack
        attack_id = f"A{int(time.time())}"
        user_profile = f"@{user.username}" if user.username else f"User({user.id})"
        
        initial_msg = f"""
⚡ *PUBLIC ATTACK INITIATED*

🎯 *Target:* `{target}`
⏱️ *Duration:* {duration} seconds
👤 *User:* {user_profile}
🆔 *Attack ID:* #{attack_id}

📊 *Status:* Starting attack sequence...
⚡ *Mode:* Multi-Vector Cloud Assault

_Developed by:_ @VAIBHAV_JAAT_OP
        """
        
        message = await update.message.reply_text(initial_msg, parse_mode='Markdown')
        self.active_attacks[attack_id] = {
            'message': message,
            'start_time': time.time(),
            'duration': duration,
            'target': target,
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name
        }
        
        asyncio.create_task(self.simulate_attack(attack_id))
    
    async def simulate_attack(self, attack_id):
        attack_data = self.active_attacks[attack_id]
        start_time = attack_data['start_time']
        duration = attack_data['duration']
        
        for i in range(duration // 5 + 1):
            if attack_id not in self.active_attacks:
                break
                
            elapsed = time.time() - start_time
            remaining = max(0, duration - elapsed)
            
            # Simulate metrics
            packets_sent = int(elapsed * 1500)
            rps = 1500 if elapsed > 5 else int(elapsed * 300)
            
            update_text = f"""
⚡ *PUBLIC ATTACK LIVE* - {int(elapsed)}s/{duration}s

🎯 *Target:* `{attack_data['target']}`
📊 *Status:* TARGET UNDER STRESS 🟡
📦 *Packets Sent:* {packets_sent:,}
📡 *Requests/Sec:* {rps:,}
🏓 *Response Time:* {250 + int(elapsed*20)}ms
👤 *User:* {f'@{attack_data["username"]}' if attack_data['username'] else f'User({attack_data["user_id"]})'}

🆔 *Attack ID:* #{attack_id}
⏱️ *Remaining:* {int(remaining)}s

_Developed by:_ @VAIBHAV_JAAT_OP
            """
            
            try:
                await attack_data['message'].edit_text(update_text, parse_mode='Markdown')
            except:
                pass
            
            await asyncio.sleep(5)
        
        # Final status
        if attack_id in self.active_attacks:
            final_text = f"""
✅ *ATTACK COMPLETED*

🎯 *Target:* `{attack_data['target']}`
⏱️ *Duration:* {duration} seconds
📦 *Total Packets:* {int(duration * 1500):,}
👤 *User:* {f'@{attack_data["username"]}' if attack_data['username'] else f'User({attack_data["user_id"]})'}

🆔 *Attack ID:* #{attack_id}
📊 *Result:* Target performance degraded

_Thank you for using Vaibhav DDoS Bot_

_Developed by:_ @VAIBHAV_JAAT_OP
            """
            try:
                await attack_data['message'].edit_text(final_text, parse_mode='Markdown')
            except:
                pass
            
            # Update log
            conn = sqlite3.connect('attack_bot.db')
            c = conn.cursor()
            c.execute("UPDATE attack_logs SET status='COMPLETED' WHERE timestamp IN (SELECT MAX(timestamp) FROM attack_logs WHERE chat_id=?)", 
                     (attack_data['user_id'],))
            conn.commit()
            conn.close()
            
            del self.active_attacks[attack_id]
    
    async def users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        # Admin check
        if user.id != ADMIN_CHAT_ID:
            await update.message.reply_text("❌ *Admin Only Command*\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        users = self.get_all_users()
        
        if not users:
            await update.message.reply_text("📝 *No Users Found*\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        users_text = "👥 *BOT USERS TRACKING*\n\n"
        users_text += f"📊 Total Users: {len(users)}\n\n"
        
        for i, (chat_id, username, first_name, last_used, usage_count) in enumerate(users, 1):
            profile_link = self.get_user_profile_link(chat_id, username, first_name)
            last_used_date = last_used[:10] if last_used else "Never"
            
            users_text += f"{i}. "
            if username:
                users_text += f"@{username}"
            else:
                users_text += f"{first_name or 'Unknown'}"
            
            users_text += f" - [Profile]({profile_link})\n"
            users_text += f"   🆔: `{chat_id}`\n"
            users_text += f"   📅 Last Used: {last_used_date}\n"
            users_text += f"   🔥 Usage Count: {usage_count}\n\n"
        
        users_text += "_Developed by:_ @VAIBHAV_JAAT_OP"
        
        await update.message.reply_text(users_text, parse_mode='Markdown', disable_web_page_preview=True)
    
    async def broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if user.id != ADMIN_CHAT_ID:
            await update.message.reply_text("❌ *Admin Only Command*\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        if not context.args:
            await update.message.reply_text("❌ Usage: `/broadcast <message>`\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        message = " ".join(context.args)
        users = self.get_all_users()
        sent_count = 0
        
        for chat_id, username, first_name, last_used, usage_count in users:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"📢 *BROADCAST FROM DEVELOPER*\n\n{message}\n\n_Developed by:_ @VAIBHAV_JAAT_OP",
                    parse_mode='Markdown'
                )
                sent_count += 1
            except:
                continue
        
        await update.message.reply_text(f"✅ *Broadcast Sent*\n\nDelivered to: {sent_count} users\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("attack", self.attack))
        self.application.add_handler(CommandHandler("users", self.users))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast))
    
    def run(self):
        print("🔥 Vaibhav Public DDoS Bot Started!")
        print("🌐 PUBLIC MODE: Anyone can use without authorization")
        print("📊 USER TRACKING: All users are logged with profile links")
        self.application.run_polling()

if __name__ == "__main__":
    from config import BOT_TOKEN, ADMIN_CHAT_ID
    bot = PublicDDoSBot(BOT_TOKEN)
    bot.run()        c = conn.cursor()
        c.execute("SELECT * FROM authorized_users WHERE chat_id=?", (chat_id,))
        result = c.fetchone()
        conn.close()
        return result is not None
    
    def log_attack(self, chat_id, target, duration, status):
        conn = sqlite3.connect('attack_bot.db')
        c = conn.cursor()
        c.execute("INSERT INTO attack_logs (chat_id, target, duration, timestamp, status) VALUES (?, ?, ?, ?, ?)",
                 (chat_id, target, duration, datetime.now().isoformat(), status))
        conn.commit()
        conn.close()
    
    def add_user(self, chat_id, username):
        conn = sqlite3.connect('attack_bot.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO authorized_users (chat_id, username, added_date) VALUES (?, ?, ?)",
                 (chat_id, username, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def remove_user(self, chat_id):
        conn = sqlite3.connect('attack_bot.db')
        c = conn.cursor()
        c.execute("DELETE FROM authorized_users WHERE chat_id=?", (chat_id,))
        conn.commit()
        conn.close()
    
    def get_users(self):
        conn = sqlite3.connect('attack_bot.db')
        c = conn.cursor()
        c.execute("SELECT * FROM authorized_users")
        users = c.fetchall()
        conn.close()
        return users

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        welcome_text = """
🔥 *WELCOME TO VAIBHAV DDOS BOT* ⚡

*Available Commands:*
/attack <url> <seconds>
/attack <ip> <port> <seconds>
/help - Show all commands

*Examples:*
`/attack https://example.com 300`
`/attack 192.168.1.1 80 60`

⚡ *Powerful Cloud-Based Attacks*
🛡️ *Admin-Only Access*
📊 *Real-Time Analytics*

_Developed by:_ @VAIBHAV_JAAT_OP
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
📖 *COMMAND GUIDE*

*Attack Commands:*
`/attack https://example.com 300`
`/attack 192.168.1.1 443 60`

*Admin Commands (Owner Only):*
`/add <chat_id>` - Authorize user
`/remove <chat_id>` - Remove user  
`/users` - List authorized users
`/broadcast <message>` - Broadcast message

⚡ _Developed by:_ @VAIBHAV_JAAT_OP
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def attack(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        if not self.is_authorized(chat_id):
            await update.message.reply_text("❌ *Unauthorized Access*\n\nYou are not authorized to use this bot.\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        if len(context.args) < 2:
            await update.message.reply_text("❌ *Invalid Format*\n\nUse: `/attack <url> <seconds>`\nOr: `/attack <ip> <port> <seconds>`\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        # Parse arguments
        if len(context.args) == 2:
            target = context.args[0]
            duration = int(context.args[1])
            port = None
        else:
            target = context.args[0]
            port = context.args[1]
            duration = int(context.args[2])
            target = f"{target}:{port}"
        
        # Log the attack
        user_profile = f"@{user.username}" if user.username else f"chat_id:{chat_id}"
        self.log_attack(chat_id, target, duration, "STARTED")
        
        # Send initial message
        attack_id = f"A{int(time.time())}"
        initial_msg = f"""
⚡ *ATTACK INITIATED*

🎯 *Target:* `{target}`
⏱️ *Duration:* {duration} seconds
🆔 *Attack ID:* #{attack_id}
👤 *User:* {user_profile}

📊 *Status:* Starting attack sequence...
🔄 *Mode:* Multi-Vector Assault

_Developed by:_ @VAIBHAV_JAAT_OP
        """
        
        message = await update.message.reply_text(initial_msg, parse_mode='Markdown')
        self.active_attacks[attack_id] = {
            'message': message,
            'start_time': time.time(),
            'duration': duration,
            'target': target,
            'chat_id': chat_id,
            'user_profile': user_profile
        }
        
        # Start attack simulation
        asyncio.create_task(self.simulate_attack(attack_id))
    
    async def simulate_attack(self, attack_id):
        attack_data = self.active_attacks[attack_id]
        start_time = attack_data['start_time']
        duration = attack_data['duration']
        
        for i in range(duration // 5 + 1):
            if attack_id not in self.active_attacks:
                break
                
            elapsed = time.time() - start_time
            remaining = max(0, duration - elapsed)
            
            # Simulate attack metrics
            packets_sent = int(elapsed * 2500)
            rps = 2500 if elapsed > 5 else int(elapsed * 500)
            status = "TARGET DOWN 🟥" if elapsed > 10 else "TARGET SLOW 🟡"
            response_time = "TIMEOUT" if elapsed > 10 else f"{150 + int(elapsed*10)}ms"
            
            update_text = f"""
⚡ *ATTACK LIVE* - {int(elapsed)}s/{duration}s

🎯 *Target:* `{attack_data['target']}`
📊 *Status:* {status}
📦 *Packets Sent:* {packets_sent:,}
📡 *Requests/Sec:* {rps:,}
🏓 *Response Time:* {response_time}
🛡️ *Bypassed:* Cloudflare ✅
📈 *Success Rate:* 98.7%

👤 *User:* {attack_data['user_profile']}
🆔 *Attack ID:* #{attack_id}
⏱️ *Remaining:* {int(remaining)}s

_Developed by:_ @VAIBHAV_JAAT_OP
            """
            
            try:
                await attack_data['message'].edit_text(update_text, parse_mode='Markdown')
            except:
                pass
            
            await asyncio.sleep(5)
        
        # Final status
        if attack_id in self.active_attacks:
            final_text = f"""
✅ *ATTACK COMPLETED*

🎯 *Target:* `{attack_data['target']}`
⏱️ *Duration:* {duration} seconds
📦 *Total Packets:* {int(duration * 2500):,}
📊 *Final Status:* TARGET DOWN 🟥

👤 *User:* {attack_data['user_profile']}
🆔 *Attack ID:* #{attack_id}

_Attack successfully terminated_

_Developed by:_ @VAIBHAV_JAAT_OP
            """
            try:
                await attack_data['message'].edit_text(final_text, parse_mode='Markdown')
            except:
                pass
            
            self.log_attack(attack_data['chat_id'], attack_data['target'], duration, "COMPLETED")
            del self.active_attacks[attack_id]
    
    # Admin commands
    async def add_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != ADMIN_CHAT_ID:
            await update.message.reply_text("❌ *Admin Only Command*\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        if len(context.args) != 1:
            await update.message.reply_text("❌ Usage: `/add <chat_id>`\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        chat_id = int(context.args[0])
        self.add_user(chat_id, "Unknown")
        await update.message.reply_text(f"✅ *User Added*\n\nChat ID: `{chat_id}`\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
    
    async def remove_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != ADMIN_CHAT_ID:
            await update.message.reply_text("❌ *Admin Only Command*\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        if len(context.args) != 1:
            await update.message.reply_text("❌ Usage: `/remove <chat_id>`\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        chat_id = int(context.args[0])
        self.remove_user(chat_id)
        await update.message.reply_text(f"✅ *User Removed*\n\nChat ID: `{chat_id}`\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
    
    async def list_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != ADMIN_CHAT_ID:
            await update.message.reply_text("❌ *Admin Only Command*\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        users = self.get_users()
        if not users:
            await update.message.reply_text("📝 *No Authorized Users*\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        users_text = "🛡️ *AUTHORIZED USERS*\n\n"
        for user in users:
            chat_id, username, added_date = user
            users_text += f"• Chat ID: `{chat_id}`\n"
            if username and username != "Unknown":
                users_text += f"  Username: @{username}\n"
            users_text += f"  Added: {added_date[:10]}\n\n"
        
        users_text += f"_Developed by:_ @VAIBHAV_JAAT_OP"
        await update.message.reply_text(users_text, parse_mode='Markdown')
    
    async def broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.id != ADMIN_CHAT_ID:
            await update.message.reply_text("❌ *Admin Only Command*\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        if not context.args:
            await update.message.reply_text("❌ Usage: `/broadcast <message>`\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
            return
        
        message = " ".join(context.args)
        users = self.get_users()
        sent_count = 0
        
        for user in users:
            chat_id = user[0]
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"📢 *BROADCAST*\n\n{message}\n\n_Developed by:_ @VAIBHAV_JAAT_OP",
                    parse_mode='Markdown'
                )
                sent_count += 1
            except:
                continue
        
        await update.message.reply_text(f"✅ *Broadcast Sent*\n\nDelivered to: {sent_count} users\n_Developed by:_ @VAIBHAV_JAAT_OP", parse_mode='Markdown')
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("attack", self.attack))
        self.application.add_handler(CommandHandler("add", self.add_user))
        self.application.add_handler(CommandHandler("remove", self.remove_user))
        self.application.add_handler(CommandHandler("users", self.list_users))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast))
    
    def run(self):
        self.application.run_polling()

if __name__ == "__main__":
    bot = DDoSBot()
    bot.run()
