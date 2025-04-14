import traceback
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from datetime import datetime,timedelta

##################### send html rendered email
# send attachment email
def send_attachment_email(subject, string, file_path, to_email, file_name):
    try:
    # from_email = settings.EMAIL_HOST_USER
        from_email = f'JD <{settings.EMAIL_HOST_USER}>'
        email_msg = EmailMultiAlternatives(subject, string ,from_email, to_email)
        if file_path:
            attachment = open(file_path, 'rb')
            email_msg.attach(file_name, attachment.read() , 'application/pdf')
        email_msg.attach_alternative(string, "text/html")
        email_msg.send() 
        return "success"
    except Exception as e:
        print(str(traceback.format_exc()))
    return "error"


### send email with html
def send_html_email(subject, html_content, to_email, pdf_path=None,pdf_file=None):
    try:
        send_email_to = None
        if type(to_email) == list:
            send_email_to = to_email
        else:
            send_email_to = [to_email]

        for email in send_email_to:
            from_email = f'JD College <{settings.EMAIL_HOST_USER}>'
            email_msg = EmailMultiAlternatives(subject, html_content, from_email, [email])

            # Attach HTML content
            email_msg.attach_alternative(html_content, "text/html")

            if pdf_path:
                # Attach PDF file	
                with open(pdf_path, 'rb') as pdf_file:
                    email_msg.attach(pdf_file.name, pdf_file.read(), 'application/pdf')
            email_msg.send()
        
        return "success"
    except Exception as e:
        print(str(traceback.format_exc()))
        return "error"
	



#################### send normal email
def send_htmlfile_email(subject, string, to_email_list):
	try:
		from_email = settings.EMAIL_HOST_USER
		email_msg = EmailMultiAlternatives(
        subject, string, from_email=from_email, to=[to_email_list])
		# email_msg.attach_alternative(string, "website/email_rts/Verification_code.html")
		email_msg.mixed_subtype = 'related'
		email_msg.send()
		return	"success"
	except:
		traceback.print_exc()
		return "error"

def send_normal_email(subject,message,to_email_list):
    try:
        from_email = settings.EMAIL_HOST_USER
        send_mail(subject, message, from_email, [to_email_list])
        return "success"
    except:
          traceback.print_exc()
          return "error"


