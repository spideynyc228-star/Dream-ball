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

  const confirmModal = document.querySelector("[data-confirm-modal]");
  let formToConfirm = null;
  const closeConfirmModal = () => {
    if (!confirmModal) return;
    confirmModal.hidden = true;
    formToConfirm = null;
  };
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      if (form.dataset.confirmed === "true") return;
      event.preventDefault();
      if (!confirmModal) return;
      formToConfirm = form;
      confirmModal.querySelector("[data-confirm-message]").textContent = form.dataset.confirm;
      confirmModal.hidden = false;
      confirmModal.querySelector("[data-confirm-accept]").focus();
    });
  });
  confirmModal?.querySelectorAll("[data-confirm-cancel]").forEach((button) => button.addEventListener("click", closeConfirmModal));
  confirmModal?.querySelector("[data-confirm-accept]")?.addEventListener("click", () => {
    if (!formToConfirm) return;
    formToConfirm.dataset.confirmed = "true";
    formToConfirm.requestSubmit();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && confirmModal && !confirmModal.hidden) closeConfirmModal();
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

  // Center headings only for public landing navigation; app tabs use their own targets.
  document.querySelectorAll('.landing-header a[href^="#"], .landing-footer-full a[href^="#"], .hero-actions a[href^="#"]').forEach((link) => {
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

  document.querySelectorAll('.admin-nav a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (event) => {
      const target = document.querySelector(link.getAttribute("href"));
      if (!target) return;

      event.preventDefault();
      const headerHeight = document.querySelector(".site-header")?.offsetHeight || 0;
      const destination = Math.max(0, target.getBoundingClientRect().top + window.scrollY - headerHeight - 18);
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

  const rehearsalModal = document.querySelector("[data-rehearsal-modal]");
  if (rehearsalModal) {
    const rehearsalForm = rehearsalModal.querySelector("[data-rehearsal-request]");
    const rehearsalTitle = rehearsalModal.querySelector("#rehearsal-title");
    const rehearsalMessage = rehearsalModal.querySelector("[data-rehearsal-message]");
    const closeRehearsal = () => {
      rehearsalModal.hidden = true;
      rehearsalMessage.textContent = "";
    };
    document.querySelectorAll("[data-open-rehearsal]").forEach((button) => {
      button.addEventListener("click", () => {
        rehearsalForm.action = button.dataset.recipientUrl;
        rehearsalTitle.textContent = `Invite ${button.dataset.recipientName} to a rehearsal`;
        rehearsalModal.hidden = false;
        rehearsalForm.querySelector('input[name="proposed_date"]').focus();
      });
    });
    rehearsalModal.querySelectorAll("[data-close-rehearsal]").forEach((button) => button.addEventListener("click", closeRehearsal));
    rehearsalForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const submitButton = rehearsalForm.querySelector('[type="submit"]');
      submitButton.disabled = true;
      rehearsalMessage.textContent = "Sending invitation…";
      try {
        const response = await fetch(rehearsalForm.action, { method: "POST", body: new FormData(rehearsalForm), headers: { "X-Requested-With": "XMLHttpRequest" } });
        const data = await response.json();
        rehearsalMessage.textContent = data.message;
        if (response.ok) {
          rehearsalForm.reset();
          submitButton.textContent = "Invitation sent ✓";
          window.setTimeout(closeRehearsal, 900);
        }
      } catch (_error) {
        rehearsalMessage.textContent = "Could not send the invitation. Please try again.";
      } finally {
        submitButton.disabled = false;
      }
    });
  }
});
