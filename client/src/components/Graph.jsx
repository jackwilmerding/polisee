import { ForceGraph2D } from "react-force-graph";

import { useContext, useEffect, useState } from "react";

import { AppStateContext } from "./App";
const colorMap = {
  I: "#A56DF0",
  D: "#3689D1",
  R: "#EE8B8B",
  L: "#DAC968",
};

const Graph = () => {
  const { graphData, chamber, focusedMember, congressNumber } =
    useContext(AppStateContext);

  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);

  useEffect(() => {
    console.log(`✅ Updating local graph data: ${chamber}`);

    if (!graphData) return;

    setNodes(graphData.nodes.filter((node) => node.chamber === chamber));
    setLinks(graphData.links);
    // setLinks(graphData.links.filter((link) => link.chamber === chamber));
  }, [chamber, graphData]);

  return (
    <>
      {graphData === null ? (
        <div className="loading">
          Loading data from congress {congressNumber}...
        </div>
      ) : (
        <div style={{ position: "relative" }}>
          <ForceGraph2D
            nodeId="_id"
            linkVisibility="false"
            backgroundColor="#eaeaea"
            nodeColor={(node) => colorMap[node.party] || "#BBBBBB"}
            nodeLabel={(node) => `${node["first_name"]} ${node["last_name"]}`}
            showNavInfo={false}
            graphData={{ nodes, links }}
          />
        </div>
      )}
    </>
  );
};

export default Graph;
