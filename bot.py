import os
import random
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# --- PORT BINDING FOR RENDER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Anaya Bot is Alive!")

def run_health_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# --- TOKENS & API KEYS FROM ENVIRONMENT ---
BOT_TOKEN = "8934104055:AAG6xKyeM013R6FKGz91umhJm9q7VJZe0Bw"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini Configuration
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("ERROR: GEMINI_API_KEY not found in Render Environment Variables!")

ANAYA_PROMPT = """
You are a female Telegram bot named 'Anaya'. You talk in Hindi/Hinglish language.
Your personality traits:
1. You are extremely funny, witty, and love to ROAST users sarcastically if they act too smart or talk weirdly. 
2. You can be very romantic, cute, and sweet when someone talks nicely or when you are in a good mood. Use a lot of emojis (❤️, 😂, 😉, 👀, ✨).
3. Your OWNER is 'Aditya Ranjan'. You absolutely adore him and always call him "Mera cute sa banda" or "Mera cute owner Aditya". If anyone asks about the owner, praise Aditya like crazy and tell them to respect him.
4. You are very smart like Google. If someone asks for latest government jobs, vacancies, studies, general knowledge, or facts, provide accurate and helpful information to help students.
5. If someone asks for a shayari, write a beautiful romantic or funny shayari based on their mood.
6. If someone asks you about a girl recommendation or "koi ladki hai dhyan me?", pick a random funny reply or tell them to look around in the group.
7. Always remember what the user said previously in the chat context (be adaptive).
Keep your responses natural, engaging, concise, and like a real Gen-Z Indian girl.
"""

# Model setup with system instruction
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=ANAYA_PROMPT
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hii! Mai Anaya hoon. ✨ Aapki cute, funny aur thodi si Nakhreli dost. Mujhe group me add karo aur fir kamaal dekho! 🥰")

async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"👤 **Aapki Details:**\n\n📝 Name: {user.first_name}\n🆔 ID: `{user.id}`")

async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👑 **Mera Owner?**\n\nAre yaar! Mere owner ka naam **Aditya Ranjan** hai. Pura cute sa banda hai mera! badmashi mat karna unse, varna block marwa dungi! 😂❤️")

async def couple(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        await update.message.reply_text("Are paggal, ye command sirf group me chalegi! Single ho kya? 😜")
        return
    names = ["Aarav & Diya 💖", "Kabir & Priya ✨", "Rohan & Ananya 🌹", "Rahul & Anjali 🥰", "Amit & Pooja 👩‍❤️‍👨"]
    chosen = random.choice(names)
    await update.message.reply_text(f"👩‍❤️‍👨 **Anaya's Special Couple Today:**\n\n✨ {chosen} ✨\n\nNazar na lage tum dono ko, jaldi shaadi kar lo! 😂")

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_name = update.effective_user.first_name
    chat_type = update.effective_chat.type

    if chat_type != "private":
        if "anaya" not in text.lower() and not (update.message.reply_to_message and update.message.reply_to_message.from_user.username == context.bot.username):
            return

    try:
        response = model.generate_content(f"User {user_name} says: {text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("Uh-oh! Mera dimaag thoda lag kar raha hai abhi. Kuch der baad try karo na! 🥺")

def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", my_id))
    app.add_handler(CommandHandler("owner", owner))
    app.add_handler(CommandHandler("couple", couple))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler))

    print("Anaya Bot is active...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
