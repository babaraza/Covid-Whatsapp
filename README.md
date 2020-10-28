[![Python 3.7](https://img.shields.io/badge/Python-3.6-blue.svg)](https://www.python.org/downloads/release/python-374/)
![GitHub](https://img.shields.io/github/license/babaraza/Covid-Whatsapp)



# Covid-WhatsApp

Get Covid19 data and send to user via **WhatsApp** or **SMS**



#### Technologies used

* Firebase Firestore for Database

* Flask for local server running on Raspberry Pi

* NGROK *(optional)* for exposing local Flask server to internet

* Twilio for WhatsApp messaging

* BeautifulSoup for scraping

* LXML as a parser for BeautifulSoup

  

#### Features

* Gets total number of deaths and cases

* Gets number of new cases and deaths

* **Two Approaches:**

  * Save data to a local `covid-data.txt` file

  * Save data to Firestore database with Firebase

  * This helps comparing the new retrieved data from the old one in the file or database

    

#### Usage

- Script can be deployed on a Raspberry Pi 
  - User can setup `ngrok` to accept incoming messages sent to their `twilio` number
    - On `twilio` dashboard, a `webhook` can be set to the `ngrok` url that gets triggered on every incoming message
    - The `webhook` will have the endpoint `/sms` 
  - User can then setup a `flask` server to listen on the `ngrok` url with the `/sms` endpoint and route accordingly
- Script accepts from **WhatsApp** or **SMS**:
  - Any State in USA as abbreviated text, example: `TX` for Texas
  - User can also send in `usa` to get the data for `USA` as well as two counties in Texas; **Fort Bend County** and **Harris County**
- Script will then return the results via **WhatsApp** or **SMS**



##### The script requires the following environment variables

| Environment Variable Name | Example                 | Notes                                                        |
| ------------------------- | ----------------------- | ------------------------------------------------------------ |
| TWILIO_ACCOUNT_SID        | *from Twilio dashboard* | The Session ID from TWILIO                                   |
| TWILIO_AUTH_TOKEN         | *from Twilio dashboard* | The Auth Token from TWILIO                                   |
| TWILIO_SMS_TO             | +12815555555            | The phone number to send the SMS to. *Make sure to include the area-code* |
| TWILIO_SMS_FROM           | +12815555555            | The phone number to send the SMS from (from TWILIO). *Make sure to include the area-code* |
| TWILIO_WHATSAPP_FROM      | whatsapp:+12815555555   | The phone number to send the WhatsApp message from (from TWILIO). *Make sure to include the area-code* and `whatsapp:` |
| TWILIO_WHATSAPP_TO        | whatsapp:+12815555555   | The phone number to send the WhatsApp to. *Make sure to include the area-code and `whatsapp:`* |
| PROJECT_ID                | *from firebase*         | The name of the firebase project                             |
| COLLECTION_NAME           | *from firebase*         | The name of the database collection to store the Covid19 data to |



##### The script also requires the Firebase config file (json) 

* You can get this config directly from Firebase
* Put this file in the main project directory
* Make sure the file name for this config file is `fbapp.json`
