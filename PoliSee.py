from requests import *
import pymongo
import time

key = ""
#TODO Expand for production
congresses = [117]
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
    return(req.json())


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
def update_edge(congress_number: int, from_node: str, to_node: str):
    collection = db[str(congress_number) + "_edges"]
    edge_document = collection.find_one({"$and": [{"from_node": from_node}, {"to_node": to_node}]})
    if edge_document != None:
        current_count = edge_document["count"]
        collection.update_one({"$and": [{"from_node": from_node}, {"to_node": to_node}]}, {"$set": {"count" : current_count + 1}})
    else:
        doc = {}
        doc["_id"] = from_node + "," + to_node
        doc["from_node"] = from_node
        doc["to_node"] = to_node
        doc["count"] = 1
        collection.insert_one(doc)


#DONE
def update_node(congress_number: int, bioguide_id: str, first_name: str, last_name: str, state: str, party: str, type: str):
    collection = db[str(congress_number) + "_edges"]
    edge_document = collection.find_one({"_id": bioguide_id})
    doc = {}
    doc["_id"] = bioguide_id
    doc["first_name"] = first_name.capitalize()
    doc["last_name"] = last_name.capitalize()
    doc["state"] = state.upper()
    doc["party"] = party[:1]
    doc["type"] = type
    if edge_document != None:
        collection.replace_one({"_id": bioguide_id}, doc)
    else:
        collection.insert_one(doc)


def init():
    global request_counter
    params = {
        "api_key": key,
        "format": "json"
    }
    #TODO CLEAN UP
    for congress_number in congresses:
        bills = get_bills(congress_number)
        ctr = 0
        for bill in bills[0:5]:
            ctr += 1
            print(f"\rProcessing bills: {ctr}/{len(bills)}; {request_counter} requests", end = "")
            bill_type = bill["type"]
            bill_number = bill["number"]
            current_sponsor = get(f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}", params).json()["bill"]["sponsors"][0]
            current_cosponsors = get(f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}/cosponsors", params).json()["cosponsors"]
            request_counter += 2
            if bill_type == "S":
                member_type = "Senator"
            elif bill_type == "HR":
                member_type = "Representative"
            if current_sponsor["bioguideId"] not in current_congress.members:
                current_congress.members[current_sponsor["bioguideId"]] = Member(current_sponsor["bioguideId"], "Hon. " + current_sponsor["firstName"].capitalize() + " " + current_sponsor["lastName"].capitalize(), current_sponsor["state"], current_sponsor["party"], member_type)
            for cosponsor in current_cosponsors:
                if cosponsor["bioguideId"] not in current_congress.members[current_sponsor["bioguideId"]].colleagues:
                    current_congress.members[current_sponsor["bioguideId"]].colleagues[cosponsor["bioguideId"]] = 1
                else:
                    current_congress.members[current_sponsor["bioguideId"]].colleagues[cosponsor["bioguideId"]] += 1
        collection.insert_many(current_congress.pack())


if __name__ == "__main__":
    start = time.time()
    get_secrets("./secrets.txt")
    update_edge(117, "12244l", "sdafdas")