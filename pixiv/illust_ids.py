import requests
import json

# Pixivから投稿された小説のIDを取得（PHPSESSIDを使う）
def fetch_novel_ids(session, user_id):
    url = f'https://www.pixiv.net/ajax/user/{user_id}/profile/all?lang=ja'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
        'Referer': f'https://www.pixiv.net/users/{user_id}'
    }
    response = session.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        # すべての作品のIDをリストに収集
        novel_ids = list(data['body']['novels'].keys())  # 小説のIDを取得
        return novel_ids
    else:
        print(f"ユーザーID {user_id} のデータ取得に失敗しました。ステータスコード: {response.status_code}")
        return []

# PHPSESSIDをファイルから読み込む
def load_phpsessid(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()  # PHPSESSIDをテキストファイルから読み込む
    except Exception as e:
        print(f"PHPSESSIDの読み込みに失敗しました: {e}")
        return None

# 小説IDをファイルに保存する
def save_novel_ids_to_file(novel_ids, file_path):
    try:
        with open(file_path, 'w') as f:
            for novel_id in novel_ids:
                f.write(f"{novel_id}\n")
        print(f"小説IDが {file_path} に保存されました！")
    except Exception as e:
        print(f"ファイルの保存に失敗しました: {e}")

# メイン処理
def main():
    # PHPSESSIDをファイルから読み込む
    phpsessid = load_phpsessid('PHPSESSID.txt')
    
    if not phpsessid:
        print("PHPSESSIDが取得できませんでした。プログラムを終了します。")
        return

    # PHPSESSIDを使ってログイン済みのセッションを作成
    cookies = {
        'PHPSESSID': phpsessid  # ファイルから読み込んだPHPSESSIDを使用
    }
    session = requests.Session()
    session.cookies.update(cookies)

    # PixivのユーザーID（投稿者のID）
    user_id = '53857530' 

    # 投稿された小説IDを取得
    novel_ids = fetch_novel_ids(session, user_id)

    # 取得した小説IDをファイルに保存
    if novel_ids:
        save_novel_ids_to_file(novel_ids, 'illust_ids.txt')

if __name__ == "__main__":
    main()
