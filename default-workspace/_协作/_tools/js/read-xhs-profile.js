(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(6000);
  for (let i = 0; i < 6; i++) {
    window.scrollBy(0, 1200);
    await sleep(1000);
  }
  window.scrollTo(0, 0);
  await sleep(1000);
  const t = document.body.innerText.replace(/\s+/g, ' ');
  return JSON.stringify({ url: location.href, len: t.length, text: t.slice(0, 4500) });
})()
