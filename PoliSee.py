from requests import *
import pymongo

key = ""
congresses = [113, 114, 115, 116, 117]
mongo = None

class Member:
    def __init__(self, name: str, state : str, party: str):
        self.name = name
        self.state = state
        self.party = party[:1]
        self.colleagues = {}

class Congress:
    def __init__(self, congress_number: int):
        self.congress_number = congress_number
        self.senate = {}
        self.house = {}

class Database:
    def __init__(self):
        self.congresses = {}
        for i in congresses:
            self.congresses[i] = Congress(i)

def get_secrets(filename: str):
    with open(filename) as file:
        key = file.readline()
        username = file.readline()
        password = file.readline()
        cluster_name = file.readline()
        #TODO FIX
        mongo_uri = f'mongodb+srv://{username}:{password}@{cluster_name}.buaixd5.mongodb.net/?retryWrites=true&w=majority'
        client = client = pymongo.MongoClient(mongo_uri)

def get_bills(congress_number):
    params = {
        "api_key": key,
        "format": "json",
        "offset": 0,
        "limit": 250
    }
    bills = []
    url = f"https://api.congress.gov/v3/bill/{congress_number}"
    response = get(url, params).json()
    while len(response["bills"]) != 0:
        response = get(url, params).json()
        print(response)
        bills.extend(response["bills"])
        params["offset"] += 250
    return bills

def init():
    db = Database()
    params = {
        "api_key": key,
        "format": "json",
    }
    for congress_number in congresses:
        current_congress = db.congresses[congress_number]
        bills = get_bills(congress_number)
        #for bill in bills:
        for bill in bills[:5]:
            bill_type = bill["type"]
            bill_number = bill["number"]
            current_sponsor = get(f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}", params)["sponsors"][0]
            current_cosponsors = get(f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}/cosponsors", params)["cosponsors"]
            if bill_type == "S":
                current_chamber = current_congress.senate
            elif bill_type == "HR":
                current_chamber = current_congress.senate
            if current_chamber.has_key(current_sponsor["bioguideId"]):
                for cosponsor in current_cosponsors:
                    if current_chamber[current_sponsor].colleagues.has_key(cosponsor["bioguideId"]):
                        current_chamber[current_sponsor].colleagues[cosponsor["bioguideId"]] = 1
                    else:
                        current_chamber[current_sponsor].colleagues[cosponsor["bioguideId"]] += 1
            else:
                current_chamber[current_sponsor["bioguideId"]] = Member("Hon. " + current_sponsor["firstName"] + current_sponsor["lastName"], current_sponsor["state"], current_sponsor["party"])
        #TODO UPLOAD CURRENT CONGRESS


if __name__ == "__main__":
    key = get_secrets("./secrets.txt")