import React, { useEffect, useRef, useState } from "react";
import loadCongress from "../scripts/loadCongress";
import Graph from "./Graph";
import NavBar from "./Navbar";

export const AppStateContext = React.createContext({});

const App = () => {
  const [graphData, setGraphData] = useState(null);

  const [chamber, setChamber] = useState("house");
  const [congressNumber, setCongressNumber] = useState(116);

  const [focusedMember, setFocusedMember] = useState(null);

  useEffect(() => {
    console.log(
      `✅ UseEffect detected updated congress number: ${congressNumber}`
    );
    (async () => {
      setGraphData(null);

      const { nodes, links } = await loadCongress(congressNumber);

      setGraphData({ nodes, links });
    })();
  }, [congressNumber]);

  return (
    <AppStateContext.Provider
      value={{
        congressNumber,
        setCongressNumber,
        graphData,
        setGraphData,
        chamber,
        setChamber,
        focusedMember,
        setFocusedMember,
      }}
    >
      <>
        <NavBar />
        <Graph />
      </>
    </AppStateContext.Provider>
  );
};

export default App;
