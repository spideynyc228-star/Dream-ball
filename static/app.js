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

  document.querySelectorAll("[data-event-carousel]").forEach((carousel) => {
    const panel = carousel.closest(".timeline-panel");
    const previous = panel?.querySelector("[data-carousel-prev]");
    const next = panel?.querySelector("[data-carousel-next]");
    const step = () => Math.min(carousel.clientWidth * 0.84, 360);
    const move = (direction) => carousel.scrollBy({ left: step() * direction, behavior: "smooth" });

    previous?.addEventListener("click", () => move(-1));
    next?.addEventListener("click", () => move(1));
    carousel.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft") { event.preventDefault(); move(-1); }
      if (event.key === "ArrowRight") { event.preventDefault(); move(1); }
    });
  });

  // The landing header sits outside .dream-landing, so bind to every anchor link.
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      const target = document.querySelector(link.getAttribute("href"));
      const heading = target?.querySelector("h2");
      if (!target || !heading) return;

      event.preventDefault();
      const headingTop = heading.getBoundingClientRect().top + window.scrollY;
      const destination = Math.max(0, headingTop - ((window.innerHeight - heading.offsetHeight) / 2));
      window.scrollTo({ top: destination, behavior: "smooth" });
      history.replaceState(null, "", link.getAttribute("href"));
    });
  });

  document.querySelectorAll("[data-notification-menu]").forEach((menu) => {
    const toggle = menu.querySelector("[data-notification-toggle]");
    const popover = menu.querySelector("[data-notification-popover]");
    const close = () => {
      popover.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
    };
    toggle.addEventListener("click", () => {
      const isOpen = !popover.hidden;
      if (isOpen) close();
      else {
        popover.hidden = false;
        toggle.setAttribute("aria-expanded", "true");
      }
    });
    document.addEventListener("click", (event) => {
      if (!menu.contains(event.target)) close();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") close();
    });
  });
});
