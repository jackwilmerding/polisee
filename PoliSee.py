from requests import *
import pymongo

key = ""
chamber = "s"

class Congress:
    def __init__(self, congressNumber):
        self.congressNumber = congressNumber
        self.members = get_members()

def get_secrets(filename: str):
    with open(filename) as file:
        return file.readline()

def get_bills(congressNumber):
    params = {
        "api_key": key,
        "format": "json",
        "offset": 0,
        "limit": 250
    }
    bills = []
    url = f"https://api.congress.gov/v3/bill/{congressNumber}/{chamber}"
    response = get(url, params).json()
    while len(response["bills"]) != 0:
        response = get(url, params).json()
        print(response)
        bills.extend(response["bills"])
        params["offset"] += 250
    return bills

def get_members(congressNumber):
    return {}

def update():
    for congressNumber in [117, 116, 115, 114, 113]:
        return



if __name__ == "__main__":
    key = get_secrets("./secrets.txt")