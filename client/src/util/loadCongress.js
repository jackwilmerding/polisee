const loadCongress = async (congress) => {
  const beforeFetch = Date.now();
  const res = await fetch(`/data/${congress}.json`);
  const { nodes, edges } = await res.json();

  const fetchTime = Date.now() - beforeFetch;

  console.log(
    `✅ Loaded ${nodes.length} nodes and ${edges.length} edges in ${fetchTime}ms`
  );

  return {
    nodes,
    links: edges.map((link) => {
      return {
        source: link["to_node"],
        target: link["from_node"],
        chamber: link.chamber,
      };
    }),
  };
};

export default loadCongress;
