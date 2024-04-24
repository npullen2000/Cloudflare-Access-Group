import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

GROUP_ID = os.getenv(
    "GROUP_ID"
)  # Access Group ID found at https://one.dash.cloudflare.com/
ACCOUNT_ID = os.getenv(
    "ACCOUNT_ID"
)  # https://developers.cloudflare.com/fundamentals/setup/find-account-and-zone-ids/

API_KEY = os.getenv(
    "API_KEY"
)  # API key or Token found at https://dash.cloudflare.com/profile/api-tokens

AUTH_EMAIL = os.getenv(
    "AUTH_EMAIL"
)  # Account Email found at https://dash.cloudflare.com/profile


def get_emails_in_access_group(ACCOUNT_ID, GROUP_ID):
    endpoint = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/groups/{GROUP_ID}"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Email": AUTH_EMAIL,
        "X-Auth-Key": API_KEY,
    }

    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        data = response.json()
        include_emails = [item["email"]["email"] for item in data["result"]["include"]]
        return include_emails
    else:
        return None


def add_email_to_access_group(ACCOUNT_ID, GROUP_ID, valid_email):
    existing_emails = get_emails_in_access_group(ACCOUNT_ID, GROUP_ID)
    if existing_emails:
        # checks if email already exists in Access Group
        if valid_email in existing_emails:
            print("email is already in list")
            return
        new_emails = existing_emails + [valid_email]
        endpoint = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/groups/{GROUP_ID}"
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": AUTH_EMAIL,
            "X-Auth-Key": API_KEY,
        }
        payload = {
            "include": [{"email": {"email": email}} for email in new_emails],
            # ------------------------
            # Additional options based on your needs
            # ------------------------
            # "is_default": True,
            # "name": "Allow devs",
            # "require": [{"email": {"email": email}} for email in new_emails],
            # ------------------------
        }
        response = requests.put(endpoint, headers=headers, json=payload)
        return response.json()
    else:
        return {"error": "Failed to retrieve existing emails from the access group."}


def remove_email_from_access_group(ACCOUNT_ID, GROUP_ID, valid_email):
    existing_emails = get_emails_in_access_group(ACCOUNT_ID, GROUP_ID)
    if existing_emails and valid_email in existing_emails:
        # Ensures that user is not attempting to delete the last email in list.
        # Access groups require at least one [1] include statment
        if existing_emails.count(1) == 0:
            print(existing_emails.count(1))
            print("Must have at least one email")
            exit

        existing_emails.remove(valid_email)
        endpoint = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/groups/{GROUP_ID}"
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": AUTH_EMAIL,
            "X-Auth-Key": API_KEY,
        }
        payload = {
            "include": [{"email": {"email": email}} for email in existing_emails],
            # ------------------------
            # Additional options based on your needs
            # ------------------------
            # "is_default": True,
            # "name": "Allow devs",
            # "require": [{"email": {"email": email}} for email in new_emails],
            # ------------------------
        }
        response = requests.put(endpoint, headers=headers, json=payload)
        return response.json()
    elif existing_emails:
        return {"error": f"Email '{valid_email}' not found in the access group."}
    else:
        print("Could not retrieve access group")
        return {"error": "Failed to retrieve existing emails from the access group."}


regex = "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"  # Email regex
email = input("Enter email: ")

regex_search = email = re.search(regex, email)  # Verifies input to regex

if regex_search:
    valid_email = regex_search.group()  # plaintext after regex verification

    # Add a new email
    add_response = add_email_to_access_group(
        ACCOUNT_ID, GROUP_ID, valid_email
    )  # comment out if not needed

    # Remove an email
    remove_response = remove_email_from_access_group(
        ACCOUNT_ID, GROUP_ID, valid_email
    )  # comment out if not needed

else:
    print("Not a valid email")

# prints updated list of emails
emails = get_emails_in_access_group(ACCOUNT_ID, GROUP_ID)
print("\nCurrent emails in list: ")
for email in emails:
    print(email)
