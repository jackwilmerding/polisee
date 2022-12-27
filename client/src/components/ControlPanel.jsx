import { useState, useContext } from "react";

import { AppStateContext } from "./App";
const ControlPanel = () => {
  const [expanded, setExpanded] = useState(false);

  const { chamber, setChamber } = useContext(AppStateContext);
  return (
    <>
      <div
        className={`control-center`}
        onClick={() => {
          setExpanded((c) => !c);
        }}
      >
        <i className="bi bi-list"></i>
      </div>
      {expanded && (
        <div className="control-panel">
          <div className="lead" style={{ alignSelf: "center" }}>
            Chamber
          </div>
          <div className="btn-group" role="group">
            <button
              type="button"
              className={
                chamber === "House of Representatives"
                  ? "btn btn-primary"
                  : "btn btn-outline-primary"
              }
              onClick={() => setChamber("House of Representatives")}
            >
              House
            </button>
            <button
              type="button"
              className={
                chamber === "Senate"
                  ? "btn btn-primary"
                  : "btn btn-outline-primary"
              }
              onClick={() => setChamber("Senate")}
            >
              Senate
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default ControlPanel;

/*

*/
