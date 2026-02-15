# Notification Integration Setup Guide

This guide walks through setting up Slack, Twilio (WhatsApp & SMS), and email integrations for AutoFinance notifications.

---

## 📱 Quick Start Summary

**Time to Complete:** 30-45 minutes

**What You'll Need:**
- Slack workspace (free)
- Twilio account (free trial: $15 credit)
- Email (optional - Gmail/SendGrid)

**End Result:** Multi-channel notifications from AutoFinance

---

## 🔵 Part 1: Slack Integration

### Step 1: Create Slack Bot Application

1. **Go to Slack API Dashboard**
   ```
   https://api.slack.com/apps
   ```

2. **Click "Create New App"**
   - Choose "From scratch"
   - App Name: `AutoFinance Bot`
   - Workspace: Select your workspace
   - Click "Create App"

### Step 2: Configure Bot Permissions

1. **In left sidebar, click "OAuth & Permissions"**

2. **Scroll to "Bot Token Scopes"**

3. **Add these scopes:**
   ```
   chat:write          - Send messages as bot
   chat:write.public   - Send to channels bot not in
   channels:read       - List public channels
   users:read          - Get user information
   files:write         - Upload images/files
   ```

4. **Scroll up and click "Install to Workspace"**

5. **Authorize the app**

6. **Copy the "Bot User OAuth Token"**
   - Starts with `xoxb-`
   - Keep this secret!

### Step 3: Invite Bot to Channel

1. **Open Slack app/web**

2. **Create or go to channel** (e.g., `#trading-alerts`)

3. **In channel, type:**
   ```
   /invite @AutoFinance Bot
   ```

### Step 4: Add Token to .env

1. **Open or create `.env` file in `mcp-servers/` directory:**
   ```bash
   cd ~/Documents/AutoFinance/mcp-servers
   nano .env
   ```

2. **Add this line:**
   ```bash
   SLACK_BOT_TOKEN=xoxb-your-token-here
   SLACK_DEFAULT_CHANNEL=#trading-alerts
   ```

3. **Save and exit** (Ctrl+X, Y, Enter)

### Step 5: Test Slack Integration

1. **Start notification-gateway MCP server:**
   ```bash
   cd ~/Documents/AutoFinance/mcp-servers/notification-gateway
   python server.py
   ```

2. **In another terminal, test with Python:**
   ```python
   import os
   from slack_sdk import WebClient
   
   token = os.getenv("SLACK_BOT_TOKEN")
   client = WebClient(token=token)
   
   response = client.chat_postMessage(
       channel="#trading-alerts",
       text="🚀 AutoFinance is online! Testing notification system..."
   )
   
   print("Message sent:", response["ok"])
   ```

3. **Check Slack channel** - you should see the test message!

### Slack Message Formats

**Simple Text:**
```python
send_slack_message(
    channel="#trading-alerts",
    message="Bitcoin price: $45,230"
)
```

**Alert with Formatting:**
```python
send_slack_alert(
    channel="#trading-alerts",
    title="🚨 Price Alert Triggered",
    message="BTC crossed $50,000 threshold",
    severity="critical"  # info, warning, critical
)
```

Severity colors:
- `info` → Green
- `warning` → Orange
- `critical` → Red

---

## 📞 Part 2: Twilio Integration (WhatsApp & SMS)

### Step 1: Create Twilio Account

1. **Go to Twilio:**
   ```
   https://www.twilio.com/try-twilio
   ```

2. **Sign up** (you get $15 free credit)

3. **Verify your email and phone number**

### Step 2: Get Twilio Credentials

1. **Go to Console Dashboard:**
   ```
   https://console.twilio.com/
   ```

2. **Find these values:**
   ```
   Account SID: AC...  (34 chars)
   Auth Token: ...     (32 chars)
   ```

3. **Keep these secret!**

### Step 3: Set Up WhatsApp Sandbox (For Testing)

1. **In Twilio Console, go to:**
   ```
   Messaging → Try it out → Send a WhatsApp message
   ```

2. **Follow instructions to join sandbox:**
   - Send WhatsApp message to Twilio number
   - Message format: `join <your-sandbox-code>`
   - Example: `join happy-elephant`

3. **Your phone is now connected to sandbox**

4. **Get your WhatsApp sandbox number:**
   ```
   Format: whatsapp:+14155238886
   ```

### Step 4: Get SMS Phone Number (Optional)

1. **In Twilio Console:**
   ```
   Phone Numbers → Manage → Buy a number
   ```

2. **Search for a number** (US numbers ~$1/month)

3. **Buy and note the number:**
   ```
   Format: +15551234567
   ```

### Step 5: Add Credentials to .env

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
TWILIO_AUTH_TOKEN=your_auth_token_32_chars_here

# WhatsApp (Sandbox for testing)
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# SMS (if you bought a number)
TWILIO_PHONE_FROM=+15551234567
```

### Step 6: Test Twilio Integration

**WhatsApp Test:**
```python
from twilio.rest import Client

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

message = client.messages.create(
    from_='whatsapp:+14155238886',  # Twilio sandbox
    to='whatsapp:+1YOUR_PHONE',      # Your verified phone
    body='🚀 AutoFinance WhatsApp notifications are working!'
)

print(f"WhatsApp sent: {message.sid}")
```

**SMS Test:**
```python
message = client.messages.create(
    from_='+15551234567',        # Your Twilio number
    to='+1YOUR_PHONE',           # Your phone
    body='AutoFinance SMS test!'
)

print(f"SMS sent: {message.sid}")
```

### Important Twilio Notes

**Free Trial Limitations:**
- SMS: Can only send to verified phone numbers
- WhatsApp: Must use sandbox (join code required)
- $15 credit = ~500 SMS or ~300 WhatsApp messages

**Production Setup:**
- Upgrade account for unrestricted sending
- Apply for WhatsApp Business API (takes 1-2 weeks)
- Buy dedicated phone numbers

**Message Costs:**
- SMS: ~$0.0075 per message (US)
- WhatsApp: ~$0.005 per message session

---

## 📧 Part 3: Email Integration (Optional)

### Option A: Gmail SMTP (Easy, but less reliable)

1. **Enable 2-Factor Authentication** on your Gmail account

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other"
   - Name it "AutoFinance"
   - Copy the 16-character password

3. **Add to .env:**
   ```bash
   EMAIL_SMTP_SERVER=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_FROM=your.email@gmail.com
   EMAIL_PASSWORD=your_app_password_16_chars
   ```

4. **Test:**
   ```python
   import smtplib
   from email.mime.text import MIMEText
   
   msg = MIMEText("AutoFinance email test!")
   msg['Subject'] = 'Test Email'
   msg['From'] = 'your.email@gmail.com'
   msg['To'] = 'recipient@example.com'
   
   with smtplib.SMTP('smtp.gmail.com', 587) as server:
       server.starttls()
       server.login('your.email@gmail.com', 'app_password')
       server.send_message(msg)
   ```

### Option B: SendGrid (Recommended for production)

1. **Sign up:** https://signup.sendgrid.com/

2. **Create API Key:**
   - Settings → API Keys → Create API Key
   - Full Access
   - Copy key (starts with `SG.`)

3. **Add to .env:**
   ```bash
   SENDGRID_API_KEY=SG.your_key_here
   EMAIL_FROM=noreply@yourdomain.com
   ```

4. **Install package:**
   ```bash
   pip install sendgrid
   ```

5. **Test:**
   ```python
   from sendgrid import SendGridAPIClient
   from sendgrid.helpers.mail import Mail
   
   message = Mail(
       from_email='noreply@yourdomain.com',
       to_emails='recipient@example.com',
       subject='AutoFinance Test',
       html_content='<strong>Email notifications working!</strong>'
   )
   
   sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
   response = sg.send(message)
   print(f"Email sent: {response.status_code}")
   ```

---

## 🧪 Complete Integration Test

Once everything is set up, test all channels:

```python
# Test script: test_notifications.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test 1: Slack
print("Testing Slack...")
from slack_sdk import WebClient
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
slack_response = client.chat_postMessage(
    channel="#trading-alerts",
    text="✅ Slack working"
)
print(f"Slack: {'✓' if slack_response['ok'] else '✗'}")

# Test 2: WhatsApp
print("\nTesting WhatsApp...")
from twilio.rest import Client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
whatsapp_response = twilio_client.messages.create(
    from_=os.getenv("TWILIO_WHATSAPP_FROM"),
    to='whatsapp:+1YOUR_PHONE',
    body='✅ WhatsApp working'
)
print(f"WhatsApp: ✓ (SID: {whatsapp_response.sid})")

# Test 3: SMS (if configured)
if os.getenv("TWILIO_PHONE_FROM"):
    print("\nTesting SMS...")
    sms_response = twilio_client.messages.create(
        from_=os.getenv("TWILIO_PHONE_FROM"),
        to='+1YOUR_PHONE',
        body='✅ SMS working'
    )
    print(f"SMS: ✓ (SID: {sms_response.sid})")

print("\n✅ All notification channels tested!")
```

**Run the test:**
```bash
cd ~/Documents/AutoFinance/mcp-servers
python test_notifications.py
```

You should receive messages on all configured channels!

---

## 🔒 Security Best Practices

### Never Commit Secrets

1. **Ensure .env is in .gitignore:**
   ```bash
   echo ".env" >> .gitignore
   echo "**/.env" >> .gitignore
   ```

2. **Check before committing:**
   ```bash
   git status
   # .env should NOT appear
   ```

3. **Use .env.example for templates:**
   ```bash
   # .env.example (commit this)
   SLACK_BOT_TOKEN=xoxb-YOUR-TOKEN-HERE
   TWILIO_ACCOUNT_SID=ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   TWILIO_AUTH_TOKEN=your_auth_token_here
   ```

### Secret Rotation

- **Slack bot token:** Regenerate in Slack API dashboard
- **Twilio credentials:** Rotate in Twilio Console → API credentials
- **Do this if:** Token leaked, employee leaves, suspicious activity

---

## 🚀 Production Deployment Considerations

### Slack

**For Production:**
- [ ] Submit app for workspace distribution
- [ ] Add proper app icon and description
- [ ] Configure OAuth redirect URLs
- [ ] Set up slash commands (e.g., `/autofinance help`)
- [ ] Add interactive components (buttons)

### Twilio

**For Production:**
- [ ] Upgrade from trial account ($20 minimum)
- [ ] Apply for WhatsApp Business API access
- [ ] Buy dedicated phone numbers
- [ ] Set up A2P 10DLC registration (for high-volume SMS)
- [ ] Configure delivery webhooks

### Email

**For Production:**
- [ ] Use dedicated email service (SendGrid, AWS SES)
- [ ] Set up SPF, DKIM, DMARC records
- [ ] Monitor deliverability rates
- [ ] Handle bounces and complaints
- [ ] Rate limiting (don't spam)

---

## 📊 Usage Monitoring

### Track Notification Metrics

```python
# In your notification-gateway server
notification_metrics = {
    "slack_sent": 0,
    "slack_failed": 0,
    "whatsapp_sent": 0,
    "whatsapp_failed": 0,
    "sms_sent": 0,
    "sms_failed": 0
}

# Increment after each send
# Log daily/weekly
```

### Set Up Alerts (Meta!)

- Get notified if notification system fails
- Monitor Twilio balance (alert when <$5 remaining)
- Track Slack API rate limits

---

## 🆘 Troubleshooting

### Slack Issues

**Problem:** "not_in_channel" error
```
Solution: /invite @AutoFinance Bot in the channel
```

**Problem:** "invalid_auth" error
```
Solution: 
1. Check token starts with xoxb-
2. Regenerate token in Slack API dashboard
3. Update .env file
4. Restart server
```

**Problem:** Messages not formatting correctly
```
Solution: Use blocks format, not just text
See: https://api.slack.com/block-kit
```

### Twilio Issues

**Problem:** "Cannot send to unverified number"
```
Solution: On trial, you can only send to verified numbers
1. Go to Twilio Console → Phone Numbers → Verified Caller IDs
2. Add your phone number
or
Upgrade account
```

**Problem:** WhatsApp "join code" expired
```
Solution: Get new code from Twilio Console → WhatsApp Sandbox
Send new join message
```

**Problem:** High costs
```
Solution:
1. Monitor usage in Twilio Console
2. Set spending limits
3. Throttle notifications (max 1/minute per user)
```

### Email Issues

**Problem:** Gmail SMTP "Less secure app" error
```
Solution: Use App Passwords, not account password
Enable 2FA first
```

**Problem:** Emails going to spam
```
Solution:
1. Use dedicated service like SendGrid
2. Set up SPF/DKIM/DMARC
3. Warm up sending reputation
4. Avoid spam trigger words
```

---

## ✅ Integration Checklist

- [ ] Slack bot created and installed
- [ ] Slack bot invited to #trading-alerts channel
- [ ] SLACK_BOT_TOKEN added to .env
- [ ] Twilio account created
- [ ] Phone number verified with Twilio
- [ ] WhatsApp sandbox joined
- [ ] TWILIO_ACCOUNT_SID and AUTH_TOKEN in .env
- [ ] Test notifications sent successfully
- [ ] .env file in .gitignore
- [ ] .env.example created for teammates
- [ ] All MCP servers can load environment variables
- [ ] Notification logs being written to compliance server

---

## 🎯 For Hackathon Demo

**Minimum Required:**
- ✅ Slack integration (easiest to demo)
- ⚪ WhatsApp (nice to have, but sandbox has friction)
- ⚪ SMS (optional)
- ⚪ Email (optional)

**Demo Strategy:**
1. Focus on Slack (most visual, easiest to show)
2. Mention multi-channel capability
3. Show code/architecture diagram
4. Have screenshots of WhatsApp/SMS if not live

**Time Budget:**
- Slack setup: 15 minutes
- Twilio setup: 30 minutes (if including WhatsApp)
- Testing: 15 minutes

**If short on time:** Do Slack only. It's enough to show capability.

---

## 📚 Additional Resources

**Slack:**
- Block Kit Builder: https://app.slack.com/block-kit-builder
- API Documentation: https://api.slack.com/docs
- Python SDK: https://slack.dev/python-slack-sdk/

**Twilio:**
- WhatsApp API: https://www.twilio.com/docs/whatsapp
- SMS API: https://www.twilio.com/docs/sms
- Python SDK: https://www.twilio.com/docs/libraries/python

**Email:**
- SendGrid Docs: https://docs.sendgrid.com/
- SMTP Guide: https://realpython.com/python-send-email/

---

**Need help? Check the troubleshooting section or create an issue in the GitHub repo.**

Happy notifying! 🚀
