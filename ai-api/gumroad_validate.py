import json
from urllib import error, parse, request

product_ids = {
    "Personal Monthly": "bpOmzyC5QJZKU-My3ODixg==",
    "Commercial Monthly": "atqnNLINGLt3an45A-7bHA==",
    "Personal Lifetime 4": "nSiyDUkI9GOIdQtEuxn4Eg==",
    "Personal Lifetime 9": "5zPbHEaWcC4rX_KfE2xHow==",
    "Personal Lifetime 19": "x8AuY7Cwld5HORBN3P9BIQ==",
    "Personal Lifetime 39": "yQnNIBwYXaWLMmql4XgNgA==",
    "Personal Lifetime 79": "VKG6AvrEUOey3a9qIg2Plw==",
}


class GumroadValidationNetworkError(Exception):
    pass


def verify_gumroad_license(product_id, license_key, timeout=10):
    url = "https://api.gumroad.com/v2/licenses/verify"
    data = parse.urlencode({"product_id": product_id, "license_key": license_key}).encode(
        "utf-8"
    )
    req = request.Request(url, data=data, method="POST")

    try:
        with request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        try:
            return json.loads(exc.read().decode("utf-8"))
        except Exception as inner_exc:
            raise GumroadValidationNetworkError(str(inner_exc)) from exc
    except error.URLError as exc:
        raise GumroadValidationNetworkError(str(exc)) from exc


def verify_merlin_license(license_key):
    curr_response = {"success": False}
    for product_name, product_id in product_ids.items():
        curr_response = verify_gumroad_license(product_id, license_key)
        curr_response["merlin_product_name"] = product_name
        curr_response["merlin_product_id"] = product_id
        if curr_response.get("success") is True:
            return curr_response

    return curr_response


if __name__ == "__main__":
    MY_LICENSE_KEY = "A8EBB701-225D444E-BFD6911F-FDB25D40"
    result = verify_merlin_license(MY_LICENSE_KEY)
    print(result)
