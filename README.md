# Karuta-google-sheet

# Set up

* Copy the .env-template as .env
* Fill in the secrets listed in the .env **(the google_json should be the json generated for a service [account](https://pygsheets.readthedocs.io/en/stable/authorization.html))**

# Start
To start the app type python bot.py

# Commands

zop kc - will parse the above kc and enter the first entry into the google sheet

zop kcall - will parse the above kc and enter all of the entries on the page into the google sheet.

zop wi <card-code> - will parse the above kwi and will enter the work stats on the row where the card-code is found. (should be done after card is entered in the sheet from a zop kc)
  
zop lu - will parse the above klu and will enter the card stats into the spreadsheet

zop sb - will parse the cards listed above and remove them from the spreadsheet. (Should be done before burning cards if you do not want burned cards in the spreadsheet)
