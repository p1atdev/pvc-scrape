from bs4 import BeautifulSoup
import requests
import json


def getImageUrls(html):
    soup = BeautifulSoup(html, "lxml")

    img_tags = soup.find_all("ul", class_="clearfix pvSamllImg relative")[0].find_all(
        "img"
    )
    img_urls = [img_tag["src"] for img_tag in img_tags]
    return img_urls


def getDescriptions(html):
    soup = BeautifulSoup(html, "lxml")

    desc_tags = soup.find_all("div", class_="imgViewText")[0].find_all("p")
    descriptions = [desc_tag.text for desc_tag in desc_tags]
    return descriptions


def parseDescriptions(descriptions):
    descriptions = [desc.strip() for desc in descriptions]
    # descriptions = [
    #     desc
    #     for desc in descriptions
    #     if "Price" not in desc and "Release Date" not in desc
    # ]

    # remove empty
    descriptions = [desc for desc in descriptions if desc != ""]

    # replace "：" with ":"
    descriptions = [desc.replace("：", ":") for desc in descriptions]
    descriptions = [desc.replace("（", "(") for desc in descriptions]
    descriptions = [desc.replace("）", ")") for desc in descriptions]

    # replace no break space
    descriptions = [desc.replace("\u00a0", " ") for desc in descriptions]
    descriptions = [desc.replace("\u3001", ",") for desc in descriptions]

    # split with ":" and convert to dict
    descriptions = [desc.split(":") for desc in descriptions]
    descriptions = {desc[0]: desc[1] for desc in descriptions}

    # strip
    descriptions = {k: v.strip() for k, v in descriptions.items()}

    return descriptions


def createItem(base, urls, descriptions, id):
    item = {
        "id": id,
        "image_urls": [base + url for url in urls],
        "descriptions": descriptions,
    }

    return item


def saveJson(items, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=4)


def __main__():
    base = "http://www.myethos.cn"
    template = "http://www.myethos.cn/Collection/view/id/"
    path = "../myethos.json"

    items = []

    for i in range(100, 200):
        url = template + str(i)
        print(url)

        html = requests.get(url).text

        img_urls = getImageUrls(html)

        if len(img_urls) == 0:
            continue

        print(img_urls)

        descriptions = getDescriptions(html)
        descriptions = parseDescriptions(descriptions)
        print(descriptions)

        item = createItem(base, img_urls, descriptions, i)

        print(item)

        items.append(item)

    saveJson(items, path)


if __name__ == "__main__":
    __main__()
