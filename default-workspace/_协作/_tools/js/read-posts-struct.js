(() => {
  const clean = e => (e ? e.innerText.replace(/\s+/g, ' ').trim() : null);
  const list = document.querySelector('[data-e2e="user-post-list"]');
  let items = [];
  let liCount = -1;
  let childCount = -1;
  if (list) {
    const lis = list.querySelectorAll('li');
    liCount = lis.length;
    childCount = list.children.length;
    if (lis.length) {
      items = [...lis].map(li => li.innerText.replace(/\s+/g, ' ').trim());
    } else {
      items = [...list.children].map(c => c.innerText.replace(/\s+/g, ' ').trim());
    }
  }
  return JSON.stringify({
    tabCount: clean(document.querySelector('[data-e2e="user-tab-count"]')),
    workTab: clean(document.querySelector('[data-e2e="user-work-tab"]')),
    follow: clean(document.querySelector('[data-e2e="user-info-follow"]')),
    fans: clean(document.querySelector('[data-e2e="user-info-fans"]')),
    like: clean(document.querySelector('[data-e2e="user-info-like"]')),
    liCount: liCount,
    childCount: childCount,
    itemCount: items.length,
    items: items
  });
})()
