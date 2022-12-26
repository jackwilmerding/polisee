import { useState, useContext } from "react";

import { AppStateContext } from "./App";
import searchMembers from "../util/searchMembers";

const CONGRESSES = [112, 113, 114, 115, 116].sort();

const Search = () => {
  const { congressNumber, setCongressNumber } = useContext(AppStateContext);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    const text = e.currentTarget.value;
    if (text === "") {
      setResults(null);
      return;
    }
    setLoading(true);
    const results = await searchMembers(congressNumber, text);
    setResults(results);
    setLoading(false);
  };
  //<div className="top-bar"></div>
  return (
    <>
      <div className="search-container">
        <div className="input-group">
          <div className="input-group-prepend">
            <button
              className="btn btn-primary"
              style={{ borderTopRightRadius: 0, borderBottomRightRadius: 0 }}
            >
              {loading ? (
                <div
                  className="spinner-border spinner-border-sm text-light"
                  role="status"
                >
                  <span className="sr-only"></span>
                </div>
              ) : (
                <i className="bi bi-search"></i>
              )}
            </button>
          </div>
          <input
            type="text"
            className="form-control"
            placeholder="Search members"
            style={{
              borderTopLeftRadius: 0,
              borderBottomLeftRadius: 0,
              //borderRight: 0,
            }}
            onChange={handleSearch}
            onBlur={() => {
              setResults(null);
            }}
          ></input>
          <div className="input-group-append">
            <select
              className="form-select"
              style={{
                borderTopLeftRadius: 0,
                borderBottomLeftRadius: 0,
                borderLeft: 0,
              }}
              value={congressNumber}
              onChange={(e) => {
                //console.log(e.currentTarget.value);
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
        {results && (
          <div className="search-results-container">
            <div className="search-results">
              {results.length === 0 ? (
                <div className="no-results">
                  <i>No results 🙁</i>
                </div>
              ) : (
                results.map((result) => (
                  <div className="search-result" key={result._id}>
                    <div>{`${result.firstName} ${result.lastName}`}</div>
                    <div>{result.party}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Search;
