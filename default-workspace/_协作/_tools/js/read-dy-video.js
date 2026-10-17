(async () => {
  await new Promise(r => setTimeout(r, 6000));
  const t = document.body.innerText.replace(/\s+/g, ' ');
  return JSON.stringify({ url: location.href, text: t.slice(0, 1500) });
})()
