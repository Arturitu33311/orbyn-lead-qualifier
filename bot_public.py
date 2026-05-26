import telebot
import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI
from datetime import datetime
import os

# Config
TELEGRAM_TOKEN = "TU_TOKEN_AQUI"
OPENROUTER_KEY = "TU_OPENROUTER_KEY_AQUI"
SHEET_ID = "TU_SHEET_ID_AQUI"
CREDENTIALS_FILE = "credentials.json"

# ICP de Orbyn
ICP = """
Empresa de servicios o consultoría
Mínimo 5 empleados
España o Latinoamérica
Interés en automatización o IA
"""

# Setup Telegram
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Setup OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY
)

# Setup Google Sheets
def get_sheet():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID).sheet1

# Analizar lead con LLM
def qualify_lead(lead_text):
    prompt = f"""Eres un sistema de cualificación de leads para Orbyn, una agencia de automatización con IA.

ICP (perfil de cliente ideal):
{ICP}

Analiza este lead y decide si califica o no:
"{lead_text}"

Responde en este formato exacto:
DECISIÓN: [CUALIFICADO / NO CUALIFICADO]
MOTIVO: [2-3 líneas explicando el razonamiento]"""

    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content

# Loguear en Google Sheets
def log_to_sheet(lead_text, decision, motivo):
    try:
        sheet = get_sheet()
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            lead_text,
            decision,
            motivo
        ])
    except Exception as e:
        print(f"Error logging to sheet: {e}")

# Ignorar comandos /start y /help — responder con instrucciones de uso
@bot.message_handler(commands=['start', 'help'])
def handle_start(message):
    bot.send_message(message.chat.id, 
        "Envíame los datos de un lead en texto libre.\n\n"
        "Ejemplo: *Empresa de consultoría, 15 empleados, México, quieren automatizar ventas*",
        parse_mode="Markdown")

# Handler principal
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    lead_text = message.text
    
    bot.send_message(message.chat.id, "⏳ Analizando lead...")
    
    try:
        resultado = qualify_lead(lead_text)
        
        # Parsear respuesta
        lines = resultado.strip().split("\n")
        decision = "DESCONOCIDO"
        motivo = resultado
        
        for line in lines:
            if line.startswith("DECISIÓN:"):
                decision = line.replace("DECISIÓN:", "").strip()
            if line.startswith("MOTIVO:"):
                motivo = line.replace("MOTIVO:", "").strip()
        
        # Responder en Telegram
        emoji = "✅" if "CUALIFICADO" in decision and "NO" not in decision else "❌"
        respuesta = f"{emoji} *{decision}*\n\n{motivo}"
        bot.send_message(message.chat.id, respuesta, parse_mode="Markdown")
        
        # Loguear
        log_to_sheet(lead_text, decision, motivo)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

print("Bot corriendo...")
bot.polling()
