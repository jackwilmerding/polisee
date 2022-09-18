from requests import *
import pymongo
import time

key = ""
mongo = None
db = None
request_counter = 0


# DONE
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


# DONE
def get_until_success(endpoint, params):
    global request_counter
    request_counter += 1
    req = get(endpoint, params)
    while req.status_code != 200:
        print()
        print(f"Error Fetching following endpoint: {endpoint}")
        time.sleep(300)
        req = get(endpoint, params)
    time.sleep(1.4)
    return req.json()


# DONE
def get_bills(congress_number):
    params = {
        "api_key": key,
        "format": "json",
        "offset": 0,
        "limit": 250
    }
    bills = []
    url = f"https://api.congress.gov/v3/bill/{congress_number}/hr"
    response = get_until_success(url, params)
    while len(response["bills"]) != 0:
        bills.extend(response["bills"])
        print(f"\rFetching House bills: {params['offset']}/{response['pagination']['count']}", end="")
        params["offset"] += 250
        response = get_until_success(url, params)
    url = f"https://api.congress.gov/v3/bill/{congress_number}/s"
    params["offset"] = 0
    response = get_until_success(url, params)
    while len(response["bills"]) != 0:
        bills.extend(response["bills"])
        print(f"\rFetching Senate bills: {params['offset']}/{response['pagination']['count']}", end="")
        params["offset"] += 250
        response = get_until_success(url, params)
    return bills


# DONE
def update_edge(congress_number: int, from_node: str, to_node: str, chamber: str):
    collection = db[str(congress_number) + "_edges"]
    edge_document = collection.find_one({"$and": [{"from_node": from_node}, {"to_node": to_node}, {"chamber": chamber}]})
    if edge_document is not None:
        collection.update_one({"$and": [{"from_node": from_node}, {"to_node": to_node}, {"chamber": chamber}]}, {"$inc": {"count": 1}})
    else:
        doc = {"_id": from_node + "," + to_node, "from_node": from_node, "to_node": to_node, "chamber": chamber, "count": 1}
        collection.insert_one(doc)


# DONE
def update_node(congress_number: int, bioguide_id: str, first_name: str, last_name: str, state: str, party: str, chamber: str):
    collection = db[str(congress_number) + "_nodes"]
    node_document = collection.find_one({"_id": bioguide_id})
    if node_document is not None:
        collection.update_one({"_id": bioguide_id}, {"$inc": {"sponsorships_this_congress": 1}})
    else:
        doc = {"_id": bioguide_id, "first_name": first_name.upper(), "last_name": last_name.upper(), "state": state.upper(), "party": party[:1], "chamber": chamber, "sponsorships_this_congress": 1}
        collection.insert_one(doc)


# DONE
def get_num_cosponsorships(congress_number: int, bioguide_id: str):
    edges = db[str(congress_number) + "_edges"]
    cosponsorships = 0
    for edge in edges.find({"to_node": bioguide_id}):
        cosponsorships += edge["count"]
    return cosponsorships


# DONE
def get_num_aisle_crosses(congress_number: int, bioguide_id: str):
    nodes = db[str(congress_number) + "_nodes"]
    edges = db[str(congress_number) + "_edges"]
    current_node = nodes.find_one({"_id": bioguide_id})
    current_party = current_node["party"]
    # Eliminates third parties
    if current_party not in ["D", "R"]:
        return 0
    # Swaps member party for opposition
    if current_party == "D":
        current_party = "R"
    else:
        current_party = "D"
    aisle_crosses = 0
    for edge in edges.find({"$and": [{"chamber": current_node["chamber"]}, {"from_node": bioguide_id}]}):
        if nodes.find_one({"_id": edge["to_node"]})["party"] == current_party:
            aisle_crosses += edge["count"]
    for edge in edges.find({"$and": [{"chamber": current_node["chamber"]}, {"to_node": bioguide_id}]}):
        if nodes.find_one({"_id": edge["from_node"]})["party"] == current_party:
            aisle_crosses += edge["count"]
    return aisle_crosses


# DONE
def get_prolific_rank(congress_number: int, bioguide_id: str):
    nodes = db[str(congress_number) + "_nodes"]
    current_node = nodes.find_one({"_id": bioguide_id})
    rank = 1
    for node in nodes.find({"chamber": current_node["chamber"]}):
        if node["sponsorships_this_congress"] > current_node["sponsorships_this_congress"]:
            rank += 1
    return rank


# DONE
def get_collaborative_rank(congress_number: int, bioguide_id: str):
    nodes = db[str(congress_number) + "_nodes"]
    current_node = nodes.find_one({"_id": bioguide_id})
    rank = 1
    for node in nodes.find({"chamber": current_node["chamber"]}):
        if node["cosponsorships_this_congress"] > current_node["cosponsorships_this_congress"]:
            rank += 1
    return rank


# DONE
def get_bipartisan_rank(congress_number: int, bioguide_id: str):
    nodes = db[str(congress_number) + "_nodes"]
    current_node = nodes.find_one({"_id": bioguide_id})
    rank = 1
    for node in nodes.find({"chamber": current_node["chamber"]}):
        if node["aisle_crosses_this_congress"] > current_node["aisle_crosses_this_congress"]:
            rank += 1
    return rank


# DONE
def clean_unpaired_ids(congress_number: int):
    params = {
        "api_key": key,
        "format": "json"
    }
    edges = db[str(congress_number) + "_edges"]
    nodes = db[str(congress_number) + "_nodes"]
    for edge in edges.find():
        node_document = nodes.find_one({"_id": edge["to_node"]})
        if node_document is None:
            member = get_until_success(f"https://api.congress.gov/v3/member/{edge['to_node']}", params)["member"]
            print(f"Adding {member['firstName']} {member['lastName']}")
            new_node = {"_id": edge["to_node"], "first_name": member["firstName"].upper(),
                        "last_name": member["lastName"].upper(), "state": member["state"].upper(),
                        "party": member["party"][:1].upper(), "chamber": edge["chamber"],
                        "sponsorships_this_congress": 0}
            nodes.insert_one(new_node)
            print("SUCCESS: Added missing member")


# DONE
def augment_existing_nodes(congress_number: int):
    params = {
        "api_key": key,
        "format": "json"
    }
    nodes = db[str(congress_number) + "_nodes"]
    nodes.update_many({}, {"$set": {"cosponsorships_this_congress": 0}})
    nodes.update_many({}, {"$set": {"aisle_crosses_this_congress": 0}})
    ctr = 0
    for node in nodes.find():
        new_fields = {"cosponsorships_this_congress": get_num_cosponsorships(congress_number, node["_id"]), "aisle_crosses_this_congress": get_num_aisle_crosses(congress_number, node["_id"])}
        nodes.update_one({"_id": node["_id"]}, {"$set": new_fields})
        ctr += 0.5
        print(f"Augmented {ctr} nodes")
    for node in nodes.find():
        member = get_until_success(f"https://api.congress.gov/v3/member/{node['_id']}", params)["member"]
        new_fields = {"prolific_rank": get_prolific_rank(congress_number, node["_id"]),
                      "collaborative_rank": get_collaborative_rank(congress_number, node["_id"]),
                      "bipartisan_rank": get_bipartisan_rank(congress_number, node["_id"]),
                      "image_link": member["depiction"]["imageUrl"]}
        nodes.update_one({"_id": node["_id"]}, {"$set": new_fields})
        ctr += 0.5
        print(f"Augmented {ctr} nodes")


# DONE
def get_bill_info(bill: dict, congress_number: int):
    params = {
        "api_key": key,
        "format": "json"
    }
    bill_type = bill["type"].upper()
    bill_number = bill["number"]
    current_sponsor = get_until_success(f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}", params)["bill"]["sponsors"][0]
    if bill_type == "S":
        current_sponsor["chamber"] = "Senate"
    elif bill_type == "HR":
        current_sponsor["chamber"] = "House of Representatives"
    #Fixes J. Gresham Barrett-style names from just being J. Barrett
    if len(current_sponsor["firstName"]) == 2 and current_sponsor["firstName"][1] == ".":
        current_sponsor["firstName"] += current_sponsor["middleName"]
    params = {
        "api_key": key,
        "format": "json",
        "offset": 0,
        "limit": 250
    }
    current_cosponsors = []
    url = f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}/cosponsors"
    response = get_until_success(url, params)
    while len(response["cosponsors"]) != 0:
        current_cosponsors.extend(response["cosponsors"])
        params["offset"] += 250
        response = get_until_success(url, params)
    return current_sponsor, current_cosponsors


# DONE
def get_congress_data(congress_number: int):
    global request_counter
    bills = get_bills(congress_number)
    ctr = 0
    for bill in bills:
        ctr += 1
        print(f"\rProcessing bills: {ctr}/{len(bills)}; {request_counter} requests", end="")
        current_sponsor, current_cosponsors = get_bill_info(bill, congress_number)
        for cosponsor in current_cosponsors:
            update_edge(congress_number, current_sponsor["bioguideId"], cosponsor["bioguideId"],
                        current_sponsor["chamber"])
        update_node(117, current_sponsor["bioguideId"], current_sponsor["firstName"], current_sponsor["lastName"], current_sponsor["state"], current_sponsor["party"], current_sponsor["chamber"])
    clean_unpaired_ids(congress_number)
    augment_existing_nodes(congress_number)


# TODO TEMP
def fix_sponsorless_congress(congress_number: int):
    bills = get_bills(congress_number)
    nodes = db[str(congress_number) + "_nodes"]
    print(f"Initializing {congress_number} sponsorship counts...")
    nodes.update_many({}, {"$set": {"sponsorships_this_congress": 0}})
    print("Done")
    params = {
        "api_key": key,
        "format": "json"
    }
    ctr = 0
    for bill in bills:
        bill_type = bill["type"].upper()
        bill_number = bill["number"]
        current_sponsor = get_until_success(f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}", params)["bill"]["sponsors"][0]
        current_node = nodes.find_one({"_id": current_sponsor["bioguideId"]})
        if current_node is None:
            continue
        current_sponsorships = current_node["sponsorships_this_congress"] + 1
        nodes.update_one({"_id": current_sponsor["bioguideId"]}, {"$set": {"sponsorships_this_congress": current_sponsorships}})
        ctr += 1
        print(f"\rFixing nodes: {ctr}/{len(bills)} of the way there; {request_counter} requests", end="")


if __name__ == "__main__":
    get_secrets("./secrets.txt")
    augment_existing_nodes(116)
    db.drop_collection("115_nodes")
    db.drop_collection("115_edges")
    get_congress_data(115)
    db.drop_collection("116_nodes")
    db.drop_collection("116_edges")
    get_congress_data(116)
    get_congress_data(114)
    get_congress_data(113)
    get_congress_data(112)
