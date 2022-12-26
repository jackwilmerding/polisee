import { useState, useContext } from "react";

import { AppStateContext } from "./App";
const ControlPanel = () => {
  const [expanded, setExpanded] = useState(false);

  const { chamber, setChamber, graphType, setGraphType } =
    useContext(AppStateContext);
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
                chamber === "house"
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
                chamber === "senate"
                  ? "btn btn-primary"
                  : "btn btn-outline-primary"
              }
              onClick={() => setChamber("Senate")}
            >
              Senate
            </button>
          </div>
          <div className="lead" style={{ alignSelf: "center" }}>
            Graph Type
          </div>
          <div className="btn-group">
            <button
              type="button"
              className={
                graphType === "2D"
                  ? "btn btn-primary"
                  : "btn btn-outline-primary"
              }
              onClick={() => setGraphType("2D")}
            >
              2D
            </button>
            <button
              type="button"
              className={
                graphType === "3D"
                  ? "btn btn-primary"
                  : "btn btn-outline-primary"
              }
              onClick={() => setGraphType("3D")}
            >
              3D
            </button>
            <button
              type="button"
              className={
                graphType === "VR"
                  ? "btn btn-primary"
                  : "btn btn-outline-primary"
              }
              onClick={() => setGraphType("VR")}
            >
              VR
            </button>
            <button
              type="button"
              className={
                graphType === "AR"
                  ? "btn btn-primary"
                  : "btn btn-outline-primary"
              }
              onClick={() => setGraphType("AR")}
            >
              AR
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
