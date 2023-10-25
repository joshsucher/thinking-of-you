import mailbox
from bs4 import BeautifulSoup
import json
import re

MBOX_PATH = 'vector_export.mbox'
OUTPUT_PATH = 'processed_emails.json'


def extract_first_name_from_email(email_string):
    email_string = str(email_string)  # Convert the Header object to a string
    name_part = email_string.split('<')[0].strip()
    names = name_part.split()
    if names:  # check if names are present
        return names[0].strip()
    return "Unknown"  # default name if not found

def remove_surnames_from_email_threads(email_body):
    pattern = re.compile(r"(On\s[^\n]+,\s)([^\s<]+) ([^\s<]+)(\s+<[^>]+>\s+wrote:)", re.IGNORECASE)
    email_body = pattern.sub(r"\1\2\4", email_body)
    return email_body


def remove_email_addresses(text):
    pattern = r"[\w\.-]+@[\w\.-]+"
    return re.sub(pattern, '', text)


def remove_replied_and_forwarded_content(text):
    pattern = re.compile(r"On\s[^\n]+,\s[^\n]+wrote:", re.IGNORECASE)
    return pattern.split(text)[0]


def preprocess_email_body(body):
    # If body content is just a filename or path, skip processing
    if len(body.split()) == 1 and ('/' in body or '.' in body):
        return body
    soup = BeautifulSoup(body, "lxml")
    text = soup.get_text()
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if not line.strip().startswith('>')]
    cleaned_text = ' '.join(cleaned_lines)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    return cleaned_text


def process_mbox_file(mbox_path):
    mbox = mailbox.mbox(mbox_path)
    sender_emails = {}
    total_messages = len(mbox)
    for idx, message in enumerate(mbox):
        if idx % 100 == 0:  # Print progress every 100 messages
            print(f"Processing message {idx + 1}/{total_messages}...")
            
        if message.is_multipart():
            part = message.get_payload(0)
            if part:
                body_content = part.get_payload(decode=True)
                if body_content:
                    body = body_content.decode(errors="ignore")
                else:
                    continue
            else:
                continue
        else:
            body_content = message.get_payload(decode=True)
            if body_content:
                body = body_content.decode(errors="ignore")
            else:
                continue

        sender_email = message['From']
        if sender_email:
            body = remove_surnames_from_email_threads(body)
            body = remove_email_addresses(body)
            body = remove_replied_and_forwarded_content(body)
            processed_body = preprocess_email_body(body)
            sender_first_name = extract_first_name_from_email(sender_email)
            if sender_first_name in sender_emails:
                sender_emails[sender_first_name].append(processed_body)
            else:
                sender_emails[sender_first_name] = [processed_body]

    print("Finished processing mbox file.")
    return sender_emails


if __name__ == "__main__":
    print("Starting mbox processing...")
    processed_emails = process_mbox_file(MBOX_PATH)
    print("Writing to JSON file...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(processed_emails, f, ensure_ascii=False, indent=4)
    print("Processing complete. Check the processed_emails.json file.")
