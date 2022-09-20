import {
  ForceGraph2D,
  ForceGraph3D,
  ForceGraphVR,
  ForceGraphAR,
} from "react-force-graph";

import { useContext, useEffect, useState } from "react";

import { AppStateContext } from "./App";
const colorMap = {
  I: "gray",
  D: "blue",
  R: "red",
};

const Graph = () => {
  const { graphData, chamber, focusedMember } = useContext(AppStateContext);

  const [graphType, setGraphType] = useState("3D");

  useEffect(() => {
    console.log(`✅ UseEffect detected new focused member: ${focusedMember}`);
  }, [focusedMember]);

  // Generate props because I don't want to copy this 4 times lol
  const graphProps = (graphData, chamber) => {
    if (!graphData || !chamber) return null;

    const nodes = graphData.nodes.filter((node) => node.chamber === chamber);
    const links = graphData.links.filter((link) => link.chamber === chamber);
    return {
      graphData: { nodes, links },
      nodeId: "_id",
      linkVisibility: false,
      backgroundColor: "white",
      nodeColor: (node) => colorMap[node.party] || "green",
      nodeLabel: (node) => `${node.firstName} ${node.lastName}`,
      nodeVisibility: (node) => node.chamber === chamber,
      linkOpacity: 0.1,
    };
  };

  return (
    <>
      {graphData === null ? (
        <div className="loading">Loading data...</div>
      ) : (
        <div style={{ position: "relative" }}>
          {graphType === "2D" ? (
            <ForceGraph2D {...graphProps(graphData, chamber)} />
          ) : graphType === "3D" ? (
            <ForceGraph3D {...graphProps(graphData, chamber)} />
          ) : graphType === "VR" ? (
            <ForceGraphVR {...graphProps(graphData, chamber)} />
          ) : graphType === "AR" ? (
            <ForceGraphAR {...graphProps(graphData, chamber)} />
          ) : (
            <></>
          )}
        </div>
      )}
      <div className="btn-group graph-viewmode-selector">
        <button
          type="button"
          className={
            graphType === "2D" ? "btn btn-primary" : "btn btn-outline-primary"
          }
          onClick={() => setGraphType("2D")}
        >
          2D
        </button>
        <button
          type="button"
          className={
            graphType === "3D" ? "btn btn-primary" : "btn btn-outline-primary"
          }
          onClick={() => setGraphType("3D")}
        >
          3D
        </button>
        <button
          type="button"
          className={
            graphType === "VR" ? "btn btn-primary" : "btn btn-outline-primary"
          }
          onClick={() => setGraphType("VR")}
        >
          VR
        </button>
      </div>
    </>
  );
};

export default Graph;
