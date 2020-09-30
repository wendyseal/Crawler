#單網站多網頁，透過for迴圈將不同連結頁面內的商品名稱與連結都爬下來
from selenium import webdriver
import psycopg2
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import requests
import time
# username=input('username:')
# password=input('password')
# conn = psycopg2.connect(database="gift_expert_testenv", user=username, password=password,
#                                             host="172.104.89.11", port="5432")
# print('Connection successful!')
# cur = conn.cursor()
# pinkoi的網域名稱
domain="https://www.pinkoi.com/"
total = []
# pinkoi的商品分類有15項(category=0,1,2,3,4,5,6,8,9,10,11,12,13,14,15)，透過for迴圈更新url
for cat_num in range(16)[:1]:
    if cat_num == 7: #商品分類7會連至商品分類5，所以跳過7。
        continue
    link = domain+"browse?category="+str(cat_num)
    print("=====轉換主題=====")
    # 換主題，頁碼從頭開始計算
    page = 0
    # 換主題，商品數量從頭開始計算
    cat_total = 0
    while True:
        page+=1
        pagelink=f'{link}&page={page}'

        # 打開瀏覽器
        driver = webdriver.Chrome("chromedriver")  # 括號裡面打chromedriver的路徑
        driver.get(pagelink)
        time.sleep(1)
        # 關掉廣告
        try:
            ad_block = driver.find_element_by_class_name('m-modal-close').click()
            print("有廣告")
        except:
            print("沒有廣告")
        # 抓取商品群的頁面內容
        get_source = driver.page_source
        soup = BeautifulSoup(get_source, "html.parser")  # type(soup) <class 'bs4.BeautifulSoup'>
        # 測試該頁有沒有商品
        if soup.find_all(class_='product-link')!=[]:
            # 尋找目標：想要的商品項目存放在class_='product-link'下
            nodes = soup.find_all(class_='product-link')
            # for迴圈列出該頁每一個商品，並用enumerate編號=i
            # url商品超連結
            # title商品名稱
            for i, ele in enumerate(nodes):
                url = domain + ele.find_all('a')[0].get('href')
                title = ele.find_all('a')[1].get('title')
                print("loading",i, title, url)
                if i == (len(nodes) - 1):  # 用來計算該分類的總商品數。本頁最末端list編號是(list長度-1)
                    cat_total += len(nodes)
                r=requests.get(url,headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"})
                # print('='*30)
                # print(r.text)
                #寫入DB:
                # SQL = "INSERT INTO pages(url, domain, title, content, local_file) VALUES(%s, %s, %s, %s, %s);"
                # data = (url, "www.pinkoi.com", f'pinkoi第{cat_num}分類之第{page}頁-NO.{i}-{title}', r.text, username)
                # cur.execute(SQL, data)
                # conn.commit()
            #     # with open("html.html", 'w', encoding="utf-8") as f:
            #     #     f.write(r.text)
            print(f"===成功讀取第{cat_num}分類之第{page}頁的商品===")
            print(f':: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}')
            driver.close()
        else:
            print("沒有商品可以讀取")
            driver.close()
            break
    total.append(cat_total)  # 紀錄該分類的商品數
conn.close()
print(f'total={total}')
sum = 0
for t in total:
    sum+=t
print(f'Pinkoi 總共有{sum}項商品')
