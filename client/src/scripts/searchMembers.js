const searchMembers = async (congress, text) => {
  const beforeFetch = Date.now();
  const res = await fetch(`/api/congress/${congress}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  const results = await res.json();

  const fetchTime = Date.now() - beforeFetch;

  console.log(
    `✅ Found ${results.length} results ${text} (${congress}) in ${fetchTime}ms`
  );
  return results;
};

export default searchMembers;
