"use strict";

const state = {
  items: [],
  options: {},
  query: "",
  contentType: "all",
  tool: "all",
  tag: "all"
};

const els = {
  search: document.querySelector("#library-search"),
  contentTypes: document.querySelector("#content-type-filters"),
  tool: document.querySelector("#tool-filter"),
  tag: document.querySelector("#tag-filter"),
  clear: document.querySelector("#clear-filters"),
  grid: document.querySelector("#library-grid"),
  count: document.querySelector("#results-count"),
  empty: document.querySelector("#empty-state"),
  emptyTitle: document.querySelector("#empty-title"),
  emptyCopy: document.querySelector("#empty-copy"),
  error: document.querySelector("#load-error")
};

function text(value) {
  return String(value ?? "").trim();
}

function normalize(value) {
  return text(value).toLocaleLowerCase();
}

function humanize(value) {
  return text(value)
    .replaceAll("-", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function displayContentType(item) {
  if (normalize(item.content_type) === "other" && text(item.other_label)) {
    return text(item.other_label);
  }
  return text(item.content_type);
}

function itemDate(item) {
  return Date.parse(item.updated || item.created || "1970-01-01") || 0;
}

function sortedItems(items) {
  return [...items].sort((a, b) => itemDate(b) - itemDate(a) || text(a.title).localeCompare(text(b.title)));
}

function makeElement(tag, className, content) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (content !== undefined) element.textContent = content;
  return element;
}

function uniqueSorted(values) {
  return [...new Set(values.map(text).filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

function setControlsDisabled(disabled) {
  els.search.disabled = disabled;
  els.tool.disabled = disabled;
  els.tag.disabled = disabled;
  els.clear.disabled = disabled;
}

function populateSelect(select, values, allLabel) {
  const current = select.value || "all";
  select.replaceChildren();

  const allOption = new Option(allLabel, "all");
  select.add(allOption);

  values.forEach((value) => select.add(new Option(value, value)));
  select.value = values.includes(current) ? current : "all";
}

function buildContentTypeFilters() {
  els.contentTypes.replaceChildren();

  const buttonValues = ["all"];
  const configured = Array.isArray(state.options.content_types) ? state.options.content_types : [];
  configured.forEach((contentType) => {
    if (state.items.some((item) => item.content_type === contentType)) {
      buttonValues.push(contentType);
    }
  });

  const unconfigured = uniqueSorted(
    state.items.map((item) => item.content_type).filter((value) => !configured.includes(value))
  );
  buttonValues.push(...unconfigured);

  buttonValues.forEach((value) => {
    const button = makeElement("button", "filter-pill", value === "all" ? "All" : value);
    button.type = "button";
    button.dataset.value = value;
    const active = state.contentType === value;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
    button.addEventListener("click", () => {
      state.contentType = value;
      buildContentTypeFilters();
      render();
    });
    els.contentTypes.append(button);
  });
}

function buildSecondaryFilters() {
  const tools = uniqueSorted(state.items.flatMap((item) => Array.isArray(item.tools) ? item.tools : []));
  const tags = uniqueSorted(state.items.flatMap((item) => Array.isArray(item.tags) ? item.tags : []));
  populateSelect(els.tool, tools, "All tools");
  populateSelect(els.tag, tags, "All tags");
}

function searchableText(item) {
  return normalize([
    item.title,
    item.summary,
    item.content_type,
    item.other_label,
    item.format,
    item.library_status,
    item.portfolio_status,
    ...(Array.isArray(item.tools) ? item.tools : []),
    ...(Array.isArray(item.tags) ? item.tags : [])
  ].join(" "));
}

function matchesFilters(item) {
  const queryMatch = !state.query || searchableText(item).includes(normalize(state.query));
  const typeMatch = state.contentType === "all" || item.content_type === state.contentType;
  const toolMatch = state.tool === "all" || (item.tools || []).includes(state.tool);
  const tagMatch = state.tag === "all" || (item.tags || []).includes(state.tag);
  return queryMatch && typeMatch && toolMatch && tagMatch;
}

function metaLine(label, value) {
  const line = makeElement("div", "meta-line");
  line.append(makeElement("span", "meta-label", `${label}:`));
  line.append(makeElement("span", "meta-value", value));
  return line;
}

function createCard(item) {
  const card = makeElement("article", "library-card");
  if (normalize(item.library_status) === "archived") card.classList.add("is-archived");

  const top = makeElement("div", "card-topline");
  top.append(makeElement("span", "card-type", displayContentType(item)));

  const status = makeElement("span", "status-badge", humanize(item.library_status));
  status.dataset.status = normalize(item.library_status);
  top.append(status);
  card.append(top);

  card.append(makeElement("h3", "card-title", text(item.title)));
  card.append(makeElement("p", "card-summary", text(item.summary)));

  const meta = makeElement("div", "card-meta");
  meta.append(metaLine("Format", text(item.format)));

  const tools = Array.isArray(item.tools) ? item.tools.filter(Boolean).join(" · ") : "";
  if (tools) meta.append(metaLine("Tools", tools));

  if (item.portfolio_status && item.portfolio_status !== "library-only") {
    meta.append(metaLine("Portfolio", humanize(item.portfolio_status)));
  }
  card.append(meta);

  if (Array.isArray(item.tags) && item.tags.length) {
    const tags = makeElement("div", "tag-list");
    item.tags.forEach((tag) => tags.append(makeElement("span", "tag-chip", tag)));
    card.append(tags);
  }

  return card;
}

function renderEmpty(filteredItems) {
  const hasItems = state.items.length > 0;
  const hasMatches = filteredItems.length > 0;

  els.empty.hidden = hasMatches;
  if (hasMatches) return;

  if (!hasItems) {
    els.emptyTitle.textContent = "The shelves are ready.";
    els.emptyCopy.textContent = "Library items will appear here as they are added.";
  } else {
    els.emptyTitle.textContent = "No matches found.";
    els.emptyCopy.textContent = "Try a different search term or clear one of the filters.";
  }
}

function render() {
  const filtered = sortedItems(state.items.filter(matchesFilters));
  els.grid.replaceChildren(...filtered.map(createCard));

  const noun = filtered.length === 1 ? "item" : "items";
  els.count.textContent = `${filtered.length} ${noun}`;
  renderEmpty(filtered);
}

function clearFilters() {
  state.query = "";
  state.contentType = "all";
  state.tool = "all";
  state.tag = "all";
  els.search.value = "";
  els.tool.value = "all";
  els.tag.value = "all";
  buildContentTypeFilters();
  render();
  els.search.focus();
}

function bindEvents() {
  els.search.addEventListener("input", (event) => {
    state.query = event.target.value;
    render();
  });

  els.tool.addEventListener("change", (event) => {
    state.tool = event.target.value;
    render();
  });

  els.tag.addEventListener("change", (event) => {
    state.tag = event.target.value;
    render();
  });

  els.clear.addEventListener("click", clearFilters);
}

async function loadJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} returned ${response.status}`);
  return response.json();
}

async function init() {
  bindEvents();
  setControlsDisabled(true);

  try {
    const [items, options] = await Promise.all([
      loadJson("library-data/items.json"),
      loadJson("library-data/options.json")
    ]);

    state.items = Array.isArray(items) ? items : [];
    state.options = options && typeof options === "object" ? options : {};

    buildContentTypeFilters();
    buildSecondaryFilters();
    setControlsDisabled(state.items.length === 0);
    render();
  } catch (error) {
    console.error("Learning Content Lab failed to load:", error);
    els.count.textContent = "Library unavailable";
    els.error.hidden = false;
    setControlsDisabled(true);
  }
}

init();
