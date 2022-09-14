from requests import *
import pymongo
import time

key = ""
#TODO Expand for production
congresses = [116]
mongo = None
db = None
collection = None
request_counter = 0


#DONE
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
        db = mongo.PoliSee


#DONE
def get_until_success(endpoint, params):
    req = get(endpoint, params)
    while req.status_code != 200:
        time.sleep(60)
        req = get(endpoint, params).json()
    time.sleep(1.2)
    return req.json()


#DONE
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
    response = get_until_success(url, params)
    request_counter += 1
    while len(response["bills"]) != 0:
        bills.extend(response["bills"])
        print(f"\rFetching House bills: {params['offset']}/{response['pagination']['count']}", end = "")
        response = get_until_success(url, params)
        request_counter += 1
        params["offset"] += 250
    url = f"https://api.congress.gov/v3/bill/{congress_number}/s"
    params["offset"] = 0
    response = get_until_success(url, params)
    request_counter += 1
    while len(response["bills"]) != 0:
        bills.extend(response["bills"])
        print(f"\rFetching Senate bills: {params['offset']}/{response['pagination']['count']}", end = "")
        request_counter += 1
        response = get_until_success(url, params)
        params["offset"] += 250
    return bills


#DONE
def update_edge(congress_number: int, from_node: str, to_node: str, chamber: str):
    collection = db[str(congress_number) + "_edges"]
    edge_document = collection.find_one({"$and": [{"from_node": from_node}, {"to_node": to_node}]})
    if edge_document != None:
        current_count = edge_document["count"]
        collection.update_one({"$and": [{"from_node": from_node}, {"to_node": to_node}, {"chamber" : chamber}]}, {"$set": {"count" : current_count + 1}})
    else:
        doc = {}
        doc["_id"] = from_node + "," + to_node
        doc["from_node"] = from_node
        doc["to_node"] = to_node
        doc["chamber"] = chamber
        doc["count"] = 1
        collection.insert_one(doc)


#DONE
def update_node(congress_number: int, bioguide_id: str, first_name: str, last_name: str, state: str, party: str, chamber: str):
    collection = db[str(congress_number) + "_nodes"]
    node_document = collection.find_one({"_id": bioguide_id})
    doc = {}
    doc["_id"] = bioguide_id
    doc["first_name"] = first_name.capitalize()
    doc["last_name"] = last_name.capitalize()
    doc["state"] = state.upper()
    doc["party"] = party[:1]
    doc["chamber"] = chamber
    if node_document != None:
        collection.replace_one({"_id": bioguide_id}, doc)
    else:
        collection.insert_one(doc)


#DONE
def get_bill_info(bill, congress_number):
    global request_counter
    params = {
        "api_key": key,
        "format": "json"
    }
    bill_type = bill["type"]
    bill_number = bill["number"]
    current_sponsor = get_until_success(f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}", params)["bill"]["sponsors"][0]
    current_cosponsors = get_until_success(f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}/cosponsors", params)["cosponsors"]
    if bill_type == "S":
        current_sponsor["chamber"] = "Senate"
    elif bill_type == "HR":
        current_sponsor["chamber"] = "House of Representatives"
    request_counter += 2
    return current_sponsor, current_cosponsors

#DONE
def get_congress_data(congress_number):
    global request_counter
    bills = get_bills(congress_number)
    ctr = 0
    for bill in bills:
        ctr += 1
        print(f"\rProcessing bills: {ctr}/{len(bills)}; {request_counter} requests", end="")
        current_sponsor, current_cosponsors = get_bill_info(bill, congress_number)
        for cosponsor in current_cosponsors:
            update_node(congress_number, current_sponsor["bioguideId"], current_sponsor["firstName"], current_sponsor["lastName"], current_sponsor["state"], current_sponsor["party"], current_sponsor["chamber"])
            update_edge(congress_number, current_sponsor["bioguideId"], cosponsor["bioguideId"], current_sponsor["chamber"])


if __name__ == "__main__":
    start = time.time()
    get_secrets("./secrets.txt")
    get_congress_data(116)