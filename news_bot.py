import requests
import feedparser
from google import genai
import os
from datetime import datetime
import time

# ========== Config จาก GitHub Secrets ==========
LINE_CHANNEL_TOKEN = os.environ["LINE_CHANNEL_TOKEN"]
LINE_GROUP_ID = os.environ["LINE_GROUP_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

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

    client = genai.Client(api_key=GEMINI_API_KEY)

    headlines_text = "\n".join(f"- {h}" for h in headlines)
    prompt = f"""สรุปข่าวหมวด {category} ต่อไปนี้เป็นภาษาไทย กระชับ ไม่เกิน 3 ประเด็นหลัก
แต่ละประเด็นไม่เกิน 2 บรรทัด เขียนให้เข้าใจง่าย:

{headlines_text}"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text

def send_to_line(message):
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
    print(f"[{datetime.now()}] เริ่มรวบรวมข่าว...")
    today = datetime.now().strftime("%d/%m/%Y")

    header = f"📰 สรุปข่าวประจำวัน {today}\n{'='*30}"
    send_to_line(header)

    for category, feeds in RSS_FEEDS.items():
        print(f"  กำลังดึงข่าว: {category}")
        headlines = fetch_news(feeds)
        summary = summarize_with_ai(category, headlines)
        message = f"{category}\n{summary}"
        send_to_line(message)
        time.sleep(5)

    footer = f"{'='*30}\n🤖 สรุปโดย AI | {datetime.now().strftime('%H:%M')} น."
    send_to_line(footer)
    print(f"[{datetime.now()}] ส่งข่าวสำเร็จ!")

if __name__ == "__main__":
    build_and_send_news()
