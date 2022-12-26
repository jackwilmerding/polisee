import ghpages from "gh-pages";
import fs from "node:fs";

fs.writeFile("dist/CNAME", "polisee.net", function (err) {});
ghpages.publish("dist", function (err) {});
