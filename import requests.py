import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

GROUP_ID = os.getenv("GROUP_ID")  # Access group ID
ACCOUNT_ID = os.getenv("ACCOUNT_ID")  # Account ID
API_KEY = os.getenv("API_KEY")  # API key or token
AUTH_EMAIL = os.getenv("AUTH_EMAIL")  # Account email


def get_emails_in_access_group(ACCOUNT_ID, GROUP_ID):
    endpoint = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/groups/{GROUP_ID}"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Email": AUTH_EMAIL,  # Add your Cloudflare account email here
        "X-Auth-Key": API_KEY,  # Add your Cloudflare API key here
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
        if valid_email in existing_emails:
            print("email is already in list")
            return
        new_emails = existing_emails + [valid_email]
        endpoint = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/groups/{GROUP_ID}"
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": AUTH_EMAIL,  # Add your Cloudflare account email here
            "X-Auth-Key": API_KEY,  # Add your Cloudflare API key here
        }
        payload = {
            "include": [{"email": {"email": email}} for email in new_emails],
            # "is_default": True,
            # "name": "Allow devs",
            # "require": [{"email": {"email": email}} for email in new_emails],
        }
        response = requests.put(endpoint, headers=headers, json=payload)
        return response.json()
    else:
        return {"error": "Failed to retrieve existing emails from the access group."}


def remove_email_from_access_group(ACCOUNT_ID, GROUP_ID, valid_email):
    existing_emails = get_emails_in_access_group(ACCOUNT_ID, GROUP_ID)
    if existing_emails and valid_email in existing_emails:

        if existing_emails.count(1) == 0:
            print(existing_emails.count(1))
            print("Must have at least one email")
            exit

        existing_emails.remove(valid_email)
        endpoint = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/access/groups/{GROUP_ID}"
        headers = {
            "Content-Type": "application/json",
            "X-Auth-Email": AUTH_EMAIL,  # Add your Cloudflare account email here
            "X-Auth-Key": API_KEY,  # Add your Cloudflare API key here
        }
        payload = {
            "include": [{"email": {"email": email}} for email in existing_emails],
            # "is_default": True,
            # "name": "Allow devs",
            # "require": [{"email": {"email": email}} for email in existing_emails],
        }
        response = requests.put(endpoint, headers=headers, json=payload)
        return response.json()
    elif existing_emails:
        print("Email not found")
        return {"error": f"Email '{valid_email}' not found in the access group."}
    else:
        print("Could not retrieve access group")
        return {"error": "Failed to retrieve existing emails from the access group."}


regex = "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"

# Example usage:
# account_identifier = "b2bace02efaf443d130cf5b5ddf4ec33"
# group_uuid = "f456f44c-55ee-409b-a85e-cf1e303f5e38"
email = input("Enter email: ")

regex_search = email = re.search(regex, email)

if regex_search:
    valid_email = regex_search.group()

    # Add a new email
    # add_response = add_email_to_access_group(
    #     account_identifier, group_uuid, valid_email
    # )

    # Remove an email
    remove_response = remove_email_from_access_group(ACCOUNT_ID, GROUP_ID, valid_email)

else:
    print("Not a valid email")

emails = get_emails_in_access_group(ACCOUNT_ID, GROUP_ID)
print("\nCurrent emails in list: ")
for email in emails:
    print(email)
