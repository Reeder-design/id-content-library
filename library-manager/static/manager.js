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
  let currentStep = 1;

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
      if (!field.reportValidity()) return false;
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

  const uploadInputs = [...form.querySelectorAll('[data-upload-group]')];
  const updateFileSummary = (group) => {
    const inputs = uploadInputs.filter((input) => input.dataset.uploadGroup === group);
    const files = inputs.flatMap((input) => [...input.files]);
    const target = form.querySelector(`[data-file-selection="${group}"]`);
    if (!target) return;
    target.textContent = files.length ? `${files.length} new file(s) selected.` : 'No new files selected.';
  };
  uploadInputs.forEach((input) => input.addEventListener('change', () => updateFileSummary(input.dataset.uploadGroup)));

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
