import requests
import feedparser
import anthropic
import os
import google.generativeai as genai
from datetime import datetime

# ========== Config จาก Environment Variables ==========
LINE_CHANNEL_TOKEN = os.environ["BPNlwZ0hti4g7INKeftA3P6Hs6Sr4J1IIpe3dyIr+iVkdpJWRak8O3tnfpKC3i9OEdcZBqEyRhhgFnmCDHuXoHtOncH3bu65f5u1zKFW3MuKfkWzCw0ZJS6l2HqT5O9T/BL5SsDCifaqagA0VopMJAdB04t89/1O/w1cDnyilFU="]
LINE_GROUP_ID = os.environ["LINE_GROUP_ID"]
GEMINI_API_KEY = os.environ["AIzaSyAJz1ATegdUJsz9C-09kTyK6P62kGfs-iQ"]

# ========== RSS Feed แหล่งข่าว ==========
RSS_FEEDS = {
    "🏛️ การเมืองไทย": [
        "https://www.thairath.co.th/rss/politics.xml",
        "https://www.matichon.co.th/feed",
    ],
    "📈 เศรษฐกิจ/หุ้น": [
        "https://www.bangkokbiznews.com/rss/data/bangkokbiznews-feed.xml",
        "https://feeds.bbci.co.uk/news/business/rss.xml",
    ],
    "💻 เทคโนโลยี/AI": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.theverge.com/rss/index.xml",
    ],
    "🌍 ต่างประเทศ": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    ],
    "⚽ กีฬา": [
        "https://feeds.bbci.co.uk/sport/rss.xml",
        "https://www.thairath.co.th/rss/sport.xml",
    ],
}

def fetch_news(feeds, max_per_feed=3):
    """ดึงข่าวจาก RSS Feed"""
    headlines = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_per_feed]:
                title = entry.get("title", "").strip()
                if title:
                    headlines.append(title)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return headlines[:8]

def summarize_with_ai(category, headlines):
    if not headlines:
        return "ไม่พบข่าวในหมวดนี้"
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    headlines_text = "\n".join(f"- {h}" for h in headlines)
    prompt = f"""สรุปข่าวหมวด {category} ต่อไปนี้เป็นภาษาไทย กระชับ ไม่เกิน 3 ประเด็นหลักแต่ละประเด็นไม่เกิน 2 บรรทัด เขียนให้เข้าใจง่าย:

{headlines_text}"""
    
    response = model.generate_content(prompt)
    return response.text

def send_to_line(message):
    """ส่งข้อความเข้า LINE กลุ่ม ผ่าน Messaging API"""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": LINE_GROUP_ID,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"LINE Response: {response.status_code} - {response.text}")
    return response.status_code == 200

def build_and_send_news():
    """ฟังก์ชันหลัก: รวบรวม สรุป และส่งข่าว"""
    print(f"[{datetime.now()}] เริ่มรวบรวมข่าว...")

    today = datetime.now().strftime("%d/%m/%Y")

    # ส่งหัวข้อก่อน
    header = f"📰 สรุปข่าวประจำวัน {today}\n{'='*30}"
    send_to_line(header)

    # ส่งทีละหมวด เพื่อไม่ให้เกิน limit ของ LINE
    for category, feeds in RSS_FEEDS.items():
        print(f"  กำลังดึงข่าว: {category}")
        headlines = fetch_news(feeds)
        summary = summarize_with_ai(category, headlines)
        message = f"{category}\n{summary}"
        send_to_line(message)

    # ส่งปิดท้าย
    footer = f"{'='*30}\n🤖 สรุปโดย AI | {datetime.now().strftime('%H:%M')} น."
    send_to_line(footer)

    print(f"[{datetime.now()}] ส่งข่าวสำเร็จ!")

if __name__ == "__main__":
    build_and_send_news()
