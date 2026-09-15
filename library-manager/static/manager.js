(() => {
  const search = document.querySelector('#library-search');
  if (search) {
    const cards = [...document.querySelectorAll('[data-library-card]')];
    const count = document.querySelector('#result-count');
    const applySearch = () => {
      const query = search.value.trim().toLowerCase();
      let visible = 0;
      cards.forEach((card) => {
        const matches = !query || (card.dataset.search || '').includes(query);
        card.hidden = !matches;
        if (matches) visible += 1;
      });
      if (count) count.textContent = `${visible} item(s)`;
    };
    search.addEventListener('input', applySearch);
  }

  const form = document.querySelector('[data-manager-form]');
  if (!form) return;

  const steps = [...form.querySelectorAll('[data-step]')];
  const labels = [...document.querySelectorAll('[data-step-label]')];
  const uploadInputs = [...form.querySelectorAll('[data-upload-group]')];
  const smartStatus = form.querySelector('[data-smart-prefill-status]');
  const advancedDetails = form.querySelector('[data-advanced-details]');
  let currentStep = 1;
  let applyingSmart = false;

  const showStep = (number) => {
    currentStep = Math.max(1, Math.min(3, number));
    steps.forEach((step) => step.classList.toggle('active', Number(step.dataset.step) === currentStep));
    labels.forEach((label) => label.classList.toggle('active', Number(label.dataset.stepLabel) === currentStep));
    if (currentStep === 3) updateReview();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const validateDetails = () => {
    const detailStep = form.querySelector('[data-step="2"]');
    const required = [...detailStep.querySelectorAll('[required]')];
    for (const field of required) {
      if (!field.checkValidity()) {
        if (advancedDetails && advancedDetails.contains(field)) advancedDetails.open = true;
        field.reportValidity();
        return false;
      }
    }
    return true;
  };

  form.querySelectorAll('[data-next-step]').forEach((button) => {
    button.addEventListener('click', () => {
      if (currentStep === 2 && !validateDetails()) return;
      showStep(currentStep + 1);
    });
  });
  form.querySelectorAll('[data-prev-step]').forEach((button) => button.addEventListener('click', () => showStep(currentStep - 1)));

  function updateReview() {
    form.querySelectorAll('[data-review]').forEach((target) => {
      const field = form.elements.namedItem(target.dataset.review);
      target.textContent = field && field.value ? field.value : '—';
    });
  }

  const smartFields = [...form.querySelectorAll('[data-smart-field]')];
  smartFields.forEach((field) => {
    const markHuman = () => {
      if (applyingSmart) return;
      if (field.dataset.autoFilled === 'true' && field.value !== field.dataset.autoValue) {
        field.dataset.autoFilled = 'false';
      }
    };
    field.addEventListener('input', markHuman);
    field.addEventListener('change', markHuman);
  });

  const setSuggestion = (name, value) => {
    const field = form.elements.namedItem(name);
    if (!field || field.readOnly || value === undefined || value === null || value === '') return;
    const rendered = Array.isArray(value) ? value.join(', ') : String(value);
    const current = String(field.value || '').trim();
    if (current && field.dataset.autoFilled !== 'true') return;

    applyingSmart = true;
    field.value = rendered;
    field.dataset.autoFilled = 'true';
    field.dataset.autoValue = rendered;
    field.dispatchEvent(new Event('input', { bubbles: true }));
    field.dispatchEvent(new Event('change', { bubbles: true }));
    applyingSmart = false;
    syncAllChips();
  };

  const fileDescriptors = () => uploadInputs.flatMap((input) => {
    const area = (input.dataset.uploadGroup || '').replace(/_files$/, '');
    return [...input.files].map((file) => ({
      area,
      path: file.webkitRelativePath || file.name,
    }));
  });

  let prefillSequence = 0;
  const runSmartPrefill = async () => {
    const files = fileDescriptors();
    if (!files.length) {
      if (smartStatus) {
        smartStatus.dataset.state = 'ready';
        smartStatus.querySelector('strong').textContent = 'Smart prefill ready.';
        smartStatus.querySelector('span').textContent = 'Choose files or folders to generate deterministic suggestions.';
      }
      return;
    }

    const sequence = ++prefillSequence;
    if (smartStatus) {
      smartStatus.dataset.state = 'working';
      smartStatus.querySelector('strong').textContent = 'Analyzing files…';
      smartStatus.querySelector('span').textContent = `${files.length} file path(s) selected.`;
    }

    try {
      const response = await fetch('/api/prefill', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ files }),
      });
      if (!response.ok) throw new Error(`Prefill request returned ${response.status}`);
      const suggestions = await response.json();
      if (sequence !== prefillSequence) return;

      ['title', 'slug', 'format', 'tools', 'preview_type'].forEach((name) => setSuggestion(name, suggestions[name]));
      if (smartStatus) {
        const detected = [suggestions.format, suggestions.preview_type].filter(Boolean).join(' · ');
        smartStatus.dataset.state = 'done';
        smartStatus.querySelector('strong').textContent = detected ? `Detected ${detected}.` : 'Suggestions applied.';
        smartStatus.querySelector('span').textContent = 'Review the suggestions in Details; your manual edits always win.';
      }
    } catch (error) {
      if (smartStatus) {
        smartStatus.dataset.state = 'error';
        smartStatus.querySelector('strong').textContent = 'Smart prefill could not run.';
        smartStatus.querySelector('span').textContent = error.message;
      }
    }
  };

  const updateFileSummary = (group) => {
    const inputs = uploadInputs.filter((input) => input.dataset.uploadGroup === group);
    const files = inputs.flatMap((input) => [...input.files]);
    const target = form.querySelector(`[data-file-selection="${group}"]`);
    if (!target) return;
    target.textContent = files.length ? `${files.length} new file(s) selected.` : 'No new files selected.';
  };

  uploadInputs.forEach((input) => {
    input.addEventListener('change', () => {
      updateFileSummary(input.dataset.uploadGroup);
      runSmartPrefill();
    });
  });

  const splitList = (value) => String(value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);

  const syncChipGroup = (group) => {
    const targetName = group.dataset.chipTarget;
    const field = form.elements.namedItem(targetName);
    if (!field) return;
    const selected = new Set(splitList(field.value).map((value) => value.toLowerCase()));
    group.querySelectorAll('[data-chip-value]').forEach((chip) => {
      chip.classList.toggle('selected', selected.has((chip.dataset.chipValue || '').toLowerCase()));
    });
  };

  const syncAllChips = () => form.querySelectorAll('[data-chip-target]').forEach(syncChipGroup);

  form.querySelectorAll('[data-chip-target]').forEach((group) => {
    const targetName = group.dataset.chipTarget;
    const field = form.elements.namedItem(targetName);
    group.querySelectorAll('[data-chip-value]').forEach((chip) => {
      chip.addEventListener('click', () => {
        if (!field) return;
        const value = chip.dataset.chipValue || '';
        const values = splitList(field.value);
        const index = values.findIndex((item) => item.toLowerCase() === value.toLowerCase());
        if (index >= 0) values.splice(index, 1);
        else values.push(value);
        field.value = values.join(', ');
        field.dataset.autoFilled = 'false';
        field.dispatchEvent(new Event('input', { bubbles: true }));
        syncChipGroup(group);
      });
    });
    if (field) field.addEventListener('input', () => syncChipGroup(group));
  });
  syncAllChips();

  const controlledOtherFields = ['content_type', 'library_status', 'preview_type', 'portfolio_status'];
  controlledOtherFields.forEach((name) => {
    const field = form.elements.namedItem(name);
    if (!field) return;
    field.addEventListener('change', () => {
      if (String(field.value).toLowerCase() === 'other' && advancedDetails) advancedDetails.open = true;
    });
  });

  form.addEventListener('submit', async (event) => {
    if (!validateDetails()) {
      event.preventDefault();
      showStep(2);
      return;
    }

    event.preventDefault();
    const data = new FormData(form);
    const groups = [...new Set(uploadInputs.map((input) => input.dataset.uploadGroup))];
    groups.forEach((group) => data.delete(group));

    uploadInputs.forEach((input) => {
      const group = input.dataset.uploadGroup;
      [...input.files].forEach((file) => {
        let relative = file.webkitRelativePath || file.name;
        if (input.dataset.folderInput !== undefined && relative.includes('/')) {
          relative = relative.split('/').slice(1).join('/');
        }
        data.append(group, file, relative || file.name);
      });
    });

    const submit = form.querySelector('button[type="submit"]');
    if (submit) submit.disabled = true;
    try {
      const response = await fetch(form.action || window.location.href, { method: 'POST', body: data, redirect: 'follow' });
      if (response.redirected) {
        window.location.href = response.url;
        return;
      }
      document.open();
      document.write(await response.text());
      document.close();
    } catch (error) {
      if (submit) submit.disabled = false;
      window.alert(`Save failed: ${error.message}`);
    }
  });
})();
