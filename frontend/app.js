async function loadNews() {
  const response = await fetch("/api/news");
  const data = await response.json();

  const container = document.getElementById("news");
  container.innerHTML = "";

  data.forEach(item => {
    const el = document.createElement("div");
    el.className = "news-item";
    el.innerHTML = `
      <a href="${item.url}" target="_blank">${item.title}</a>
      <div class="meta">${item.source} · ${item.category}</div>
    `;
    container.appendChild(el);
  });
}

loadNews();
