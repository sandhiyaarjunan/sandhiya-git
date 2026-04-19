from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

@shared_task
def send_async_invoice(email_data):
    html_content = render_to_string('emails/invoice_template.html', {'data': email_data})
    email = EmailMessage(
        subject="Your Purchase Invoice",
        body=html_content,
        from_email="billing@mallowtech.com",
        to=[email_data['customer_email']],
    )
    email.content_subtype = "html"
    email.send()