(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(6000);
  let last = 0;
  for (let i = 0; i < 18; i++) {
    window.scrollBy(0, 1500);
    await sleep(1100);
    window.scrollTo(0, document.body.scrollHeight);
    await sleep(1100);
    const h = document.body.scrollHeight;
    if (h === last && i > 6) break;
    last = h;
  }
  await sleep(2500);
  const t = document.body.innerText.replace(/\s+/g, ' ');
  const a = t.indexOf('搜索 Ta 的作品');
  const b = t.indexOf('广告投放');
  const body = a >= 0 ? t.slice(a, b > a ? b : undefined) : t;
  return JSON.stringify({ len: t.length, body: body.slice(0, 5000) });
})()
