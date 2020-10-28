from utilities.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_TO, TWILIO_WHATSAPP_FROM, TWILIO_SMS_FROM, TWILIO_SMS_TO
from twilio.rest import Client


def send_sms(msg):
    """
    Send regular SMS message
    """

    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to=TWILIO_SMS_TO,
        from_=TWILIO_SMS_FROM,
        body=msg
    )

    print(f'Message SID: {message.sid}')


def send_whatsapp(msg, **kwargs):
    """
    Send WhatsApp message
    """

    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        from_=TWILIO_WHATSAPP_FROM,
        to=TWILIO_WHATSAPP_TO,

        # The text of the message
        body=msg,

        # To send image (media_url=["https://demo.twilio.com/owl.png"])
        media_url=kwargs.get('media'),

        # To send map (persistent_action=['geo:37.787890,-122.391664|375 Beale St'])
        persistent_action=kwargs.get('map')
    )

    print(f'Message Sent: {message.sid}')


if __name__ == '__main__':
    # send_sms("This is a test...")
    send_whatsapp("This is *bold* and _italics_.")
