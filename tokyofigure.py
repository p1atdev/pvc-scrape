from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import json

options = webdriver.FirefoxOptions()
options.set_preference("intl.accept_languages", "en")
# headless
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 10)

base = "https://tokyofigure.jp"
cookies = [
    {
        "name": "wovn_mtm_showed_langs",
        "value": "[\"en\"]",
        "domain": "tokyofigure.jp",
    }, {
        "name": "wovn_selected_lang",
        "value": "en",
        "domain": "tokyofigure.jp",
    }
]
headers = {
    "Accept-Language": "en-US,en;q=0.9",
}

driver.get(base)

for cookie in cookies:
    driver.add_cookie(cookie)

def getProductInfo(id, html):
    soup = BeautifulSoup(html, "lxml")

    product = {}

    product["id"] = id

    product["name"] = soup.find("h2", class_="name splogin").text.strip()
    product["price"] = soup.find("span", id="price02_default").text.strip()
    product["points"] = soup.find("span", id="point_default").text.strip()

    products_spec = soup.find("div", class_="block_outer products_spec").find_all("dl")
    descriptions = {}
    for spec in products_spec:
        descriptions[spec.find("dt").text.strip()] = spec.find("dd").text.strip()

    product["descriptions"] = descriptions

    product["comment"] = soup.find("div", class_="main_comment").text.strip()

    meta_spec = soup.find("div", class_="main_spec").find_all("dl")
    meta_info = {}
    for spec in meta_spec:
        meta_info[spec.find("dt").text.replace(":", "").strip()] = spec.find(
            "dd"
        ).text.strip()

    product["meta"] = meta_info

    thumbs = soup.find("div", class_="ad-thumbs").find_all("img")
    image_urls = []
    for thumb in thumbs:
        image_urls.append(thumb["src"])

    product["image_urls"] = [base + url for url in image_urls]

    print(product["name"], product["price"], "JPY")

    return product


def getAllProducts():
    url = "https://tokyofigure.jp/products/detail.php"

    session = requests.Session()

    products = []

    for page_num in range(1, 335):

        # temporary test
        res = session.get(url, params={"product_id": page_num})
        if res.status_code != 200:
            print("Page {} failed. Skipped.".format(page_num))
            continue

        # 大丈夫なのでアクセス
        driver.get(url + "?product_id={}&wovn=en".format(page_num))

        points_el = driver.find_element(By.XPATH, "//span[@class='point_label'][1]")
        if points_el.text != "Points:":
            wait.until(lambda x: x.find_element(By.XPATH, "//span[@class='point_label'][1]").text == "Points:")
        jan_code_el = driver.find_element(By.XPATH, "//dl[@class='jan_code']/dt[1]")
        if jan_code_el.text != "JAN code":
            wait.until(lambda x: x.find_element(By.XPATH, "//dl[@class='jan_code']/dt[1]").text == "JAN code")
        relsease_date_el = driver.find_element(By.XPATH, "//dl[@class='sale_date']/dd[1]")
        if any(x in relsease_date_el.text for x in ["年", "月", "日"]) :
            wait.until(lambda x: all(y not in (x.find_element(By.XPATH, "//dl[@class='sale_date']/dd[1]").text) for y in ["年", "月", "日"]))
        comment_el = driver.find_element(By.XPATH, "//div[@class='main_comment']")
        if any(x in comment_el.text for x in ["、", "。", "「", "」"]):
            try: wait.until(lambda x: all(y not in (x.find_element(By.XPATH, "//div[@class='main_comment']").text) for y in ["、", "。", "「", "」"]))
            except: pass
            
        html = driver.page_source
        # html = res.text

        product = getProductInfo(page_num, html)

        products.append(product)

        print("Page {} done".format(page_num))

    return products


def __main__():
    products = getAllProducts()
    # print(products)

    output = "../tokyofigure.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=4)

    driver.close()

    print("Done")


if __name__ == "__main__":
    __main__()
