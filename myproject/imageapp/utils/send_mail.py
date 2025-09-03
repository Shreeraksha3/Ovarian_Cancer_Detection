
import smtplib
from email.message import EmailMessage
import os

my_mail = "raksha2004ch@gmail.com"
my_password = "jpwb foup wmmh olun"

def send_email(subject, recipient_email, template_path, context):
    """
    Send an HTML email to the recipient using a template and context.
    """
    # Ensure the template path exists
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Email template not found: {template_path}")

    # Load and format the email template
    with open(template_path, 'r') as file:
        html_content = file.read()

    # Replace placeholders in the template
    for key, value in context.items():
        html_content = html_content.replace(f"{{{{ {key} }}}}", str(value))

    # Create the email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = my_mail
    msg['To'] = recipient_email
    msg.set_content("This is a fallback plain text message.")
    msg.add_alternative(html_content, subtype='html')  # HTML content

    # Send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(my_mail, my_password)
            server.send_message(msg)
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
        raise e
