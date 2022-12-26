const loadCongress = async (congress) => {
  const beforeFetch = Date.now();
  const res = await fetch(`/data/${congress}.json`);
  const { nodes, edges } = await res.json();

  const fetchTime = Date.now() - beforeFetch;

  console.log(
    `✅ Loaded ${nodes.length} nodes and ${edges.length} edges in ${fetchTime}ms`
  );

  return { nodes, links: edges };
};

export default loadCongress;
