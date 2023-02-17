# Inspired from  https://github.com/erikKeresztes/gaugan.py

import sys
import requests
import re
import base64
import random
import string
import http.client
import imghdr


def getUrl():
    r = requests.get("http://www.imaginaire.cc/gaugan2/demo.js")
    urls = re.findall(r"\'(http.*?://.*?/)\'", r.text)
    return urls[0]


def processImage(image, style="random", url=None, caption=""):
    if not isinstance(image, bytes):
        raise (ValueError("Image must be bytes."))

    if imghdr.what(None, image) != "png":
        raise (ValueError("Image must be PNG format."))

    if not isinstance(style, int) and style != "random":
        raise (ValueError("Wrong style, must be an integer or 'random'"))

    if url is None:
        url = getUrl()

    # get b64 encoded image
    imgb64 = "data:image/png;base64," + str(base64.b64encode(image))[2:-1]

    # generate name for requests
    name = "".join(random.choices(string.ascii_lowercase + string.digits, k=20))

    # send map img to server
    requests.post(
        url + "gaugan2_infer",
        data={
            "masked_image": imgb64,
            "masked_edgemap": imgb64,
            "masked_segmap": imgb64,
            "name": name,
            "caption": caption,
            "style_name": "random",
            "enable_seg": "true",
            "enable_edge": "false",
            "enable_caption": "false",
            "enable_image": "false",
            "use_model2": "false",
        },
    )

    # get generated img from server
    r = requests.post(
        url + "gaugan2_receive_output",
        stream=True,
        data={"name": name, "style_name": str(style)},
    )

    if r.status_code != 200:
        raise (
            RuntimeError(
                f"{http.client.responses[r.status_code]} ({r.status_code}) while processing image."
            )
        )

    r.raw.decode_content = True
    return r.raw.data


if __name__ == "__main__":

    image_path = sys.argv[1]
    caption = sys.argv[2] if len(sys.argv) >= 3 else ""

    with open(image_path, "rb") as f:
        image = processImage(f.read(), caption=caption)

    with open("output.jpg", "wb") as f:
        f.write(image)
