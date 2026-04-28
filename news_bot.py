import requests
import feedparser
import anthropic
import schedule
import time
from datetime import datetime
import os

# ========== ตั้งค่าตรงนี้ ==========
LINE_NOTIFY_TOKEN = os.environ["LINE_NOTIFY_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
# ====================================

# RSS Feed แหล่งข่าวไทย + ต่างประเทศ
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
    return headlines[:8]  # ไม่เกิน 8 ข่าวต่อหมวด

def summarize_with_ai(category, headlines):
    """ใช้ Claude สรุปข่าวเป็นภาษาไทย"""
    if not headlines:
        return "ไม่พบข่าวในหมวดนี้"
    
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    headlines_text = "\n".join(f"- {h}" for h in headlines)
    prompt = f"""สรุปข่าวหมวด {category} ต่อไปนี้เป็นภาษาไทย กระชับ ไม่เกิน 3 ประเด็นหลัก
แต่ละประเด็นไม่เกิน 2 บรรทัด เขียนให้เข้าใจง่าย:

{headlines_text}"""
    
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def send_to_line(message):
    """ส่งข้อความเข้า LINE Notify"""
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    response = requests.post(url, headers=headers, data=data)
    return response.status_code == 200

def build_and_send_news():
    """ฟังก์ชันหลัก: รวบรวม สรุป และส่งข่าว"""
    print(f"[{datetime.now()}] เริ่มรวบรวมข่าว...")
    
    today = datetime.now().strftime("%d/%m/%Y")
    full_message = f"\n📰 สรุปข่าวประจำวัน {today}\n{'='*30}\n"
    
    for category, feeds in RSS_FEEDS.items():
        print(f"  กำลังดึงข่าว: {category}")
        headlines = fetch_news(feeds)
        summary = summarize_with_ai(category, headlines)
        full_message += f"\n{category}\n{summary}\n"
    
    full_message += f"\n{'='*30}\n🤖 สรุปโดย AI | {datetime.now().strftime('%H:%M')} น."
    
    # LINE มีขีดจำกัด 1000 ตัวอักษรต่อครั้ง
    # แบ่งส่งถ้าข้อความยาวเกินไป
    if len(full_message) <= 1000:
        send_to_line(full_message)
    else:
        chunks = [full_message[i:i+950] for i in range(0, len(full_message), 950)]
        for chunk in chunks:
            send_to_line(chunk)
            time.sleep(1)
    
    print(f"[{datetime.now()}] ส่งข่าวสำเร็จ!")

# ========== ตั้ง Schedule ==========
schedule.every().day.at("07:30").do(build_and_send_news)

print("🤖 News Bot เริ่มทำงานแล้ว... รอส่งข่าวทุกเช้า 07:30 น.")
print("กด Ctrl+C เพื่อหยุด")

# ทดสอบส่งทันทีครั้งแรก (ถ้าต้องการ)
# build_and_send_news()

while True:
    schedule.run_pending()
    time.sleep(60)
