(async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  await sleep(4000);
  const t = document.body.innerText.replace(/\s+/g, ' ');
  return JSON.stringify({
    url: location.href,
    text: t.slice(0, 2500)
  });
})()
