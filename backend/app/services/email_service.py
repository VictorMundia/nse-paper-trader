# This imports smtplib, Python's built-in library for sending email over SMTP.
import smtplib

# This imports threading so email is sent in the background without slowing the request.
import threading

# This imports EmailMessage to build a properly formatted email.
from email.message import EmailMessage

# This imports current_app so we can read the mail settings.
from flask import current_app

# These are the settings copied out of the app, because the background thread has no app context.
MAIL_SETTING_KEYS = ("MAIL_SERVER", "MAIL_PORT", "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_SENDER")


def _deliver(settings, to_address, subject, body):
    """Send one email via SMTP, or print it to the console when no mail server is configured."""
    # Without a mail server (development), the email is printed so the flow can be tested.
    if not settings["MAIL_SERVER"]:
        # This prints the email clearly in the Flask console.
        print(f"\n===== [Email - console mode] =====\nTo: {to_address}\nSubject: {subject}\n\n{body}\n==================================\n")
        # This ends here in console mode.
        return
    # This builds the email.
    message = EmailMessage()
    # This sets the sender.
    message["From"] = settings["MAIL_SENDER"]
    # This sets the recipient.
    message["To"] = to_address
    # This sets the subject line.
    message["Subject"] = subject
    # This sets the plain-text body.
    message.set_content(body)
    # This guards the network call so a mail failure never crashes the server.
    try:
        # This connects to the mail server and closes the connection afterwards.
        with smtplib.SMTP(settings["MAIL_SERVER"], settings["MAIL_PORT"], timeout=20) as smtp:
            # STARTTLS encrypts the connection before the password is sent.
            smtp.starttls()
            # This logs in to the mail account.
            smtp.login(settings["MAIL_USERNAME"], settings["MAIL_PASSWORD"])
            # This sends the email.
            smtp.send_message(message)
    # This catches mail server errors and network errors.
    except (smtplib.SMTPException, OSError) as error:
        # This records the failure without revealing anything to the person who made the request.
        print(f"[Email] Failed to send to {to_address}: {error}")


def send_email_in_background(to_address, subject, body):
    """Send an email on a background thread so the HTTP response is not delayed."""
    # This copies the mail settings while we still have the app context.
    settings = {key: current_app.config.get(key) for key in MAIL_SETTING_KEYS}
    # daemon=True means a pending email never stops the server from shutting down.
    threading.Thread(target=_deliver, args=(settings, to_address, subject, body), daemon=True).start()
