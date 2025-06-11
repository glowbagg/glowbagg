import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from langdetect import detect
import openai
import time

# Configuración
EMAIL = "infoglowbagg@gmail.com"
APP_PASSWORD = "pcii jwuu qokj vaph"
IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
openai.api_key = "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"

def responder_email(remitente, asunto, cuerpo):
    idioma = detect(cuerpo)
    prompt = f"Responde como si fueras un asistente profesional de Glowbagg, una tienda que vende luces para bolsos. Mensaje del cliente: '{cuerpo}'. Responde en el idioma detectado ({idioma})."

    respuesta_ia = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Eres un asistente amable y profesional de Glowbagg. Respondes dudas sobre productos, pedidos y envíos en cualquier idioma."},
            {"role": "user", "content": prompt}
        ]
    )

    respuesta_final = respuesta_ia['choices'][0]['message']['content']

    msg = MIMEText(respuesta_final)
    msg['Subject'] = f"Re: {asunto}"
    msg['From'] = EMAIL
    msg['To'] = remitente

    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as smtp:
        smtp.login(EMAIL, APP_PASSWORD)
        smtp.sendmail(EMAIL, remitente, msg.as_string())

def revisar_emails():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, APP_PASSWORD)
    mail.select('inbox')

    _, data = mail.search(None, 'UNSEEN')
    for num in data[0].split():
        _, msg_data = mail.fetch(num, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        remitente = email.utils.parseaddr(msg['From'])[1]
        asunto = msg['Subject']
        if msg.is_multipart():
            cuerpo = ""
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    cuerpo = part.get_payload(decode=True).decode()
        else:
            cuerpo = msg.get_payload(decode=True).decode()
        responder_email(remitente, asunto, cuerpo)
    mail.logout()

# Ejecutar en bucle cada 1 minuto
while True:
    revisar_emails()
    time.sleep(60)
