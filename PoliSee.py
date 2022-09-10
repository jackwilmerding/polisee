from requests import *
import pymongo

key = ""

class Member:
    def __init__(self, name: str, state : str, party: chr):
        self.name = name
        self.state = state
        self.party = party

class Congress:
    def __init__(self, congress_number: int):
        self.congress_number = congress_number
        self.senate = []
        self.house = []

class Database:
    def __init__(self):
        self.congresses = {}
        for i in range(113, 118):
            self.congresses[i] = Congress(i)

def get_secrets(filename: str):
    with open(filename) as file:
        return file.readline()

def get_bills(congress_number, chamber):
    params = {
        "api_key": key,
        "format": "json",
        "offset": 0,
        "limit": 250
    }
    bills = []
    url = f"https://api.congress.gov/v3/bill/{congress_number}/{chamber}"
    response = get(url, params).json()
    while len(response["bills"]) != 0:
        response = get(url, params).json()
        print(response)
        bills.extend(response["bills"])
        params["offset"] += 250
    return bills

def update():
    db = Database()
    for congress_number in range(113, 118):
        current_congress = db.congresses[congress_number]
        bills = get_bills(congress_number)



if __name__ == "__main__":
    key = get_secrets("./secrets.txt")