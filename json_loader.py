import json
import pymongo

congresses = [112, 113, 114, 115, 116]

mongo = None
db = None

def get_secrets(filename: str):
    with open(filename) as file:
        file.readline()
        username = file.readline().strip("\n")
        password = file.readline().strip("\n")
        cluster_name = file.readline().strip("\n")
        mongo_uri = f'mongodb+srv://{username}:{password}@{cluster_name}.buaixd5.mongodb.net/?retryWrites=true&w=majority'
        global mongo
        mongo = pymongo.MongoClient(mongo_uri)
        global db
        db = mongo.PoliSee

if __name__ == "__main__":
    get_secrets("secrets.txt")
    members = {}
    for congress_number in congresses:
        nodes_collection = db[str(congress_number) + "_nodes"]
        edges_collection = db[str(congress_number) + "_edges"]
        nodes = []
        edges = []
        for document in nodes_collection.find():
            nodes.append(document)
            full_name = f"{document['first_name']} {document['last_name']}"
            if full_name not in members:
                members[full_name] = [congress_number]
            else:
                members[full_name].append(congress_number)
        for document in edges_collection.find():
            edges.append(document)
        unified = {
            "nodes": nodes,
            "edges": edges,
        }
        with open(f"./client/public/data/{congress_number}.json", "w") as json_file:
            json.dump(unified, json_file)
        print(f"Done with {congress_number}")
    with open("./client/public/data/index.json", "w") as json_file:
        json.dump(members, json_file)