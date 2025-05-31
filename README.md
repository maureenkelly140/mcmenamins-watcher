
# McMenamins Room Watcher

This script monitors room availability on the McMenamins Edgefield reservation page for specific dates and room types.

## How It Works
- Uses Playwright to navigate the reservation form
- Searches for your chosen room types
- Sends an email if a match is found

## Setup

1. Create a Gmail App Password at https://myaccount.google.com/apppasswords
2. Set the following environment variables on Render:
   - `EMAIL_USER`: Your Gmail address
   - `EMAIL_PASS`: Your Gmail App Password
   - `EMAIL_TO`: Your notification email

## Deployment on Render

1. Push this folder to a new GitHub repository
2. Create a new **cron job** service on Render
3. Connect it to your GitHub repo
4. Set your environment variables
5. Done! The script will run daily and notify you if a match is found
