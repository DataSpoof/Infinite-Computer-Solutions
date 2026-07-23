"""
Email Automation with Python -- Sending (SMTP) & Retrieving (IMAP)
=================================================================

What this does
    * send_plain_text()      -> plain text email
    * send_html()            -> HTML email
    * send_with_attachment() -> email with a file attached
    * fetch_recent_emails()  -> read the latest N emails from the inbox (IMAP)

Gmail setup
    1. Enable 2-Step Verification on the sender account.
    2. Create an App Password:  https://myaccount.google.com/apppasswords
    3. DO NOT hardcode it. Put it in an environment variable instead:

           # Windows PowerShell (current terminal only)
           $env:GMAIL_APP_PASSWORD = "your app password"

           # Windows (persist for future terminals)
           setx GMAIL_APP_PASSWORD "your app password"

    Then run:  python email_automation.py

Security note
    App passwords give full mailbox access. Never commit them to git, never
    paste them in chat, and rotate them if they are ever exposed.

No extra installs needed -- smtplib, imaplib and email are in the stdlib.
"""

import imaplib # read email, search, message, download attachment
import os # to create folder and deal with env variabe
import smtplib # sendig email
import ssl # for protecting email connection 
from email import encoders #covert your email into safe format
from email.header import decode_header # decode your body
from email.mime.base import MIMEBase # attach pdf or imahes
from email.mime.multipart import MIMEMultipart # send email with attachment
from email.mime.text import MIMEText # to send html or text email

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SMTP_SERVER = "smtp.gmail.com" # smtp.office365.com
SMTP_PORT = 587                     # 587 = STARTTLS
IMAP_SERVER = "imap.gmail.com" # outlook.office365.com
IMAP_PORT = 993                     # 993 = SSL

SENDER_EMAIL = ""
RECEIVER_EMAIL = ""

# Read the app password from the environment. The second argument is a
# fallback ONLY so the demo runs; replace it by setting GMAIL_APP_PASSWORD
# and delete the literal once you've rotated the exposed password.
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "wmxd msgg nrnl sitv")


# ---------------------------------------------------------------------------
# One shared, authenticated SMTP session helper
# ---------------------------------------------------------------------------
def _send(message):
    """Open a secure SMTP session, log in, and send the given message."""
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)          # upgrade to encrypted TLS
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(message)
    print(f"  Sent: {message['Subject']!r} -> {message['To']}")


# ---------------------------------------------------------------------------
# 1. Plain text email
# ---------------------------------------------------------------------------
def send_plain_text():
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = "Test Email (plain text)"
    msg.attach(MIMEText("Hello from Python! This is a plain text email.", "plain"))
    _send(msg)


# ---------------------------------------------------------------------------
# 2. HTML email (with a plain-text fallback for old clients)
# ---------------------------------------------------------------------------
def send_html():
    html = """
    <html>
      <body>
        <h2 style="color:#0b5;">Hello 👋</h2>
        <p>This is an <b>HTML</b> email sent from <i>Python</i>.</p>
      </body>
    </html>
    """
    msg = MIMEMultipart("alternative")
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = "HTML Demo"
    msg.attach(MIMEText("Hello from Python! (plain text fallback)", "plain"))
    msg.attach(MIMEText(html, "html"))            # last part = preferred
    _send(msg)


# ---------------------------------------------------------------------------
# 3. Email with an attachment
# ---------------------------------------------------------------------------
def send_with_attachment(filename="abc.txt"):
    # Create a small demo file if it doesn't exist, so this runs out of the box.
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            f.write("This is a sample attachment created by email_automation.py\n")

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = "Attachment Demo"
    msg.attach(MIMEText("Please find the attached file.", "plain"))

    with open(filename, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={os.path.basename(filename)}",
    )
    msg.attach(part)
    _send(msg)


# ---------------------------------------------------------------------------
# 4. Retrieve emails via IMAP
# ---------------------------------------------------------------------------
def fetch_recent_emails(count=5, mailbox="INBOX"):
    """Print the subject / from / short body of the latest `count` emails."""
    with imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT) as imap:
        imap.login(SENDER_EMAIL, APP_PASSWORD)
        imap.select(mailbox)

        # Search all messages, then take the last `count` ids (newest).
        status, data = imap.search(None, "ALL")
        ids = data[0].split()
        latest = ids[-count:] if len(ids) >= count else ids

        print(f"\nLatest {len(latest)} email(s) in {mailbox}:")
        for num in reversed(latest):              # newest first
            status, msg_data = imap.fetch(num, "(RFC822)")
            message = __import__("email").message_from_bytes(msg_data[0][1])

            subject = _decode(message["Subject"])
            sender = _decode(message["From"])
            print(f"  • From: {sender}")
            print(f"    Subject: {subject}")
            print(f"    Body: {_body_preview(message)}\n")


def _decode(value):
    """Decode an email header that may be RFC 2047-encoded."""
    if not value:
        return ""
    text, enc = decode_header(value)[0]
    if isinstance(text, bytes):
        return text.decode(enc or "utf-8", errors="replace")
    return text


def _body_preview(message, limit=120):
    """Return the first bit of the plain-text body."""
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True) or b""
                return payload.decode(errors="replace").strip()[:limit]
        return ""
    payload = message.get_payload(decode=True) or b""
    return payload.decode(errors="replace").strip()[:limit]


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not APP_PASSWORD:
        raise SystemExit("Set GMAIL_APP_PASSWORD in your environment first.")

    print("Sending emails...")
    send_plain_text()
    send_html()
    send_with_attachment()

    # Read them back:
    fetch_recent_emails(count=5)

    print("\nDone.")
