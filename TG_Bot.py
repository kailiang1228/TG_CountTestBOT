#!/usr/bin/env python3
import time
import requests
import datetime
import pytz
import os
import sys
from dotenv import load_dotenv

# 載入環境變數 (本地開發用)
load_dotenv()

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
    
    # 判斷是否還有任何考試在未來，如果都考完了就回傳 None 或提示
    active_exams_count = 0

    for school, (month, day) in EXAM_DATES.items():
        # 計算考試日期 (假設是今年)
        try:
            # 這裡簡單假設考試年份就是現在年份
            # 如果現在是 12 月而考試在 2 月，通常是指隔年，但這裡先以「當年度邏輯」或「跨年邏輯」處理
            # 您的情境是 2026/01/20，考試在 2 月，所以是 same year
            target_date = datetime.date(now.year, month, day)
        except ValueError: # 閏年處理
            target_date = datetime.date(now.year, month, day)

        # 計算天數差
        days_left = (target_date - today).days

        # 如果 days_left < 0 代表考過了，依需求不輸出
        if days_left < 0:
            continue
            
        active_exams_count += 1
        date_str = f"{month:02d}/{day:02d}"

        if school == "成大":
            lines.append(f"{school}：{date_str} - 02/04（倒數{days_left}天）")
        else:
            lines.append(f"{school}：{date_str}（倒數{days_left}天）")

    if active_exams_count == 0:
        return "所有考試皆已結束！恭喜解脫或是...下次加油？"

    lines.append(".")
    lines.append(".")
    lines.append("這個時間點還在滑手機？會當兵的")
    return "\n".join(lines)

def send_telegram(text):
    if not TOKEN or not CHAT_ID:
        print("錯誤: 未設定 TOKEN 或 CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
        print(f"[{get_tw_now()}] 訊息發送成功", flush=True)
    except Exception as e:
        print(f"發送失敗: {e}", flush=True)

def get_seconds_until_next_run():
    now = get_tw_now()
    # 尋找今天稍晚的執行時間
    for h in sorted(SEND_HOURS):
        # 設定目標為今天的該小時 0分 0秒
        target = now.replace(hour=h, minute=0, second=0, microsecond=0)
        
        # 如果目標時間比現在晚，這就是下一個時間點
        if target > now:
            return (target - now).total_seconds()

    # 如果今天都過了，找明天的第一個時間
    next_day = now + datetime.timedelta(days=1)
    target = next_day.replace(hour=SEND_HOURS[0], minute=0, second=0, microsecond=0)
    return (target - now).total_seconds()

def main():
    print(f"已啟動。目標 Chat ID: {CHAT_ID}", flush=True)
    
    # 剛啟動時先檢查一次是否要補發？
    # 或者直接進入排程模式。通常雲端重啟頻繁，直接進入排程較安全，避免一直發。
    
    while True:
        wait_seconds = get_seconds_until_next_run()
        next_run_time = get_tw_now() + datetime.timedelta(seconds=wait_seconds)
        print(f"[{get_tw_now()}] 下次發送時間: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')} (約 {wait_seconds / 60:.1f} 分鐘後)", flush=True)

        time.sleep(wait_seconds)

        # 醒來後再次確認時間是否正確 (避免 sleep 提早醒來的極端狀況，或確保真的到了整點)
        # 這裡直接執行，因為 calculate_message 會根據當下日期計算
        msg = calculate_message()
        send_telegram(msg)

        # 避免在同一秒內重複觸發，休息一下
        time.sleep(5)

if __name__ == "__main__":
    main()
