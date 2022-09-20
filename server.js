import express from "express";
import * as fs from "fs";
import * as dotenv from "dotenv";

import { MongoClient } from "mongodb";
import path, { dirname } from "path";

import { fileURLToPath } from "url";
dotenv.config();

//javascripttttt
const __dirname = dirname(fileURLToPath(import.meta.url));

const client = new MongoClient(process.env.MONGO_URI, {
  useUnifiedTopology: true,
});
const port = process.env.PORT || 3000;
const app = express();

const getDb = async () => {
  await client.connect();
  return client.db("PoliSee");
};

const getCongress = async (congressNumber) => {
  const db = await getDb();
  const url = `cache/${congressNumber}.json`;
  if (fs.existsSync(url)) {
    console.log(`Cache hit! Serving ${url}`);
    return url;
  }

  if (!fs.existsSync("./cache")) {
    fs.mkdirSync("./cache");
  }

  console.log(`Cache miss! Getting from MongoDB 🙄`);

  const nodes = (
    await db.collection(`${congressNumber}_nodes`).find().toArray()
  ).map((node) => ({
    _id: node._id.toString(),
    firstName: node["first_name"],
    lastName: node["last_name"],
    imageUrl: node["image_link"],
    state: node["state"],
    party: node["party"],
    // this line might be bad lol
    chamber: node["chamber"] === "Senate" ? "senate" : "house",
  }));

  //console.table(nodes);

  const links = (
    await db.collection(`${congressNumber}_edges`).find().toArray()
  ).map((node) => ({
    source: node["from_node"],
    target: node["to_node"],
    value: node["count"],
    chamber: node["chamber"] === "Senate" ? "senate" : "house",
  }));

  /// bad zone!!!!
  // 🚨🚨🚨
  //TODO: GET RID OF THIS AND RESET CACHE!!!!!

  /*
  for (let i = 0; i < edges.length; i++) {
    const edge = edges[i];

    const source = nodes.find((node) => node._id === edge.source);

    const target = nodes.find((node) => node._id === edge.target);

    if (!source || !target) {
      console.error(`Found bad edge! Removing ${source} -> ${target}`);
      edges.splice(i, 1);
      i--;
    }
  }
  */
  ///!!!!! BAD!!

  fs.writeFileSync(url, JSON.stringify({ nodes, links }), { flag: "w" });
  return url;
};

// Express land

app.use(express.static(path.join(__dirname, "client/dist")));
app.use(express.json());

app.get("/api/congress/:congressNumber", async (req, res) => {
  const congressNumber = req.params.congressNumber;
  const url = await getCongress(congressNumber);

  res.sendFile(path.join(__dirname, url));
});

app.post("/api/congress/:congressNumber/search", async (req, res) => {
  const db = await getDb();
  const { text } = req.body;
  if (!text) {
    res.status(400).end();
    return;
  }

  console.log(`Searching for ${text}`);
  const results = await db
    .collection(`${req.params.congressNumber}_nodes`)
    .aggregate([
      {
        $search: {
          index: `${req.params.congressNumber}_search`,
          text: {
            query: text,
            fuzzy: {},
            path: {
              wildcard: "*",
            },
          },
        },
      },

      { $limit: 8 },
      {
        $project: {
          _id: 1,
          first_name: 1,
          last_name: 1,
          state: 1,
          party: 1,
          chamber: 1,
          score: { $meta: "searchScore" },
        },
      },
    ])
    .toArray();

  for (const result of results) {
    // Rename result fields to comply with client conventions
    result.firstName = result.first_name;
    result.lastName = result.last_name;

    delete result.first_name;
    delete result.last_name;

    result.chamber = result.chamber === "Senate" ? "senate" : "house";
  }
  console.table(results);

  res.json(results);
});

app.listen(port, () => {
  console.log(`Server is listening on port ${port}`);
});
