from requests import *

key = ""
congress = 117

def get_secrets(filename: str):
    with open(filename) as file:
        return file.readline()

def get_bills():
    params = {
        "api_key": key,
        "format": "json",
        "offset": 0,
        "limit": 250
    }
    bills = []
    url = f"https://api.congress.gov/v3/bill/{congress}/s"
    response = get(url, params).json()
    while len(response["bills"]) != 0:
        response = get(url, params).json()
        print(response)
        bills.extend(response["bills"])
        params["offset"] += 250
    return bills

if __name__ == "__main__":
    key = get_secrets("./secrets.txt")
    bills = get_bills()