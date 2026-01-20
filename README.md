# TG CountBot (研究所倒數計時機器人)

這個機器人會發送研究所考試的倒數計時訊息到指定的 Telegram 聊天室或群組。

## 功能

- 自動計算距離各大專院校考試日期的天數。
- **動態過濾**：考試日期已過的學校將自動從列表中移除。
- **定時報時**：每天 07:00 到 23:00 整點報時（排除深夜 00:00 - 06:00）。
- **時區支援**：使用 `Asia/Taipei` 時區，適合部署在任何雲端平台 (Zeabur, Heroku 等)。

## 本地開發設置

1. 安裝 Python 套件：
   ```bash
   pip install -r requirements.txt
   ```

2. 設定環境變數：
   複製 `.env.example` 為 `.env`，並填入您的資訊：
   ```text
   TELEGRAM_TOKEN=你的機器人Token
   TELEGRAM_CHAT_ID=你的ChatID
   ```

3. 執行機器人：
   ```bash
   python TG_Bot
   ```

## 部署到 Zeabur

### 1. 準備 GitHub Repository
確保此資料夾內已有 `requirements.txt` 和 `TG_Bot`，並推送到 GitHub。

### 2. 在 Zeabur 建立服務
1. 登入 [Zeabur Dashboard](https://dash.zeabur.com)。
2. 建立新專案 -> 部署新服務 -> 選擇 GitHub -> 選取此 Repository。
3. Zeabur 會自動偵測這是 Python 專案並開始建置。

### 3. 設定環境變數 (Environment Variables)
在 Zeabur 該服務的 **Variables** 分頁中，新增以下變數：

| Key | Value |
| -- | -- |
| `TELEGRAM_TOKEN` |(你的 Bot Token) |
| `TELEGRAM_CHAT_ID` |(你的 Chat ID) |

> 注意：不要將 `.env` 檔案上傳到 GitHub，請直接在 Zeabur 後台設定。

### 4. 設定時區 (可選)
雖然程式碼內已指定 `Asia/Taipei`，但建議在 Zeabur 環境變數中也加入 `TZ` 設定：
- `TZ` = `Asia/Taipei`

### 5. 確保運作
Zeabur 預設會執行 `python main.py`，如果找不到會嘗試 `python TG_Bot` (或是看它如何偵測)。
如果啟動失敗，請在 Zeabur 的 **Settings -> Service Name** 修改 **Start Command** 為：
```bash
python TG_Bot
```
