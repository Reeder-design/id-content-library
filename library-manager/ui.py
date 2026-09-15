from __future__ import annotations

import html
from collections.abc import Iterable


def esc(value) -> str:
    return html.escape(str(value or ""), quote=True)


def as_text(item, key: str) -> str:
    value = item.get(key, "") if hasattr(item, "get") else ""
    if isinstance(value, list):
        return ", ".join(str(part) for part in value)
    return str(value or "")


def selected(value, current) -> str:
    return " selected" if str(value) == str(current or "") else ""


def options_html(values: Iterable[str], current="", *, blank_label: str | None = None) -> str:
    rows = []
    if blank_label is not None:
        rows.append(f'<option value="">{esc(blank_label)}</option>')
    for value in values:
        rows.append(f'<option value="{esc(value)}"{selected(value, current)}>{esc(value)}</option>')
    return "".join(rows)


def layout(title: str, body: str, messages: list[tuple[str, str]], urls: dict[str, str]) -> str:
    flashes = "".join(
        f'<div class="flash flash-{esc(category)}">{esc(message)}</div>' for category, message in messages
    )
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)} | Library Manager</title>
  <link rel="stylesheet" href="{esc(urls['css'])}">
</head>
<body>
  <header class="manager-header">
    <div class="shell header-row">
      <a class="brand" href="{esc(urls['library'])}"><span class="brand-mark">L</span><span>Library Manager</span></a>
      <nav><a href="{esc(urls['library'])}">Library</a><a class="button" href="{esc(urls['add'])}">Add Item</a></nav>
    </div>
  </header>
  <main class="shell manager-main">{flashes}{body}</main>
  <script src="{esc(urls['js'])}"></script>
</body>
</html>'''


def library_body(items: list[dict], csrf: str, route_urls: dict[str, callable]) -> str:
    cards = []
    for item in items:
        slug = str(item.get("slug", ""))
        status = str(item.get("library_status", ""))
        tags = " ".join(str(tag) for tag in item.get("tags", []))
        tools = " · ".join(str(tool) for tool in item.get("tools", []))
        search = " ".join(
            [str(item.get("title", "")), str(item.get("summary", "")), str(item.get("content_type", "")), tags, tools]
        ).lower()
        archive = ""
        if status != "archived":
            archive = f'''<form method="post" action="{esc(route_urls['archive'](slug))}">
<input type="hidden" name="csrf_token" value="{esc(csrf)}"><button class="text-button" type="submit">Archive</button></form>'''
        cards.append(f'''<article class="manager-card" data-library-card data-search="{esc(search)}">
  <div class="card-topline"><span class="eyebrow">{esc(item.get('content_type'))}</span><span class="status-pill" data-status="{esc(status)}">{esc(status)}</span></div>
  <h2>{esc(item.get('title'))}</h2>
  <p>{esc(item.get('summary'))}</p>
  <div class="meta-line"><strong>{esc(item.get('format'))}</strong><span>{esc(tools)}</span></div>
  <div class="tag-line">{esc(tags)}</div>
  <div class="card-actions">
    <a class="button secondary" target="_blank" rel="noopener" href="{esc(item.get('_preview_url'))}">Preview</a>
    <a class="button secondary" href="{esc(route_urls['edit'](slug))}">Edit</a>
    <form method="post" action="{esc(route_urls['open'](slug))}"><input type="hidden" name="csrf_token" value="{esc(csrf)}"><button class="button secondary" type="submit">Open Files</button></form>
    {archive}
    <a class="danger-link" href="{esc(route_urls['delete'](slug))}">Delete…</a>
  </div>
</article>''')

    empty = '<div class="empty-state"><h2>No library items yet.</h2><p>Add the first reusable asset when you are ready.</p></div>'
    grid = "".join(cards) if cards else empty
    return f'''<section class="page-heading">
  <div><p class="eyebrow">Local workspace</p><h1>Library</h1><p>Browse and maintain public-safe reusable learning content before publishing.</p></div>
  <a class="button" href="{esc(route_urls['add_page'])}">Add Item</a>
</section>
<section class="toolbar"><label for="library-search">Search library</label><input id="library-search" type="search" placeholder="Title, type, tool, tag…" autocomplete="off"></section>
<p class="result-count" id="result-count">{len(items)} item(s)</p>
<section class="manager-grid" id="library-grid">{grid}</section>'''


def upload_area(label: str, key: str, editing: bool) -> str:
    replace = ""
    if editing:
        replace = f'''<label class="check-row"><input type="checkbox" name="replace_{key}" value="1"> Replace everything currently in <code>{key}/</code> before saving</label>'''
    return f'''<div class="upload-card">
  <h3>{esc(label)}</h3>
  <p>Add individual files, a complete folder, or both. Folder structure is preserved.</p>
  <label>Choose files<input type="file" name="{key}_files" data-upload-group="{key}_files" multiple></label>
  <label>Choose folder<input type="file" name="{key}_files" data-upload-group="{key}_files" data-folder-input multiple webkitdirectory directory></label>
  <div class="file-selection" data-file-selection="{key}_files">No new files selected.</div>
  {replace}
</div>'''


def item_form_body(mode: str, item, options: dict, csrf: str, action_url: str) -> str:
    editing = mode == "edit"
    title = "Edit Item" if editing else "Add Item"
    submit = "Save Changes" if editing else "Add to Library"
    slug_note = "Stable URL identifier. Editing is intentionally disabled here." if editing else "Use lowercase letters, numbers, and hyphens. Phase 6 will suggest this automatically."
    readonly = " readonly" if editing else ""
    portfolio = as_text(item, "portfolio_status")

    return f'''<section class="page-heading compact"><div><p class="eyebrow">Local workspace</p><h1>{title}</h1><p>Files first, then human context, then a final review before writing to the library.</p></div></section>
<form class="manager-form" method="post" action="{esc(action_url)}" enctype="multipart/form-data" data-manager-form>
  <input type="hidden" name="csrf_token" value="{esc(csrf)}">
  <ol class="stepper" aria-label="Add item steps"><li class="active" data-step-label="1">1. Files</li><li data-step-label="2">2. Details</li><li data-step-label="3">3. Review</li></ol>

  <section class="form-step active" data-step="1">
    <div class="section-heading"><p class="eyebrow">Step 1</p><h2>Files</h2><p>Place files into the same preview/source/assets structure used by every library item.</p></div>
    <div class="upload-grid">{upload_area('Preview', 'preview', editing)}{upload_area('Source', 'source', editing)}{upload_area('Supporting assets', 'assets', editing)}</div>
    <div class="step-actions"><button type="button" class="button" data-next-step>Continue to Details</button></div>
  </section>

  <section class="form-step" data-step="2">
    <div class="section-heading"><p class="eyebrow">Step 2</p><h2>Details</h2><p>Describe what the item is. Smart detection and prefill arrive in Phase 6.</p></div>
    <div class="form-grid">
      <label class="span-2">Title<input required name="title" value="{esc(as_text(item, 'title'))}"></label>
      <label>Slug<input required name="slug" value="{esc(as_text(item, 'slug'))}" pattern="[a-z0-9]+(?:-[a-z0-9]+)*"{readonly}><small>{esc(slug_note)}</small></label>
      <label>Created<input required type="date" name="created" value="{esc(as_text(item, 'created'))}"></label>
      <label class="span-2">Summary<textarea required name="summary" rows="3">{esc(as_text(item, 'summary'))}</textarea></label>
      <label>Content type<select required name="content_type"><option value="">Choose…</option>{options_html(options['content_types'], as_text(item, 'content_type'))}</select></label>
      <label>Format<input required name="format" list="format-suggestions" value="{esc(as_text(item, 'format'))}"></label>
      <label class="span-2">Tools<input required name="tools" value="{esc(as_text(item, 'tools'))}" placeholder="Articulate Storyline, JavaScript"><small>Comma-separated for Phase 5.</small></label>
      <label class="span-2">Tags<input required name="tags" value="{esc(as_text(item, 'tags'))}" placeholder="branching, sales enablement, scenario"><small>Comma-separated for Phase 5.</small></label>
      <label>Library status<select required name="library_status"><option value="">Choose…</option>{options_html(options['library_statuses'], as_text(item, 'library_status'))}</select></label>
      <label>Preview type<select required name="preview_type"><option value="">Choose…</option>{options_html(options['preview_types'], as_text(item, 'preview_type'))}</select></label>
      <label>Portfolio status<select name="portfolio_status">{options_html(options['portfolio_statuses'], portfolio, blank_label='Not set')}</select></label>
      <label>Updated<input type="date" name="updated" value="{esc(as_text(item, 'updated'))}"></label>
      <label class="span-2">Other label<input name="other_label" value="{esc(as_text(item, 'other_label'))}"><small>Required only when a controlled field uses Other.</small></label>
      <label class="span-2">Thumbnail path<input name="thumbnail" value="{esc(as_text(item, 'thumbnail'))}" placeholder="assets/thumbnail.png"></label>
      <label class="span-2">Usage notes<textarea name="usage_notes" rows="4">{esc(as_text(item, 'usage_notes'))}</textarea></label>
    </div>
    <datalist id="format-suggestions">{''.join(f'<option value="{esc(value)}"></option>' for value in options['format_suggestions'])}</datalist>
    <div class="step-actions"><button type="button" class="button secondary" data-prev-step>Back</button><button type="button" class="button" data-next-step>Review Item</button></div>
  </section>

  <section class="form-step" data-step="3">
    <div class="section-heading"><p class="eyebrow">Step 3</p><h2>Review</h2><p>This is a save review, not the generated preview. Full pre-publish preview arrives in Phase 7.</p></div>
    <div class="review-card" data-review-card><dl><div><dt>Title</dt><dd data-review="title">—</dd></div><div><dt>Slug</dt><dd data-review="slug">—</dd></div><div><dt>Content type</dt><dd data-review="content_type">—</dd></div><div><dt>Format</dt><dd data-review="format">—</dd></div><div><dt>Tools</dt><dd data-review="tools">—</dd></div><div><dt>Tags</dt><dd data-review="tags">—</dd></div><div><dt>Status</dt><dd data-review="library_status">—</dd></div><div><dt>Preview type</dt><dd data-review="preview_type">—</dd></div></dl></div>
    <p class="public-safe-note"><strong>Public-safe boundary:</strong> everything written here belongs in the public repository. Do not add confidential or unsanitized material.</p>
    <div class="step-actions"><button type="button" class="button secondary" data-prev-step>Back</button><button type="submit" class="button">{submit}</button></div>
  </section>
</form>'''


def delete_body(item: dict, csrf: str, required_phrase: str, back_url: str, action_url: str) -> str:
    return f'''<section class="danger-panel">
  <p class="eyebrow">Danger zone</p><h1>Delete {esc(item.get('title'))}?</h1>
  <p>Archive is the safer normal action. Delete removes the entire local item folder; committed history can still recover older versions.</p>
  <div class="delete-phrase"><span>Type exactly:</span><code>{esc(required_phrase)}</code></div>
  <form method="post" action="{esc(action_url)}">
    <input type="hidden" name="csrf_token" value="{esc(csrf)}">
    <label>Confirmation phrase<input required name="confirm_phrase" autocomplete="off"></label>
    <label class="check-row"><input required type="checkbox" name="understand" value="1"> I understand this removes the entire item folder from my working copy.</label>
    <div class="step-actions"><a class="button secondary" href="{esc(back_url)}">Cancel</a><button class="button danger" type="submit">Permanently Delete</button></div>
  </form>
</section>'''
