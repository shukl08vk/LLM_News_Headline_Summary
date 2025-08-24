import requests
import os
from dotenv import load_dotenv
from transformers import pipeline
from google import genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

load_dotenv()
#print(os.getcwd())
email=os.getenv("EMAIL")
password=os.getenv("PASSWORD")
gem_api_key=os.getenv("GEM_API_KEY")
gnews_api_key=os.getenv("GNEWS_API_KEY")

# Function to get top headline from India using Gnews Api 
def get_news_from_api():

    url = (f'https://gnews.io/api/v4/top-headlines?country=in&lang=en&apikey={gnews_api_key}')
    print(url)
    response = requests.get(url)
    if response.status_code==200:
        data=response.json()
        articles=data.get('articles',[])
        text=''''''
        for idx,article in enumerate(articles,start=1):
            text+=f'''{idx} -> {article["title"]}'''
            text+=f''' \t  description: {article['description']}\t'''
            text+=f''' \t  URL: {article['url']}\n'''
            #print(f"   URL: {article['url']}\n")
        print(type(text))
        return text
    else:
        print('error:',response.status_code,response.text)

'''
def summarize_news_llm():
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    text = get_news_from_api()
    print(type(text))
    summary = summarizer(text, max_length=100, min_length=30, do_sample=False)
    print(summary)
'''
#Function to send email for summarized top News headlines
def send_email(subject, body, sender_email, receiver_email, app_password):
    # Create the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    body1='Hello, Good Morning! \n\n'
    if isinstance(body, list):  
        body2= "\n\n".join(body)
    body3='Thanks & Regards,\n Daily New Corp'
    body=body1+body2+body3
    # Attach body as plain text
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure connection

        server.login(sender_email, app_password)  # Use app password
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(" Email sent successfully!")
    except Exception as e:
        print(" Error:", str(e))

# Function to set up Google Gemini setup to use LLM to summarize and properly format the new headlines received from new API
def google_api():
    client = genai.Client(api_key=gem_api_key)
    print(client,'gemini')
    text = get_news_from_api()
    prompt = f"""
    Here is the given text having top news headlines: {text}.
    Provide a brief summary of each news headlines in this exact JSON format:
    {{
        "Subject": "Daily News Briefing: Top Headlines Today",
        "Body": [
            "Headline - Summary (URL)",
            "Headline - Summary (URL)"
        ]
    }}
    IMPORTANT: Return only valid JSON, no extra text.
    """
    response = client.models.generate_content(
    model="gemini-2.5-flash", contents=prompt)
    raw_text = response.text.strip()
    #print(raw_text)
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("```json").strip("```").strip()
    text_dict = json.loads(raw_text)
    return text_dict
    
 
#summarize_news_llm()
#get_news_from_api()
text=google_api()
#print(type(text))
#print(text)
send_email(text['Subject'],text['Body'],email,email,password)