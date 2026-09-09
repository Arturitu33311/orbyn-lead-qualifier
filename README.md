# Orbyn Lead Qualifier Bot
> Agente de cualificación de leads conectado a Telegram con logging en Google Sheets.

## ¿Qué hace?
Recibe datos de un lead en texto libre via Telegram, analiza si encaja con el ICP
de Orbyn usando un LLM, responde con la decisión y loguea todo en Google Sheets.

## ICP evaluado
- Empresa de servicios o consultoría
- Mínimo 5 empleados
- España o Latinoamérica
- Interés en automatización o IA

## Stack
| Componente | Tecnología |
|-----------|-----------|
| Mensajería | Telegram Bot API (pyTelegramBotAPI) |
| LLM | Gemini 2.0 Flash via OpenRouter |
| Logging | Google Sheets API (gspread) |
| Infra | Python 3.12 · Debian · systemd |

## Configuración
1. Copia bot_public.py a bot.py
2. Rellena las variables de config con tus credenciales
3. Añade tu credentials.json de Google Service Account
4. Comparte tu Google Sheet con el email de la service account
