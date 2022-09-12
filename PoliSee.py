from requests import *
import pymongo
import time

key = ""
congresses = [113, 114, 115, 116, 117]
mongo = None
db = None
request_counter = 0

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
        global key
        key = file.readline().strip("\n")
        username = file.readline().strip("\n")
        password = file.readline().strip("\n")
        cluster_name = file.readline().strip("\n")
        mongo_uri = f'mongodb+srv://{username}:{password}@{cluster_name}.buaixd5.mongodb.net/?retryWrites=true&w=majority'
        global mongo
        mongo = pymongo.MongoClient(mongo_uri)
        global db
        db = mongo.get_database("congresses")

def get_bills(congress_number):
    global request_counter
    params = {
        "api_key": key,
        "format": "json",
        "offset": 0,
        "limit": 250
    }
    bills = []
    url = f"https://api.congress.gov/v3/bill/{congress_number}/hr"
    response = get(url, params).json()
    request_counter += 1
    while len(response["bills"]) != 0:
        print(f"\rFetching House bills: {params['offset']}/{response['pagination']['count']}", end = "")
        response = get(url, params).json()
        request_counter += 1
        bills.extend(response["bills"])
        params["offset"] += 250
    url = f"https://api.congress.gov/v3/bill/{congress_number}/s"
    params["offset"] = 0
    response = get(url, params).json()
    request_counter += 1
    while len(response["bills"]) != 0:
        print(f"\rFetching Senate bills: {params['offset']}/{response['pagination']['count']}", end = "")
        request_counter += 1
        response = get(url, params).json()
        bills.extend(response["bills"])
        params["offset"] += 250
    return bills

def init():
    global request_counter
    new_db = Database()
    params = {
        "api_key": key,
        "format": "json"
    }
    #TODO FIX
    for congress_number in [117]:
        current_congress = new_db.congresses[congress_number]
        bills = get_bills(congress_number)
        ctr = 0
        for bill in bills:
            ctr += 1
            print(f"\rProcessing bills: {ctr}/{len(bills)}; {request_counter} requests", end = "")
            bill_type = bill["type"]
            bill_number = bill["number"]
            current_sponsor = get(f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}", params).json()["bill"]["sponsors"][0]
            current_cosponsors = get(f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}/cosponsors", params).json()["cosponsors"]
            request_counter += 2
            if bill_type == "S":
                current_chamber = current_congress.senate
            elif bill_type == "HR":
                current_chamber = current_congress.senate
            if current_sponsor["bioguideId"] not in current_chamber:
                current_chamber[current_sponsor["bioguideId"]] = Member("Hon. " + current_sponsor["firstName"] + current_sponsor["lastName"], current_sponsor["state"], current_sponsor["party"])
            for cosponsor in current_cosponsors:
                if cosponsor["bioguideId"] not in current_chamber[current_sponsor["bioguideId"]].colleagues:
                    current_chamber[current_sponsor["bioguideId"]].colleagues[cosponsor["bioguideId"]] = 1
                else:
                    current_chamber[current_sponsor["bioguideId"]].colleagues[cosponsor["bioguideId"]] += 1


if __name__ == "__main__":
    start = time.time()
    get_secrets("./secrets.txt")
    try:
        init()
        print(time.time() - start)
    except:
        print(time.time() - start)