import { useState, useContext } from "react";

import { AppStateContext } from "./App";
import searchMembers from "../scripts/searchMembers";

const Search = () => {
  const { congressNumber } = useContext(AppStateContext);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    setLoading(true);
    const results = await searchMembers(congressNumber, e.currentTarget.value);
    setResults(results);
    setLoading(false);
  };
  return (
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
          style={{ borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }}
          onChange={handleSearch}
        ></input>
      </div>
      {results.map((result) => (
        <div className="search-result" key={result._id}>
          <div>{`${result.firstName} ${result.lastName}`}</div>
          <div>{result.party}</div>
        </div>
      ))}
    </div>
  );
};

export default Search;
