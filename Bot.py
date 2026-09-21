import os
import requests
import telebot

# Siz bergan Telegram bot tokeni
TELEGRAM_BOT_TOKEN = "8253896558:AAHbnvA2k_GdOxaYfG3h64wcKYgYJsvGbzA"

# Siz bergan Fish Audio API kaliti
FISH_API_KEY = "sk-fish-MmToaErPrFzQSzBcwjup3f51p1-5CnLqsFFCPHO3y6Y"

# Ovozlar lug'ati (Siz bergan aniq ID'lar bilan)
VOICES = {
    "fox": "85266846dfa14a2ca3cfacc709a774bb",  # Fox ovozi
    "story": "0f5ae82ac56d4473a9f61abc71fd543a",  # AI Story ozuchka ovozi
}

# Har bir foydalanuvchi uchun tanlangan boshlang'ich ovoz (Standart holatda Fox)
user_voices = {}

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def generate_audio(text: str, voice_id: str):
  url = "https://api.fish.audio/v1/tts"
  headers = {
      "Authorization": f"Bearer {FISH_API_KEY}",
      "Content-Type": "application/json",
  }

  payload = {"text": text, "format": "mp3", "reference_id": voice_id}

  try:
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
      return response.content
    else:
      print(f"Xatolik: {response.status_code} - {response.text}")
      return None
  except Exception as e:
    print(f"Ulanishda xatolik: {e}")
    return None


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
  text = (
      "Salom! Botga xush kelibsiz.\n\n"
      "Ovozni o'zgartirish uchun quyidagi buyruqlardan foydalaning:\n"
      "🦊 /fox - Fox ovozini tanlash\n"
      "📖 /story - AI Story (Ozuchka) ovozini tanlash\n\n"
      "Ovozni tanlaganingizdan keyin menga matn yuboring, ovozli xabar"
      " qilib beraman!"
  )
  bot.reply_to(message, text)


@bot.message_handler(commands=["fox"])
def set_fox(message):
  user_voices[message.chat.id] = VOICES["fox"]
  bot.reply_to(message, "✅ Ovoz **Fox** ga o'zgartirildi! Matn yuboring.")


@bot.message_handler(commands=["story"])
def set_story(message):
  user_voices[message.chat.id] = VOICES["story"]
  bot.reply_to(
      message, "✅ Ovoz **AI Story Ozuchka** ga o'zgartirildi! Matn yuboring."
  )


@bot.message_handler(func=lambda message: True)
def handle_text(message):
  chat_id = message.chat.id
  text = message.text

  # Agar foydalanuvchi hali ovoz tanlamagan bo'lsa, avtomatik ravishda Fox ni tanlaymiz
  if chat_id not in user_voices:
    user_voices[chat_id] = VOICES["fox"]

  current_voice_id = user_voices[chat_id]

  sent_msg = bot.reply_to(message, "Ovoz tayyorlanmoqda, kuting...")

  audio_bytes = generate_audio(text, current_voice_id)

  if audio_bytes:
    file_path = "output.mp3"
    with open(file_path, "wb") as f:
      f.write(audio_bytes)

    with open(file_path, "rb") as audio:
      bot.send_voice(chat_id, audio)

    os.remove(file_path)
    bot.delete_message(chat_id, sent_msg.message_id)
  else:
    bot.edit_message_text(
        "Ovozni yaratishda xatolik yuz berdi.", chat_id, sent_msg.message_id
    )


print("Bot tayyor va ishga tushdi!")

# 409 xatoligini oldini olish uchun webhook tozalanadi
bot.remove_webhook()
bot.infinity_polling()
