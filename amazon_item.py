import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd
import datetime
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager


def set_driver(headless_flg):
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    service=Service(ChromeDriverManager().install())
    return Chrome(service=service, options=options)


#ログ出力
log_file_path = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
file_name = f"./log/log_{log_file_path}.log"

def log(txt):
    now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(file_name, mode='a', encoding='utf-8_sig') as f:
        f.write(f'[log: {now}] {txt}' + '\n')


#main処理
def main():
    count = 0
    # 空のDataFrame作成
    df = pd.DataFrame()
    log("処理開始")
    search_keyword = input('検索キーワードを入力してください:')
    log(f"検索キーワード:{search_keyword}")
    driver = set_driver(False)

    #URLにて検索ワードを直接指定して検索結果を表示
    url = "https://www.amazon.co.jp/s?k=" + search_keyword
    driver.get(url)
    time.sleep(5)
    
    # ページ終了まで繰り返し取得
    while True:
        page = driver.page_source       
        bs = BeautifulSoup(page, 'lxml')

        # 商品名、価格、ASIN、画像URL
        name_list = bs.select('.a-size-base-plus')
        prices = bs.select('.a-price-whole')
        asin_code = bs.select('div[data-component-type="s-search-result"]')
        image_url = bs.select('.s-image')
        
        
        # 1ページ分繰り返し
        for name, price, asin, image in zip(name_list, prices, asin_code, image_url):
            try:
                asin = asin.get('data-asin')
                image = image.get('src')
                print(name.text, price.text, asin, image, sep="\n")
                log(f"{count}件目成功：{name.text}")

                #DataFrameに対して辞書形式でデータを追加
                df = df.append(
                {"商品名": name.text, 
                "価格": price.text,
                "ASIN": asin,
                 "画像URL": image}, 
                ignore_index=True)
            except Exception as e:
                log(f"{count}件目失敗：{name.text}")
                log(e)
            finally:
                count += 1
        
        #次ページクリック、ない場合は終了
        next_page = bs.select('li.a-last > a')
        if len(next_page) > 0:
            next_page_url = "https://www.amazon.co.jp" + next_page[0].get('href')
            driver.get(next_page_url)
            time.sleep(3)
        else:
            break
        
    df.to_csv('test.csv', mode='a', encoding='utf_8_sig')
       


if __name__ == "__main__":
    main()

