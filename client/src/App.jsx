import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

import {
  ForceGraph2D,
  ForceGraph3D,
  ForceGraphVR,
  ForceGraphAR,
} from "react-force-graph";

const colorMap = {
  0: "gray",
  1: "blue",
  2: "red",
};

const App = () => {
  const [state, setState] = useState({ nodes: [], links: [] });
  useEffect(() => {
    (async () => {
      console.log("🎉 Welcome to Poli See");

      const beforeFetch = Date.now();

      const res = await fetch("/api/116");
      const { nodes, edges: links } = await res.json();

      const fetchTime = Date.now() - beforeFetch;

      console.log(
        `✅ Loaded ${nodes.length} nodes and ${links.length} edges in ${fetchTime}ms`
      );

      setState({ nodes, links });
    })();
  }, []);

  return (
    <div>
      <ForceGraph3D
        graphData={state}
        nodeId="_id"
        nodeColor={(node) => colorMap[node.group]}
        nodeLabel={(node) => `${node.firstName} ${node.lastName}`}
        linkOpacity={0.1}
      />
    </div>
  );
};

export default App;
