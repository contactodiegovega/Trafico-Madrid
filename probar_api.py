import requests

url = "https://openapi.desarrollo.emtmadrid.es/v2/mobilitylabs/user/login/"

headers = {
    "email": "dievesan019@gamil.com",
    "password": "NFTisthefuture1%"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print(response.json())