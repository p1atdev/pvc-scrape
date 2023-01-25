import requests
import json
import argparse
import os


def downloadProduct(obj, output, ext):
    image_urls = obj["image_urls"]
    descriptions = obj["descriptions"]
    meta = obj["meta"]

    captions = []
    captions.append(obj["name"])
    captions.append(descriptions["Product Categories"])
    try: captions.append(meta["Original"])
    except: pass
    try: captions.append(meta["character"])
    except: pass

    for i, url in enumerate(image_urls):
        image_name = url.split("/")[-1]
        filename = image_name.split(".")[0]

        # if exists, skip
        if not os.path.exists(f"{output}/{image_name}"):
            image = requests.get(url).content

            with open(f"{output}/{image_name}", "wb") as f:
                f.write(image)

        # save captions
        if not os.path.exists(f"{output}/{filename}.txt"):
            with open(f"{output}/{filename}.{ext}", "w", encoding="utf-8") as f:
                f.write(", ".join(captions))


def __main__(input, output, ext, limit, debug):
    print("Downloading Tokyo Figure products...")

    json_data = json.load(open(input, "r", encoding="utf-8"))

    # filter with Product Categories
    exclude_categories = [
        "Pullip / Sakura Kinomoto",
        "Doll Collection Doll",
        "Deformed Collection Figure",
        "Large statueSeries",
        "Artist Collections/Statues",
        "PVC Figures",
        "Deformed Figures (Shokugan/Candy Toys)",
    ]
    products = []
    for obj in json_data:
        print(obj["descriptions"])
        if obj["descriptions"]["Product Categories"] in exclude_categories:
            continue
        else:
            products.append(obj)

    # limit
    if debug:
        products = products[:10]
        print(products)
    elif limit is not None:
        products = products[:limit]

    for i, obj in enumerate(products):
        downloadProduct(obj, output, ext)
        print(f"Downloaded {i+1}/{len(products)}")


if __name__ == "__main__":
    # input json path, output path
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input json path")
    parser.add_argument("output", help="output json path")
    parser.add_argument("--ext", help="caption extension", default="txt")
    parser.add_argument("--limit", help="limit", default=None)
    parser.add_argument("--debug", help="debug", default=False)
    args = parser.parse_args()

    __main__(args.input, args.output, args.ext, args.limit, args.debug)
