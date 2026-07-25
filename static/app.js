document.addEventListener("DOMContentLoaded", () => {
  const photoInput = document.querySelector("#photo");
  if (photoInput) {
    photoInput.addEventListener("change", () => {
      const file = photoInput.files?.[0];
      if (!file) return;
      const name = document.querySelector("#photo-name");
      const preview = document.querySelector("#photo-preview");
      const placeholder = document.querySelector("#photo-placeholder");
      if (name) name.textContent = file.name;
      if (placeholder) placeholder.hidden = true;
      if (preview) {
        preview.src = URL.createObjectURL(file);
        preview.hidden = false;
      }
    });
  }

  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (!window.confirm(form.dataset.confirm)) event.preventDefault();
    });
  });

  document.querySelectorAll("[data-copy-plan]").forEach((button) => {
    button.addEventListener("click", async () => {
      const original = button.textContent;
      try {
        await navigator.clipboard.writeText(button.dataset.copyPlan);
        button.textContent = "Template copied ✓";
      } catch {
        button.textContent = "Select and copy the plan manually";
      }
      window.setTimeout(() => { button.textContent = original; }, 2200);
    });
  });

  document.querySelectorAll(".flash").forEach((flash) => {
    window.setTimeout(() => {
      flash.style.opacity = "0";
      flash.style.transform = "translateY(-6px)";
      window.setTimeout(() => flash.remove(), 220);
    }, 4500);
  });
});
