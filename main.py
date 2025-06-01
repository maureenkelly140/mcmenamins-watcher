
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from playwright.sync_api import sync_playwright

ROOM_KEYWORDS = [
    "Women's Hostel",
    "Twin w/common bath",
    "Queen w/common bath",
    "King w/common bath",
    "Double Queen w/common bath",
    "Queen Suite w/Private Bath",
    "King Suite w/Private Bath",
    "Family Room w/common bath"
]

CHECKIN_DATE = "09/18/2025"
CHECKOUT_DATE = "09/19/2025"
LOCATION = "Edgefield"

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = os.environ["EMAIL_USER"]
    msg["To"] = os.environ["EMAIL_TO"]
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["EMAIL_USER"], os.environ["EMAIL_PASS"])
        server.send_message(msg)

def check_rooms():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://reserve.mcmenamins.com/mcmenamins/availability.asp", wait_until="networkidle")

        # Wait for the location dropdown to be present in the DOM
        page.wait_for_selector("select[name='property']", state="attached", timeout=20000)
        page.select_option("select[name='property']", label=LOCATION)

        # Set check-in and check-out dates
        page.fill("input[name='arrival']", CHECKIN_DATE)
        page.fill("input[name='departure']", CHECKOUT_DATE)

        # Submit form
        page.click("input[type='submit']")

        page.wait_for_selector(".roomName", timeout=15000)
        room_names = page.locator(".roomName").all_inner_texts()

        browser.close()

        found = [room for room in room_names if any(k in room for k in ROOM_KEYWORDS)]

        if found:
            body = "Available room(s) found:\n" + "\n".join(found)
            send_email("Room Availability Alert - McMenamins", body)

if __name__ == "__main__":
    check_rooms()
