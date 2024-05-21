from unittest import TestCase

from codes.mail import EmailMessage


class TestEmail(TestCase):
    def test_send_mail(self):
        """can not run, need fill data"""
        data = []
        email_message = EmailMessage(*data)
        email_message.send()
