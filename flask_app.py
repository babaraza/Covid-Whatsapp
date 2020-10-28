from twilio.twiml.messaging_response import MessagingResponse
from flask import Flask, request
import covid_states
import covid_usa

app = Flask(__name__)

# List for checking State abbreviations
all_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY',
              'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND',
              'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']


@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    # Get the message the user sent to our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()

    try:
        # Handling the message the user sent i.e. body
        if body.upper() in all_states:
            # If the user texts a State abbreviation get data from covidtracking.com
            resp.message(covid_states.get_data(body))
        elif body.lower() == 'usa':
            # If the user texts USA get the data from Worldometer
            try:
                data, _ = covid_usa.get_results()
                resp.message(data)
            except Exception as e:
                print(e)
                resp.message(maintenance())

        else:
            resp.message('Stop messaging me, I am busy!')
    except Exception as e:
        print(e)

    return str(resp)


def maintenance():
    """
    Placeholder function to let users know when app is under maintenance
    :return: String message
    """
    message = 'I am Under Maintenance...'
    return message


if __name__ == "__main__":
    app.run(debug=False)
