import React, { useEffect, useRef, useState } from "react";
import loadCongress from "../util/loadCongress";
import Graph from "./Graph";
import Search from "./Search";
import ControlPanel from "./ControlPanel";

export const AppStateContext = React.createContext({});

const App = () => {
  const [graphData, setGraphData] = useState(null);

  const [chamber, setChamber] = useState("Senate");
  const [congressNumber, setCongressNumber] = useState(112);

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
    // React state management go brrr
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
        <Search />
        <ControlPanel />
        <Graph />
      </>
    </AppStateContext.Provider>
  );
};

export default App;
