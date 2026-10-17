(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(5000);
  const seen = new Set();
  for (let i = 0; i < 8; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await sleep(1600);
    const h = document.body.scrollHeight;
    if (seen.has(h)) break;
    seen.add(h);
  }
  window.scrollTo(0, 0);
  await sleep(800);
  const t = document.body.innerText.replace(/\s+/g, ' ');
  return JSON.stringify({
    url: location.href,
    title: document.title,
    len: t.length,
    text: t.slice(0, 5000)
  });
})()
