import requests
import json
import argparse
import os


def downloadProduct(obj, output, ext):
    image_urls = obj["image_urls"]
    descriptions = obj["descriptions"]

    # take = 3

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
                caption = descriptions["Product Name"]
                f.write(caption)


def __main__(input, output, ext):
    json_data = json.load(open(input, "r"))

    for i, obj in enumerate(json_data):
        downloadProduct(obj, output, ext)
        print(f"Downloaded {i+1}/{len(json_data)}")


if __name__ == "__main__":
    # input json path, output path
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input json path")
    parser.add_argument("output", help="output json path")
    parser.add_argument("--ext", help="caption extension", default="txt")
    args = parser.parse_args()

    __main__(args.input, args.output, args.ext)
