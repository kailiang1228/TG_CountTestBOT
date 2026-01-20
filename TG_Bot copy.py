#!/usr/bin/env python3
import time
import requests
import datetime
import pytz
import os
import sys
import logging
from dotenv import load_dotenv

# 載入環境變數 (本地開發用)
load_dotenv()

# 設定 Logging (輸出到 stdout，方便雲端環境查看 Logs)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# 設定 (優先讀取環境變數)
TOKEN = os.getenv('TELEGRAM_TOKEN', 'YOUR_TOKEN_HERE')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_HERE')

# 考試日期
EXAM_DATES = {
    "台科大": (2, 1),
    "台聯大": (2, 2),
    "成大": (2, 3), 
    "中興": (2, 6),
    "中山": (2, 7),
    "中央": (2, 9),
    "中正": (2, 11),
    "北科大": (3, 8),
}

# 發送時間點 (每日 07:00 ~ 23:00 整點發送)
SEND_HOURS = list(range(7, 24))  # 7, 8, ..., 23

def get_tw_now():
    return datetime.datetime.now(pytz.timezone('Asia/Taipei'))

def calculate_message():
    now = get_tw_now()
    today = now.date()
    lines = ["研究所筆試倒數："]
    
    # 判斷是否還有任何考試在未來
    active_exams_count = 0

    for school, (month, day) in EXAM_DATES.items():
        # 計算考試日期 (假設是今年)
        try:
            target_date = datetime.date(now.year, month, day)
        except ValueError: # 閏年處理
            target_date = datetime.date(now.year, month, day)

        # 計算天數差
        days_left = (target_date - today).days

        # 如果 days_left < 0 代表考過了，不輸出
        if days_left < 0:
            continue
            
        active_exams_count += 1
        date_str = f"{month:02d}/{day:02d}"

        if school == "成大":
            lines.append(f"{school}：{date_str} - 02/04（倒數{days_left}天）")
        else:
            lines.append(f"{school}：{date_str}（倒數{days_left}天）")

    if active_exams_count == 0:
        return "所有考試皆已結束！"

    lines.append(".")
    lines.append(".")
    lines.append("這個時間還在滑手機？會當兵的")
    return "\n".join(lines)

def send_telegram(text):
    if not TOKEN or not CHAT_ID:
        logging.error("錯誤: 未設定 TELEGRAM_TOKEN 或 TELEGRAM_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        logging.info(f"準備發送訊息，目標 Chat ID: {CHAT_ID}")
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status() # 檢查 HTTP 錯誤
        logging.info("訊息發送成功")
    except Exception as e:
        logging.error(f"發送失敗: {e}")

def get_seconds_until_next_run():
    now = get_tw_now()
    # 尋找今天稍晚的執行時間
    for h in sorted(SEND_HOURS):
        target = now.replace(hour=h, minute=0, second=0, microsecond=0)
        if target > now:
            return (target - now).total_seconds()

    # 如果今天都過了，找明天的第一個時間
    next_day = now + datetime.timedelta(days=1)
    target = next_day.replace(hour=SEND_HOURS[0], minute=0, second=0, microsecond=0)
    return (target - now).total_seconds()

def main():
    logging.info("程式啟動中...")
    logging.info(f"目前時間 (TW): {get_tw_now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not TOKEN or "YOUR_TOKEN" in TOKEN:
         logging.warning("⚠️ 警告: TELEGRAM_TOKEN 尚未設定正確")
    
    logging.info(f"設定排程時間點 (24h): {SEND_HOURS}")
    logging.info("開始進入排程迴圈...")

    while True:
        try:
            wait_seconds = get_seconds_until_next_run()
            next_run_time = get_tw_now() + datetime.timedelta(seconds=wait_seconds)
            
            logging.info(f"下次發送時間: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')} (約 {wait_seconds / 60:.1f} 分鐘後)")
            logging.info("進入休眠...")

            time.sleep(wait_seconds)

            # 醒來後執行
            logging.info("休眠結束，開始執行任務")
            msg = calculate_message()
            send_telegram(msg)

            # 避免在同一秒內重複觸發
            time.sleep(5)

        except KeyboardInterrupt:
            logging.info("接收到停止訊號，程式結束")
            break
        except Exception as e:
            logging.error(f"發生未預期的錯誤: {e}", exc_info=True)
            logging.info("為防止崩潰，等待 60 秒後重試...")
            time.sleep(60)

if __name__ == "__main__":
    main()
