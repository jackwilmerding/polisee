import { useContext } from "react";

import { AppStateContext } from "./App";
import Search from "./Search";

const CONGRESSES = [115, 116, 117].sort();

const NavBar = () => {
  const { congressNumber, setCongressNumber, chamber, setChamber } =
    useContext(AppStateContext);

  return (
    <div className="nav">
      <div className="btn-group nav-left" role="group">
        <button
          type="button"
          className={
            chamber === "house" ? "btn btn-primary" : "btn btn-outline-primary"
          }
          onClick={() => setChamber("house")}
        >
          House
        </button>
        <button
          type="button"
          className={
            chamber === "senate" ? "btn btn-primary" : "btn btn-outline-primary"
          }
          onClick={() => setChamber("senate")}
        >
          Senate
        </button>
      </div>
      <div className="nav-center">
        <Search />
      </div>
      <div className="nav-right">
        <select
          className="form-select"
          value={congressNumber}
          onChange={(e) => {
            console.log(e.currentTarget.value);
            e.preventDefault();
            setCongressNumber(e.currentTarget.value);
          }}
        >
          {CONGRESSES.map((congress) => (
            <option value={congress} key={congress}>
              {congress}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default NavBar;
