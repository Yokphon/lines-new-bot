# 📰 LINE News Bot

ระบบส่งข่าวสรุปอัตโนมัติเข้า LINE ทุกเช้า โดยใช้ AI สรุปข่าวจาก RSS Feed หลายหมวดหมู่

---

## ✨ ฟีเจอร์

- ดึงข่าวอัตโนมัติจาก RSS Feed 5 หมวด
- สรุปข่าวด้วย AI (Google Gemini)
- ส่งข้อความเข้า LINE อัตโนมัติทุกเช้า 07:30 น.
- รันบน GitHub Actions ไม่ต้องเปิดคอมทิ้งไว้

---

## 📂 โครงสร้างไฟล์

```
line-news-bot/
├── news_bot.py          # โค้ดหลัก
├── requirements.txt     # Library ที่ใช้
└── .github/
    └── workflows/
        └── daily_news.yml  # GitHub Actions Schedule
```

---

## 🗞️ หมวดข่าวที่ส่ง

| หมวด | แหล่งข่าว |
|---|---|
| 🏛️ การเมืองไทย | ไทยรัฐ, มติชน |
| 📈 เศรษฐกิจ/หุ้น | Bangkok Biz News, BBC Business |
| 💻 เทคโนโลยี/AI | TechCrunch, The Verge |
| 🌍 ต่างประเทศ | BBC World, NY Times |
| ⚽ กีฬา | BBC Sport, ไทยรัฐกีฬา |

---

## ⚙️ วิธีติดตั้ง

### 1. Fork หรือ Clone Repository นี้

```bash
git clone https://github.com/your-username/line-news-bot.git
```

### 2. ตั้งค่า GitHub Secrets

ไปที่ **Settings → Secrets and variables → Actions** แล้วเพิ่ม:

| Secret Name | รายละเอียด |
|---|---|
| `LINE_CHANNEL_TOKEN` | Channel Access Token จาก LINE Developers Console |
| `LINE_GROUP_ID` | User ID หรือ Group ID ที่ต้องการส่ง |
| `GEMINI_API_KEY` | API Key จาก Google AI Studio |

### 3. วิธีขอ Keys

**LINE Channel Access Token**
1. ไปที่ [developers.line.biz](https://developers.line.biz/console)
2. สร้าง Provider → สร้าง Messaging API Channel
3. แถบ Messaging API → Channel access token → กด Issue

**Gemini API Key**
1. ไปที่ [aistudio.google.com](https://aistudio.google.com)
2. กด Get API Key → Create API Key
3. คัดลอก Key ไว้

### 4. ทดสอบรัน

ไปที่แถบ **Actions** → เลือก **Daily News Bot** → กด **Run workflow**

---

## ⏰ กำหนดการส่งข่าว

```yaml
cron: '30 0 * * *'  # ทุกวัน 07:30 น. เวลาไทย (UTC+7)
```

ถ้าต้องการเปลี่ยนเวลา แก้ไขไฟล์ `.github/workflows/daily_news.yml` ครับ

ตัวอย่างเวลาอื่น:
```yaml
'0 1 * * *'   # 08:00 น.
'30 1 * * *'  # 08:30 น.
'0 2 * * *'   # 09:00 น.
```

---

## 📱 ตัวอย่างข้อความที่ได้รับ

```
📰 สรุปข่าวประจำวัน 29/04/2026
==============================

🏛️ การเมืองไทย
1. รัฐบาลประกาศมาตรการ...
2. สภาผู้แทนราษฎรลงมติ...
3. พรรคฝ่ายค้านออกแถลงการณ์...

📈 เศรษฐกิจ/หุ้น
1. ตลาดหุ้นไทยปิดบวก...
2. ค่าเงินบาทแข็งค่า...

...

==============================
🤖 สรุปโดย AI | 07:30 น.
```

---

## 🛠️ เทคโนโลยีที่ใช้

- **Python 3.11**
- **Google Gemini API** — สรุปข่าวด้วย AI
- **LINE Messaging API** — ส่งข้อความเข้า LINE
- **feedparser** — ดึงข่าวจาก RSS Feed
- **GitHub Actions** — รันอัตโนมัติทุกวัน

---

## 💰 ค่าใช้จ่าย

| บริการ | ค่าใช้จ่าย |
|---|---|
| GitHub Actions | ฟรี (2,000 นาที/เดือน) |
| Google Gemini API | ฟรี (15 requests/นาที) |
| LINE Messaging API | ฟรี (200 ข้อความ/เดือน) |
| **รวม** | **ฟรี 100%** |

---

## 📝 License

MIT License
