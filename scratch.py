import json
from requests import get
import time


key = ""
covered_congresses = [116]


def get_secrets(filename: str):
    with open(filename) as file:
        global key
        key = file.readline().strip("\n")


def get_until_success(endpoint, params):
    try:
        params["api_key"] = key
        params["format"] = "json"
        req = get(endpoint, params)
        while req.status_code != 200:
            print()
            print(f"Error Fetching following endpoint: {endpoint}, {req.text}")
            time.sleep(300)
            req = get(endpoint, params)
        time.sleep(1.4)
        return req.json()
    except:
        print("network did an oopsie")
        # tail recursion go brap brap
        return get_until_success(endpoint, params)


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
        print(
            f"\rFetching House bills: {params['offset']}/{response['pagination']['count']}", end="")
        params["offset"] += 250
        response = get_until_success(url, params)
    url = f"https://api.congress.gov/v3/bill/{congress_number}/s"
    params["offset"] = 0
    response = get_until_success(url, params)
    while len(response["bills"]) != 0:
        bills.extend(response["bills"])
        print(
            f"\rFetching Senate bills: {params['offset']}/{response['pagination']['count']}", end="")
        params["offset"] += 250
        response = get_until_success(url, params)
    return bills


def get_bill_info(bill: dict, congress_number: int):
    params = {
        "api_key": key,
        "format": "json"
    }
    bill_type = bill["type"].upper()
    bill_number = bill["number"]
    current_sponsor = get_until_success(
        f"https://api.congress.gov/v3/bill/{congress_number}/{bill_type}/{bill_number}", params)["bill"]["sponsors"][0]
    if bill_type == "S":
        current_sponsor["chamber"] = "Senate"
    elif bill_type == "HR":
        current_sponsor["chamber"] = "House of Representatives"
    # Fixes J. Gresham Barrett-style names from just being J. Barrett
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



def dict_to_list_no_keys(original: dict):
    new_list = []
    for _, value in original.items():
        new_list.append(value)
    return new_list


def augment_existing_nodes(nodes: dict, edges: dict):
    for key in nodes.keys():
        nodes[key]["aisle_crosses_this_congress"] = get_num_aisle_crosses(nodes[key], nodes, edges)
        nodes[key]["cosponsorships_this_congress"] = get_num_cosponsorships(nodes[key], edges)
        nodes[key]["prolific_rank"] = get_prolific_rank(nodes, nodes[key])
        nodes[key]["bipartisan_rank"] = get_bipartisan_rank(nodes, nodes[key])
        nodes[key]["collaborative_rank"] = get_collaborative_rank(nodes, nodes[key])


def get_num_aisle_crosses(node: dict, nodes: dict, edges: dict):
    aisle_crosses = 0
    for _, edge in edges.items():
        if edge["to_node"] == node["_id"]:
            if nodes[edge["to_node"]]["party"] != node["party"] and node["party"] in ["D", "R"]:
                aisle_crosses += 1
    return aisle_crosses


def get_num_cosponsorships(node: dict, edges: dict):
    cosponsorships = 0
    for _, edge in edges.items():
        if edge["to_node"] == node["_id"]:
            cosponsorships += edge["count"]
    return cosponsorships


def get_prolific_rank(nodes: dict, current_node: dict):
    rank = 1
    for _, node in nodes.items():
        if node["sponsorships_this_congress"] > current_node["sponsorships_this_congress"]:
            rank += 1
    return rank


def get_bipartisan_rank(nodes: dict, current_node: dict):
    rank = 1
    for _, node in nodes.items():
        if node["aisle_crosses_this_congress"] > current_node["aisle_crosses_this_congress"]:
            rank += 1
    return rank


def get_collaborative_rank(nodes: dict, current_node: dict):
    rank = 1
    for _, node in nodes.items():
        if node["cosponsorships_this_congress"] > current_node["cosponsorships_this_congress"]:
            rank += 1
    return rank


def get_congress_data(congress_number: int):
    bills = get_bills(congress_number)
    house_nodes = {}
    house_edges = {}
    senate_nodes = {}
    senate_edges = {}
    ctr = 0
    for bill in bills:
        current_nodes = None
        current_edges = None
        current_chamber = None
        ctr += 1
        current_sponsor, current_cosponsors = get_bill_info(bill, congress_number)
        current_nodes = senate_nodes if bill["type"].upper() == "S" else house_nodes
        current_edges = senate_edges if bill["type"].upper() == "S" else house_edges
        for cosponsor in current_cosponsors:
            edge_tag = f"{current_sponsor['bioguideId']},{cosponsor['bioguideId']}"
            if edge_tag not in current_edges:
                current_edges[edge_tag] = {
                    "from_node": current_sponsor['bioguideId'],
                    "to_node": cosponsor['bioguideId'],
                    "count": 1
                }
            else:
                current_edges[edge_tag]["count"] += 1
            if current_sponsor["bioguideId"] not in current_nodes:
                current_nodes[current_sponsor["bioguideId"]] = {
                    "_id": current_sponsor["bioguideId"],
                    "first_name": current_sponsor["firstName"].upper(),
                    "last_name": current_sponsor["lastName"].upper(),
                    "state": current_sponsor["state"].upper(),
                    "party": current_sponsor["party"][:1].upper(),
                    "image": get_until_success(f"https://api.congress.gov/v3/member/{current_sponsor['bioguideId']}", {})["member"]["depiction"]["imageUrl"],
                    "sponsorships_this_congress": 1,
                }
                print(f"Added member {current_sponsor['firstName']} {current_sponsor['lastName']} from {current_sponsor['state']} to {congress_number}th congress {current_sponsor['chamber']}")
            else:
                current_nodes[current_sponsor["bioguideId"]]["sponsorships_this_congress"] += 1
        print(f"\rHandled base bill {ctr}/{len(bills)}", end="")
    # These two loops handle missing members who have edges but no nodes
    for edge in senate_edges:
        if edge["to_node"] not in senate_nodes:
            member = get_until_success(f"https://api.congress.gov/v3/member/{edge['to_node']}", {})["member"]
            house_nodes[current_sponsor["bioguideId"]] = {
                "_id": edge["to_node"],
                "first_name": member["firstName"].upper(),
                "last_name": member["lastName"].upper(),
                "state": member["state"].upper(),
                "party": member["party"][:1].upper(),
                "image": member["depiction"]["imageUrl"],
                "sponsorships_this_congress": 0,
            }
            print(f"Added missing member {member['firstName']} {member['lastName']} from {member['state']} to {congress_number}th congress in the Senate")
    for edge in house_edges:
        if edge["to_node"] not in house_nodes:
            member = get_until_success(f"https://api.congress.gov/v3/member/{edge['to_node']}", {})["member"]
            house_nodes[current_sponsor["bioguideId"]] = {
                "_id": edge["to_node"],
                "first_name": member["firstName"].upper(),
                "last_name": member["lastName"].upper(),
                "state": member["state"].upper(),
                "party": member["party"][:1].upper(),
                "image": member["depiction"]["imageUrl"],
                "sponsorships_this_congress": 0,
            }
            print(f"Added missing member {member['firstName']} {member['lastName']} from {member['state']} to {congress_number}th congress in the House")
    for edge in senate_edges:
        if edge["to_node"] not in senate_nodes:
            member = get_until_success(f"https://api.congress.gov/v3/member/{edge['to_node']}", {})["member"]
            senate_nodes[current_sponsor["bioguideId"]] = {
                "_id": edge["to_node"],
                "first_name": member["firstName"].upper(),
                "last_name": member["lastName"].upper(),
                "state": member["state"].upper(),
                "party": member["party"][:1].upper(),
                "image": member["depiction"]["imageUrl"],
                "sponsorships_this_congress": 0,
            }
            print(f"Added missing member {member['firstName']} {member['lastName']} from {member['state']} to {congress_number}th congress in the senate")
    # SAVES PROGRESS BEFORE CODE THAT COULD HAVE ERRORS IN IT
    unified_house = {
        "nodes": dict_to_list_no_keys(house_nodes),
        "edges": dict_to_list_no_keys(house_edges),
    }
    unified_senate = {
        "nodes": dict_to_list_no_keys(senate_nodes),
        "edges": dict_to_list_no_keys(senate_edges),
    }
    with open(f"./client/public/data/{congress_number}_senate_intermediate.json", "w") as json_file:
        json.dump(unified_senate, json_file)
    with open(f"./client/public/data/{congress_number}_house_intermediate.json", "w") as json_file:
        json.dump(unified_house, json_file)
    # Redundancy go brap brap
    augment_existing_nodes(senate_nodes, senate_edges)
    augment_existing_nodes(house_nodes, house_edges)
    unified_house = {
        "nodes": dict_to_list_no_keys(house_nodes),
        "edges": dict_to_list_no_keys(house_edges),
    }
    unified_senate = {
        "nodes": dict_to_list_no_keys(senate_nodes),
        "edges": dict_to_list_no_keys(senate_edges),
    }
    with open(f"./client/public/data/{congress_number}_senate.json", "w") as json_file:
        json.dump(unified_senate, json_file)
    with open(f"./client/public/data/{congress_number}_house.json", "w") as json_file:
        json.dump(unified_house, json_file)


def get_index():
    index = {}
    for congress_number in covered_congresses:
        senate_nodes = {}
        with open(f"./client/public/data/{congress_number}_senate.json", "r") as json_file:
            senate_nodes = json.load(json_file)
        house_nodes = {}
        with open(f"./client/public/data/{congress_number}_house.json", "r") as json_file:
            house_nodes = json.load(json_file)
        for _, node in senate_nodes.items():
            unified_name = f"{node['first_name']} {node['last_name']}"
            if unified_name not in index:
                index[unified_name] = {
                    "congresses": [congress_number],
                    "senate": True,
                    "house": False,
                }
            else:
                if congress_number not in index[unified_name]["congresses"]:
                    index[unified_name]["congresses"].append(congress_number)
                index[unified_name]["senate"] = True
        for _, node in house_nodes.items():
            unified_name = f"{node['first_name']} {node['last_name']}"
            if unified_name not in index:
                index[unified_name] = {
                    "congresses": [congress_number],
                    "senate": False,
                    "house": True,
                }
            else:
                if congress_number not in index[unified_name]["congresses"]:
                    index[unified_name]["congresses"].append(congress_number)
                index[unified_name]["house"] = True


if __name__ == "__main__":
    get_secrets("secrets.txt")
    get_congress_data(116)