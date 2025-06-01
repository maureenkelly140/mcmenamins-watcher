
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

        # Wait for the correct dropdown and select location
        try:
            page.wait_for_selector("select[name='hotelCode']", state="attached", timeout=20000)
        except Exception as e:
            print("WAIT FAILED:", e)
            page.screenshot(path="screenshot.png", full_page=True)
        
            import base64
            with open("screenshot.png", "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                print("SCREENSHOT_BASE64_START")
                print(encoded)
                print("SCREENSHOT_BASE64_END")
            raise  # Re-raise the exception so the job still fails (for now)
        
        page.click("a.sbSelector")
        page.wait_for_selector("ul.sbOptions li >> text=Edgefield", timeout=5000)
        page.click("ul.sbOptions li >> text=Edgefield")

        # Remove readonly and set check-in and check-out dates
        try:
            print("Waiting for arrival input field...")
            page.wait_for_selector("input[name='startDate']", state="attached", timeout=20000)
            print("Arrival field found. Removing readonly...")
            page.eval_on_selector("input[name='startDate']", "el => el.removeAttribute('readonly')")
            print("Filling arrival date...")
            page.fill("input[name='startDate']", CHECKIN_DATE)
        except Exception as e:
            print("Arrival field error:", e)
            page.screenshot(path="arrival-error.png", full_page=True)
            with open("arrival-error.png", "rb") as f:
                import base64
                encoded = base64.b64encode(f.read()).decode('utf-8')
                print("SCREENSHOT_BASE64_START")
                print(encoded)
                print("SCREENSHOT_BASE64_END")
            raise
            
        try:
            print("Waiting for departure input field...")
            page.wait_for_selector("input[name='endDate']", state="attached", timeout=20000)
            print("Departure field found. Removing readonly...")
            page.eval_on_selector("input[name='endDate']", "el => el.removeAttribute('readonly')")
            print("Filling departure date...")
            page.fill("input[name='endDate']", CHECKOUT_DATE)
        except Exception as e:
            print("Departure field error:", e)
            page.screenshot(path="departure-error.png", full_page=True)
            with open("departure-error.png", "rb") as f:
                import base64
                encoded = base64.b64encode(f.read()).decode('utf-8')
                print("SCREENSHOT_BASE64_START")
                print(encoded)
                print("SCREENSHOT_BASE64_END")
            raise

        # DEBUG: Log field values before search
        print("Checking field values before submit...")
        arrival_val = page.eval_on_selector("input[name='arrival']", "el => el.value")
        departure_val = page.eval_on_selector("input[name='departure']", "el => el.value")
        print("Arrival field value:", arrival_val)
        print("Departure field value:", departure_val)
        page.screenshot(path="before-submit.png", full_page=True)
        
        # Submit form
        try:
            print("Waiting for SEARCH button...")
            page.wait_for_selector("a#tbtAv", state="visible", timeout=20000)
            print("Clicking SEARCH button...")
            page.click("a#tbtAv", timeout=10000, force=True)
        except Exception as e:
            print("SEARCH button click error:", e)
            page.screenshot(path="submit-error.png", full_page=True)
            with open("submit-error.png", "rb") as f:
                import base64
                encoded = base64.b64encode(f.read()).decode('utf-8')
                print("SCREENSHOT_BASE64_START")
                print(encoded)
                print("SCREENSHOT_BASE64_END")
            raise

        # Wait a few seconds for results to load
        page.wait_for_timeout(5000)  # 5 seconds
        
        # Take screenshot whether or not results show up
        page.screenshot(path="after-search.png", full_page=True)
        with open("after-search.png", "rb") as f:
            import base64
            encoded = base64.b64encode(f.read()).decode('utf-8')
            print("RESULT_SCREENSHOT_BASE64_START")
            print(encoded)
            print("RESULT_SCREENSHOT_BASE64_END")
        
        # Try to wait for the results (this may still fail, but that's okay)
        page.wait_for_selector(".roomName", timeout=15000)

        room_names = page.locator(".roomName").all_inner_texts()

        browser.close()

        found = [room for room in room_names if any(k in room for k in ROOM_KEYWORDS)]

        if found:
            body = "Available room(s) found:\n" + "\n".join(found)
            send_email("Room Availability Alert - McMenamins", body)

if __name__ == "__main__":
    check_rooms()
