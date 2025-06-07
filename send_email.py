import json
import smtplib
import getpass
import argparse
import time
import markdown
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

def load_data(json_file):
    """Load participants data from JSON file"""
    with open(json_file, 'r') as f:
        return json.load(f)

def send_email(sender_email, password, recipient, cc_list, subject, body, use_markdown=True):
    """Send email using Office 365 SMTP"""
    msg = MIMEMultipart()
    msg['From'] = formataddr(("GrifflesCTF Admin", sender_email))
    msg['To'] = recipient
    if cc_list:
        msg['Cc'] = ", ".join(cc_list)
    msg['Subject'] = subject
    
    if use_markdown:
        # Convert markdown to HTML
        html_body = markdown.markdown(body)
        msg.attach(MIMEText(html_body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()
        server.login(sender_email, password)
        
        recipients = [recipient] + (cc_list if cc_list else [])
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        print(f"✅ Email sent successfully to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Error sending email to {recipient}: {e}")
        return False

def generate_email_body(team_name, username, password, platform_link, team_password):
    """Generate personalized email body with markdown formatting"""
    body = f"""Hallooooooo GrifflesCTF2025 Participants!

## GrifflesCTF 2025 credentials are ready! 🎉

**You'll find your login details below:**

* **Team Name:** {team_name}
* **Username:** {username}
* **Password:** {password}
* **Team Password:** {team_password}

Keep these safe and handy — you'll need them to access the CTF platform once the competition kicks off!
You can also try to log in to the platform via the link below! If you encounter any issues, please reach out to us via the Discord server's tickets.

**GrifflesCTF Platform link:** [{platform_link}]({platform_link})

## Important Reminders

* **We will be conducting an IMPORTANT BRIEFING on Friday at 8.45 AM.** Please join the #General Stage channel in the Discord Server to listen in!

* If you haven't joined our official GrifflesCTF 2025 Discord server yet, please do so ASAP! It's where we'll be posting announcements, updates, and it'll be the only way to reach support during the CTF. Join us here: [https://discord.gg/CGKhntjTYa](https://discord.gg/CGKhntjTYa)

* Don't forget to remind your groupmates to hop in if they haven't joined yet, as this discord channel will be the only way to contact us, receive updates or to ask for support during the competition.

We can't wait to see you in action this Friday!

Best Regards,  
GrifflesCTF Admin"""
    return body

def main():
    parser = argparse.ArgumentParser(description='Send CTF credentials via email')
    parser.add_argument('--json', default='data.json', help='Path to the JSON data file')
    parser.add_argument('--sender', help='Sender email address (Office 365 account)')
    parser.add_argument('--cc', nargs='+', help='CC email addresses')
    parser.add_argument('--platform-link', default='', help='CTF platform URL')
    parser.add_argument('--test', action='store_true', help='Test mode (no emails sent)')
    parser.add_argument('--filter-team', help='Send only to specific team')
    parser.add_argument('--filter-email', help='Send only to specific email')
    parser.add_argument('--delay', type=int, default=2, help='Delay between emails in seconds')
    parser.add_argument('--plain-text', action='store_true', help='Send emails in plain text (no markdown)')
    args = parser.parse_args()
    
    # Load participant data
    data = load_data(args.json)
    
    # Get Office 365 credentials if not in test mode
    if not args.test:
        if not args.sender:
            args.sender = input("Enter your Office 365 email address: ")
        password = getpass.getpass("Enter your Office 365 password: ")
    
    # Count eligible users
    total_users = 0
    for team in data:
        if args.filter_team and team['team'] != args.filter_team:
            continue
        for user in team['users']:
            if args.filter_email and user[1] != args.filter_email:
                continue
            total_users += 1
    
    print(f"📋 Found {total_users} users to process")
    
    # Process each team and user
    processed_count = 0
    for team in data:
        if args.filter_team and team['team'] != args.filter_team:
            continue
        
        team_name = team['team']
        team_password = team['teampwd']
        print(f"\n🔄 Processing team: {team_name}")
        
        for user in team['users']:
            if args.filter_email and user[1] != args.filter_email:
                continue
            
            username = user[0]
            email = user[1]
            user_password = user[2]
            
            print(f"  📧 Processing: {username} ({email})")
            
            subject = f"GrifflesCTF 2025 Credentials for {username}"
            body = generate_email_body(team_name, username, user_password, args.platform_link, team_password)
            
            if not args.test:
                success = send_email(args.sender, password, email, args.cc, subject, body, not args.plain_text)
                if success:
                    processed_count += 1
                time.sleep(args.delay)  # Add delay to avoid rate limiting
            else:
                print("  [TEST] Email would be sent with the following details:")
                print(f"    To: {email}")
                if args.cc:
                    print(f"    CC: {', '.join(args.cc)}")
                print(f"    Subject: {subject}")
                print(f"    Format: {'Plain text' if args.plain_text else 'HTML (from Markdown)'}")
                print(f"    Body preview: {body[:60]}...")
                processed_count += 1
    
    print(f"\n✅ Processed {processed_count}/{total_users} users successfully")

if __name__ == "__main__":
    main()