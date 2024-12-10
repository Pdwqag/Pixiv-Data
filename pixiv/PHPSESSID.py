import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager  

current_dir = os.path.dirname(os.path.abspath(__file__))

# ログイン情報をファイルから読み込む
def load_credentials(file_path):
    try:
        with open(file_path, 'r') as file:
            credentials = file.read().splitlines()
        if len(credentials) >= 2:
            return credentials[0], credentials[1] 
        else:
            raise ValueError("ファイルに十分な情報がありません")
    except Exception as e:
        print(f"ログイン情報の読み込みに失敗しました: {e}")
        return None, None

# PixivにログインしてPHPSESSIDを取得
def login_to_pixiv_via_selenium(username, password):
    # 自動で適切なChromeDriverを取得
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    driver.get("https://accounts.pixiv.net/login")

    wait = WebDriverWait(driver, 20)

    email_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="username webauthn"]')))
    email_input.send_keys(username)

    password_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@autocomplete="current-password webauthn"]')))
    password_input.send_keys(password)

    password_input.send_keys(Keys.RETURN)

    # CAPTCHA解決を手動で促す
    print("CAPTCHAを解決してください。解決後にEnterキーを押してください...")
    input()  # 手動操作を待機

    input("操作を完了後、ブラウザを閉じる前にEnterキーを押してください...")

    # PHPSESSIDを取得
    cookies = driver.get_cookies()
    phpsessid = None
    for cookie in cookies:
        if cookie['name'] == 'PHPSESSID':
            phpsessid = cookie['value']
            break

    driver.quit() 

    return phpsessid

# PHPSESSIDをファイルに保存する
def save_phpsessid_to_file(phpsessid, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(phpsessid)
        print(f"PHPSESSIDが {file_path} に保存されました！")
    except Exception as e:
        print(f"PHPSESSIDの保存に失敗しました: {e}")

# メイン処理
def main():
    # credentials.txtからログイン情報を読み込む
    username, password = load_credentials(os.path.join(current_dir, 'credentials.txt'))

    if username and password:
        # PixivにログインしてPHPSESSIDを取得
        phpsessid = login_to_pixiv_via_selenium(username, password)
    
        if phpsessid:
            # PHPSESSIDをファイルに保存
            save_phpsessid_to_file(phpsessid, os.path.join(current_dir, 'PHPSESSID.txt'))
        else:
            print("PHPSESSIDを取得できませんでした")
    else:
        print("ログイン情報が不十分です")

if __name__ == "__main__":
    main()
