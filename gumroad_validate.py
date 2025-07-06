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
    print(data)
    response = requests.post(url, data=data)
    return response.json()

def verify_merlin_license(license_key):
    validations = []
    for k in product_ids:
        v = product_ids[k]
        validations.append(verify_gumroad_license(v,license_key)) 
    return validations

if __name__ == "__main__":
    result = verify_gumroad_license("PRODUCT_ID", "LICENSE_KEY")
    if result["success"]:
        print("License is valid!")
    else:
        print("Invalid license:", result.get("message"))
    MY_LICENSE_KEY = "A8EBB701-225D444E-BFD6911F-FDB25D40"
    result = verify_merlin_license(MY_LICENSE_KEY)
    for v in result:
        print(v)
    
