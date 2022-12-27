import fs from "node:fs";

fs.writeFileSync("dist/CNAME", "polisee.net", (err) => {});
fs.writeFileSync("dist/.nojekyll", " ", (err) => {});

console.log("Added CNAME and .nojekyll files");
