from dotenv import load_dotenv
import os

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM')
TWILIO_WHATSAPP_TO = os.getenv('TWILIO_WHATSAPP_TO')
TWILIO_SMS_FROM = os.getenv('TWILIO_SMS_FROM')
TWILIO_SMS_TO = os.getenv('TWILIO_SMS_TO')
