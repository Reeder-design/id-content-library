(() => {
  const form = document.querySelector('[data-manager-form]');
  if (!form) return;

  const q = (s) => form.querySelector(s);
  const qa = (s) => [...form.querySelectorAll(s)];
  const uploads = qa('[data-upload-group="project_files"]');
  const advanced = q('[data-advanced-details]');
  const sourceOnly = q('[data-source-only]');
  const replaceProject = q('[data-replace-project]');
  const smartStatus = q('[data-smart-prefill-status]');
  let step = 1;
  let maxReached = 1;
  let autoWriting = false;
  let requestId = 0;

  const valueOf = (name) => {
    const field = form.elements.namedItem(name);
    return field && 'value' in field ? String(field.value || '').trim() : '';
  };

  const split = (value) => String(value || '').split(',').map((x) => x.trim()).filter(Boolean);

  const updateReview = () => {
    qa('[data-review]').forEach((el) => {
      const value = valueOf(el.dataset.review);
      el.textContent = value || '—';
    });
  };

  const updateDraftPreview = () => {
    qa('[data-draft]').forEach((el) => {
      const name = el.dataset.draft;
      const value = valueOf(name);
      if (name === 'tags') {
        el.replaceChildren(...split(value).map((tag) => {
          const chip = document.createElement('span');
          chip.className = 'choice-chip selected';
          chip.textContent = tag;
          return chip;
        }));
        return;
      }
      const fallbacks = {
        title: 'Untitled item',
        summary: 'Your description will appear here.',
        content_type: 'Resource',
        library_status: 'stable',
        format: 'Format',
        tools: 'Tools',
      };
      el.textContent = value || fallbacks[name] || '—';
    });
  };

  const showStep = (next) => {
    step = Math.max(1, Math.min(3, next));
    maxReached = Math.max(maxReached, step);
    qa('[data-step]').forEach((el) => el.classList.toggle('active', Number(el.dataset.step) === step));
    qa('[data-step-label]').forEach((el) => {
      const current = Number(el.dataset.stepLabel) === step;
      el.classList.toggle('active', current);
      if (current) el.setAttribute('aria-current', 'step');
      else el.removeAttribute('aria-current');
      el.querySelector('[data-step-jump]').disabled = Number(el.dataset.stepLabel) > maxReached;
    });
    const progress = q('[data-step-progress]');
    if (progress) progress.textContent = ['Step 1 of 3 · Choose project', 'Step 2 of 3 · Add details', 'Step 3 of 3 · Review & save'][step - 1];
    const back = q('[data-step-back]');
    if (back) {
      back.hidden = step === 1;
      back.textContent = step === 3 ? '← Back to details' : '← Back to project';
    }
    if (step === 3) {
      updateReview();
      updateDraftPreview();
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const validDetails = () => {
    for (const field of qa('[data-step="2"] [required]')) {
      if (!field.checkValidity()) {
        if (advanced && advanced.contains(field)) advanced.open = true;
        field.reportValidity();
        return false;
      }
    }
    return true;
  };

  qa('[data-next-step]').forEach((button) => button.addEventListener('click', () => {
    if (step === 2 && !validDetails()) return;
    showStep(step + 1);
  }));
  qa('[data-prev-step]').forEach((button) => button.addEventListener('click', () => showStep(step - 1)));
  const topBack = q('[data-step-back]');
  if (topBack) topBack.addEventListener('click', () => showStep(step - 1));
  qa('[data-step-jump]').forEach((button) => button.addEventListener('click', () => {
    const target = Number(button.dataset.stepJump);
    if (target > maxReached) return;
    if (target === 3 && step < 3 && !validDetails()) return;
    showStep(target);
  }));

  qa('[data-smart-field]').forEach((field) => {
    const markHuman = () => {
      if (!autoWriting && field.dataset.autoFilled === 'true' && field.value !== field.dataset.autoValue) field.dataset.autoFilled = 'false';
    };
    field.addEventListener('input', markHuman);
    field.addEventListener('change', markHuman);
  });

  const syncChips = () => qa('[data-chip-target]').forEach((group) => {
    const field = form.elements.namedItem(group.dataset.chipTarget);
    if (!field) return;
    const chosen = new Set(split(field.value).map((x) => x.toLowerCase()));
    group.querySelectorAll('[data-chip-value]').forEach((chip) => chip.classList.toggle('selected', chosen.has(chip.dataset.chipValue.toLowerCase())));
  });

  qa('[data-chip-target]').forEach((group) => {
    const field = form.elements.namedItem(group.dataset.chipTarget);
    group.querySelectorAll('[data-chip-value]').forEach((chip) => chip.addEventListener('click', () => {
      const values = split(field.value);
      const i = values.findIndex((x) => x.toLowerCase() === chip.dataset.chipValue.toLowerCase());
      if (i >= 0) values.splice(i, 1); else values.push(chip.dataset.chipValue);
      field.value = values.join(', ');
      field.dataset.autoFilled = 'false';
      syncChips();
    }));
  });
  syncChips();

  const suggest = (name, value) => {
    const field = form.elements.namedItem(name);
    if (!field || field.readOnly || value == null || value === '') return;
    const rendered = Array.isArray(value) ? value.join(', ') : String(value);
    if (field.value.trim() && field.dataset.autoFilled !== 'true') return;
    autoWriting = true;
    field.value = rendered;
    field.dataset.autoFilled = 'true';
    field.dataset.autoValue = rendered;
    field.dispatchEvent(new Event('change', { bubbles: true }));
    autoWriting = false;
    syncChips();
  };

  const selectedProjectFiles = () => uploads.flatMap((input) => [...input.files].map((file) => ({ input, file })));
  const descriptors = () => selectedProjectFiles().map(({ file }) => ({
    area: sourceOnly && sourceOnly.checked ? 'source' : 'preview',
    path: file.webkitRelativePath || file.name,
  }));

  const setSmartMessage = (state, strong, text) => {
    if (!smartStatus) return;
    smartStatus.dataset.state = state;
    smartStatus.querySelector('strong').textContent = strong;
    smartStatus.querySelector('span:last-child').textContent = text;
  };

  const runSmartPrefill = async () => {
    const files = descriptors();
    if (!files.length) return setSmartMessage('ready', 'Smart suggestions are ready.', 'Choose a file or folder and we’ll suggest the obvious details.');
    const id = ++requestId;
    setSmartMessage('working', 'Looking at the project…', `${files.length} file${files.length === 1 ? '' : 's'} detected.`);
    try {
      const response = await fetch('/api/prefill', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ files }) });
      if (!response.ok) throw new Error();
      const data = await response.json();
      if (id !== requestId) return;
      ['title', 'slug', 'format', 'tools', 'preview_type'].forEach((name) => suggest(name, data[name]));
      const detected = [data.format, data.preview_type].filter(Boolean).join(' · ');
      setSmartMessage('done', detected ? `Looks like ${detected}.` : 'Suggestions applied.', 'Change anything you want — your edits win.');
    } catch (_) {
      setSmartMessage('error', 'Couldn’t make smart suggestions.', 'No problem — you can still fill in the details yourself.');
    }
  };

  const updateFileSummary = () => {
    const chosen = selectedProjectFiles();
    const target = q('[data-file-selection="project_files"]');
    if (!target) return;
    if (!chosen.length) { target.textContent = 'Nothing selected yet.'; target.dataset.state = 'empty'; return; }
    const folder = chosen.find(({ file }) => file.webkitRelativePath);
    target.textContent = folder ? `Folder selected: ${folder.file.webkitRelativePath.split('/')[0]} · ${chosen.length} files` : `File selected: ${chosen[0].file.name}`;
    target.dataset.state = 'selected';
  };

  uploads.forEach((input) => input.addEventListener('change', () => {
    if (input.files.length) uploads.filter((other) => other !== input).forEach((other) => { other.value = ''; });
    updateFileSummary();
    runSmartPrefill();
  }));
  if (sourceOnly) sourceOnly.addEventListener('change', runSmartPrefill);

  const otherNames = ['content_type', 'library_status', 'preview_type', 'portfolio_status'];
  const otherWrap = q('[data-other-label-wrap]');
  const syncOtherLabel = () => {
    if (!otherWrap) return;
    const active = otherNames.some((name) => {
      const field = form.elements.namedItem(name);
      return field && String(field.value).toLowerCase() === 'other';
    });
    otherWrap.hidden = !active;
    const input = otherWrap.querySelector('input');
    if (input) input.disabled = !active;
  };
  otherNames.forEach((name) => {
    const field = form.elements.namedItem(name);
    if (field) field.addEventListener('change', () => { syncOtherLabel(); if (String(field.value).toLowerCase() === 'other' && advanced && name !== 'content_type') advanced.open = true; });
  });
  syncOtherLabel();

  const appendFile = (data, group, input, file) => {
    let path = file.webkitRelativePath || file.name;
    if (input.dataset.folderInput !== undefined && path.includes('/')) path = path.split('/').slice(1).join('/');
    data.append(group, file, path || file.name);
  };

  form.addEventListener('submit', async (event) => {
    if (!validDetails()) { event.preventDefault(); showStep(2); return; }
    event.preventDefault();
    const data = new FormData(form);
    data.delete('project_files');
    selectedProjectFiles().forEach(({ input, file }) => {
      appendFile(data, 'source_files', input, file);
      if (!(sourceOnly && sourceOnly.checked)) appendFile(data, 'preview_files', input, file);
    });
    if (replaceProject && replaceProject.checked) {
      data.append('replace_source', '1');
      data.append('replace_preview', '1');
    }
    const submit = q('button[type="submit"]');
    if (submit) submit.disabled = true;
    try {
      const response = await fetch(form.action || window.location.href, { method: 'POST', body: data, redirect: 'follow' });
      if (response.redirected) return void (window.location.href = response.url);
      document.open(); document.write(await response.text()); document.close();
    } catch (error) {
      if (submit) submit.disabled = false;
      window.alert(`Save failed: ${error.message}`);
    }
  });
})();
