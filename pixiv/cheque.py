import aiohttp
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# PHPSESSIDをファイルから読み込む
def load_phpsessid(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        print(f"PHPSESSIDの読み込みに失敗しました: {e}")
        return None

# Google Sheetsに接続
def connect_google_sheets(sheet_id):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_id).sheet1
    return sheet

# 小説のデータを非同期で取得
async def get_novel_data(session, novel_id):
    url = f'https://www.pixiv.net/ajax/novel/{novel_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
        'Referer': f'https://www.pixiv.net/novel/show.php?id={novel_id}'
    }
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()

            bookmark_count = data['body']['bookmarkCount']  # ブクマ数
            like_count = data['body']['likeCount']  # いいね数
            view_count = data['body']['viewCount']  # 閲覧数

            bookmark_rate = (bookmark_count / view_count) * 100 if view_count > 0 else 0

            return novel_id, view_count, bookmark_count, like_count, round(bookmark_rate, 2)
        else:
            print(f"小説ID {novel_id} のデータ取得に失敗しました。ステータスコード: {response.status}")
            return None

# Google Sheetsにデータを書き込む
def update_google_sheet(sheet, data):
    
    sheet.clear()
    
    sheet.append_row(["作品ID", "閲覧数", "ブクマ数", "いいね数", "ブクマ率(%)"])
    
    sheet.append_rows(data)

# ファイルから小説IDを読み込む
def load_novel_ids_from_file(file_path):
    try:
        with open(file_path, 'r') as f:
            novel_ids = f.read().splitlines()  # 各行のIDをリストに変換
        return novel_ids
    except Exception as e:
        print(f"ファイルの読み込みに失敗しました: {e}")
        return []

# 非同期処理をメインで実行
async def main():
    phpsessid = load_phpsessid('PHPSESSID.txt')
    
    if not phpsessid:
        print("PHPSESSIDが取得できませんでした。プログラムを終了します。")
        return

    cookies = {'PHPSESSID': phpsessid}
    sheet_id = "スプレットシートのID（urlの後ろの文字列）"
    sheet = connect_google_sheets(sheet_id)

    novel_ids = load_novel_ids_from_file('illust_ids.txt')
    if not novel_ids:
        return

    async with aiohttp.ClientSession(cookies=cookies) as session:
        data = []
        for novel_id in novel_ids:
            retries = 3 
            for attempt in range(retries):
                result = await get_novel_data(session, novel_id)
                if result is not None:
                    data.append(result)
                    break 
                else:
                    print(f"小説ID {novel_id} のデータ取得に失敗しました。リトライします...")
                    await asyncio.sleep(10)
            await asyncio.sleep(5) 

    # Google Sheetsにデータを更新
    update_google_sheet(sheet, data)
    print("スプレッドシートが更新されました！")

if __name__ == "__main__":
    asyncio.run(main())
