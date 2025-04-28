import os
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# Charger les variables d’environnement
load_dotenv()

# Variables requises
REQUIRED_VARS = [
    "EMAIL_HOST", "EMAIL_PORT", "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD", "EMAIL_FROM"
]

# Vérification
missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"⚠️ Les variables suivantes sont manquantes dans le .env : {', '.join(missing_vars)}")

# Config SMTP
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

def send_email(to, cc, subject, body, html=False):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_FROM
        msg["To"] = to
        msg["Cc"] = cc

        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.set_debuglevel(1)  # 🐛 Mode debug SMTP activé
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.send_message(msg)
            print("✅ Email envoyé avec succès à", to)

    except Exception as e:
        print("❌ Erreur lors de l’envoi de l’e-mail :", str(e))
        raise
