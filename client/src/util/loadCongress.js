const loadCongress = async (congress) => {
  const beforeFetch = Date.now();
  const res = await fetch(`/data/${congress}.json`);
  const { nodes, links } = await res.json();

  const fetchTime = Date.now() - beforeFetch;

  console.log(
    `✅ Loaded ${nodes.length} nodes and ${links.length} edges in ${fetchTime}ms`
  );

  return { nodes, links };
};

export default loadCongress;
