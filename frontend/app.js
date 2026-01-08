const state = {
  limit: 20,
  offset: 0,
  category: "",
  q: ""
};

function fmtDate(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, { year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" });
  } catch {
    return iso;
  }
}

function setStatus(text) {
  const el = document.getElementById("status");
  el.textContent = text;
}

async function loadHealth() {
  try {
    const r = await fetch("/health", { cache: "no-store" });
    if (!r.ok) throw new Error("health not ok");
    setStatus("ok");
  } catch {
    setStatus("offline");
  }
}

async function loadCategories() {
  const sel = document.getElementById("category");
  sel.innerHTML = "";

  const optAll = document.createElement("option");
  optAll.value = "";
  optAll.textContent = "Все категории";
  sel.appendChild(optAll);

  try {
    const r = await fetch("/sources", { cache: "no-store" });
    if (!r.ok) throw new Error("sources failed");
    const sources = await r.json();

    const cats = new Set();
    sources.forEach(s => {
      if (s.category) cats.add(s.category);
    });

    Array.from(cats).sort().forEach(c => {
      const opt = document.createElement("option");
      opt.value = c;
      opt.textContent = c;
      sel.appendChild(opt);
    });
  } catch {
    // если sources не доступны — оставляет только "Все категории"
  }
}

function buildNewsUrl() {
  const params = new URLSearchParams();
  params.set("limit", String(state.limit));
  params.set("offset", String(state.offset));
  if (state.category) params.set("category", state.category);
  if (state.q) params.set("q", state.q);
  return `/news?${params.toString()}`;
}

async function loadNews() {
  const url = buildNewsUrl();
  const feed = document.getElementById("feed");
  feed.innerHTML = "";

  const r = await fetch(url, { cache: "no-store" });
  if (!r.ok) {
    feed.innerHTML = `<div class="card">Ошибка загрузки ленты: ${r.status}</div>`;
    return;
  }

  const items = await r.json();
  if (!Array.isArray(items) || items.length === 0) {
    feed.innerHTML = `<div class="card">Пока пусто. Добавь источники в /sources и подожди цикл сборщика.</div>`;
    updatePagerInfo(0);
    return;
  }

  items.forEach(n => {
    const card = document.createElement("div");
    card.className = "card";

    const source = n.source_name ? n.source_name : `source#${n.source_id}`;
    const pub = n.published_at ? fmtDate(n.published_at) : "";

    card.innerHTML = `
      <a href="${n.url}" target="_blank" rel="noreferrer">${escapeHtml(n.title)}</a>
      <div class="meta">
        <span class="badge">${escapeHtml(n.category)}</span>
        <span>${escapeHtml(source)}</span>
        <span>${escapeHtml(pub)}</span>
      </div>
    `;
    feed.appendChild(card);
  });

  updatePagerInfo(items.length);
}

function updatePagerInfo(count) {
  const page = Math.floor(state.offset / state.limit) + 1;
  document.getElementById("pageInfo").textContent = `стр. ${page} · показано ${count}`;
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function applyFilters() {
  const q = document.getElementById("q").value.trim();
  const category = document.getElementById("category").value;

  state.q = q;
  state.category = category;
  state.offset = 0;
  loadNews();
}

function nextPage() {
  state.offset += state.limit;
  loadNews();
}

function prevPage() {
  state.offset = Math.max(0, state.offset - state.limit);
  loadNews();
}

document.getElementById("apply").addEventListener("click", applyFilters);
document.getElementById("next").addEventListener("click", nextPage);
document.getElementById("prev").addEventListener("click", prevPage);

(async function init() {
  await loadHealth();
  await loadCategories();
  await loadNews();
})();
