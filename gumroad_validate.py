import requests

product_ids = {
    "Personal Monthly": "bpOmzyC5QJZKU-My3ODixg==",
    "Commercial Monthly": "atqnNLINGLt3an45A-7bHA==",
    "Personal Lifetime 4": "nSiyDUkI9GOIdQtEuxn4Eg==",
    "Personal Lifetime 9": "5zPbHEaWcC4rX_KfE2xHow==",
    "Personal Lifetime 19": "x8AuY7Cwld5HORBN3P9BIQ==",
    "Personal Lifetime 39": "yQnNIBwYXaWLMmql4XgNgA==",
    "Personal Lifetime 79": "VKG6AvrEUOey3a9qIg2Plw==",
}


def verify_gumroad_license(product_id, license_key):
    url = "https://api.gumroad.com/v2/licenses/verify"
    data = {"product_id": product_id, "license_key": license_key}
    response = requests.post(url, data=data)
    return response.json()

def verify_merlin_license(license_key):
    curr_response = None
    for k in product_ids:
        v = product_ids[k]
        curr_response = verify_gumroad_license(v,license_key) 
        if curr_response["success"]==True:
            return curr_response
    return curr_response

if __name__ == "__main__":
    MY_LICENSE_KEY = "A8EBB701-225D444E-BFD6911F-FDB25D40"
    result = verify_merlin_license(MY_LICENSE_KEY)
    print(result)
