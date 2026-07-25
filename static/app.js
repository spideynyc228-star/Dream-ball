document.addEventListener("DOMContentLoaded", () => {
  const photoInput = document.querySelector("#id_photo, #photo");
  if (photoInput) {
    const editor = document.querySelector("[data-avatar-editor]");
    const preview = document.querySelector("#photo-preview");
    const placeholder = document.querySelector("#photo-placeholder");
    const cropModal = document.querySelector("[data-avatar-crop-modal]");
    const cropStage = document.querySelector("[data-avatar-crop-stage]");
    const cropPreview = document.querySelector("[data-avatar-crop-preview]");
    const cropZoom = document.querySelector("[data-avatar-crop-zoom]");
    if (cropZoom) cropZoom.value = document.querySelector("#id_photo_scale")?.value || "100";
    document.querySelector("[data-avatar-select]")?.addEventListener("click", () => photoInput.click());
    const controls = {
      x: document.querySelector("[data-photo-x]"),
      y: document.querySelector("[data-photo-y]"),
      scale: cropZoom,
      hiddenX: document.querySelector("#id_photo_position_x"),
      hiddenY: document.querySelector("#id_photo_position_y"),
      hiddenScale: document.querySelector("#id_photo_scale"),
    };
    const updatePhotoFrame = () => {
      if (!preview || !controls.x || !controls.y || !controls.scale) return;
      preview.style.setProperty("--photo-x", `${controls.x.value}%`);
      preview.style.setProperty("--photo-y", `${controls.y.value}%`);
      preview.style.setProperty("--photo-scale", controls.scale.value);
      // The crop can move in fractions of a pixel, while Django stores these
      // framing values as whole numbers. Keep the visual movement smooth but
      // submit valid, rounded integer values.
      const wholeNumber = (value) => Math.round(Number(value) || 0);
      if (controls.hiddenX) controls.hiddenX.value = wholeNumber(controls.x.value);
      if (controls.hiddenY) controls.hiddenY.value = wholeNumber(controls.y.value);
      if (controls.hiddenScale) controls.hiddenScale.value = wholeNumber(controls.scale.value);
    };
    const updateCropFrame = () => {
      if (!cropPreview || !controls.x || !controls.y || !controls.scale) return;
      cropPreview.style.setProperty("--photo-x", `${controls.x.value}%`);
      cropPreview.style.setProperty("--photo-y", `${controls.y.value}%`);
      cropPreview.style.setProperty("--photo-scale", controls.scale.value);
    };
    controls.scale?.addEventListener("input", () => { updatePhotoFrame(); updateCropFrame(); });
    let dragState = null;
    cropStage?.addEventListener("pointerdown", (event) => {
      if (!cropPreview?.src || !controls.x || !controls.y) return;
      dragState = { pointerId: event.pointerId, x: event.clientX, y: event.clientY };
      cropStage.setPointerCapture(event.pointerId);
      cropStage.classList.add("is-dragging");
      event.preventDefault();
    });
    cropStage?.addEventListener("pointermove", (event) => {
      if (!dragState || event.pointerId !== dragState.pointerId) return;
      const bounds = cropStage.getBoundingClientRect();
      const clamp = (value) => Math.max(0, Math.min(100, value));
      const scale = Math.max(1, Number(controls.scale?.value || 100) / 100);
      controls.x.value = clamp(Number(controls.x.value) - ((event.clientX - dragState.x) / bounds.width) * 100 / scale);
      controls.y.value = clamp(Number(controls.y.value) - ((event.clientY - dragState.y) / bounds.height) * 100 / scale);
      dragState.x = event.clientX;
      dragState.y = event.clientY;
      updatePhotoFrame();
      updateCropFrame();
    });
    const stopCropDrag = (event) => {
      if (!dragState || event.pointerId !== dragState.pointerId) return;
      if (cropStage?.hasPointerCapture(event.pointerId)) cropStage.releasePointerCapture(event.pointerId);
      cropStage?.classList.remove("is-dragging");
      dragState = null;
    };
    cropStage?.addEventListener("pointerup", stopCropDrag);
    cropStage?.addEventListener("pointercancel", stopCropDrag);
    const openCropModal = () => {
      if (!cropModal || !cropPreview || !preview?.src) return;
      cropPreview.src = preview.src;
      if (cropZoom && controls.scale) cropZoom.value = controls.scale.value;
      updateCropFrame();
      cropModal.hidden = false;
      cropStage?.focus();
    };
    cropModal?.querySelector("[data-avatar-crop-done]")?.addEventListener("click", () => { cropModal.hidden = true; });
    cropModal?.querySelector("[data-avatar-crop-cancel]")?.addEventListener("click", () => { cropModal.hidden = true; });
    updatePhotoFrame();
    photoInput.addEventListener("change", () => {
      const file = photoInput.files?.[0];
      if (!file) return;
      const name = document.querySelector("#photo-name");
      if (name) name.textContent = file.name;
      if (placeholder) placeholder.hidden = true;
      if (preview) {
        preview.src = URL.createObjectURL(file);
        preview.hidden = false;
      }
      if (controls.scale && Number(controls.scale.value) <= 100) controls.scale.value = "145";
      if (editor) editor.classList.add("has-photo");
      updatePhotoFrame();
      openCropModal();
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
    const confirmedForm = formToConfirm;
    confirmedForm.dataset.confirmed = "true";
    closeConfirmModal();
    confirmedForm.requestSubmit();
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

  document.querySelectorAll("form[data-form-recovery]").forEach((form) => {
    const storageKey = `dream-ball-form-${form.dataset.formRecovery}`;
    const shouldRestore = new URLSearchParams(window.location.search).get("_form_refresh") === "1";
    if (shouldRestore) {
      try {
        const saved = JSON.parse(sessionStorage.getItem(storageKey));
        if (saved && Date.now() - saved.savedAt < 30 * 60 * 1000) {
          Object.entries(saved.values).forEach(([name, value]) => {
            const field = form.elements.namedItem(name);
            if (!field || field.type === "password" || field.type === "file") return;
            if (field.length && !field.type && typeof field !== "string") {
              const selected = Array.isArray(value) ? value : [];
              Array.from(field).forEach((choice) => {
                if (choice.type === "checkbox") choice.checked = selected.includes(choice.value);
              });
            } else if (field.type === "checkbox") {
              field.checked = Boolean(value);
            } else {
              field.value = value;
            }
          });
        }
        sessionStorage.removeItem(storageKey);
      } catch (_error) {
        sessionStorage.removeItem(storageKey);
      }
    }
    const saveRecoveryDraft = () => {
      const values = {};
      const fields = Array.from(form.elements).filter((field) => {
        if (!field.name || field.name === "csrfmiddlewaretoken" || field.type === "password" || field.type === "file") return;
        return true;
      });
      fields.forEach((field) => {
        if (field.type !== "checkbox") {
          values[field.name] = field.value;
          return;
        }
        const matchingCheckboxes = fields.filter((candidate) => candidate.name === field.name && candidate.type === "checkbox");
        if (matchingCheckboxes.length === 1) {
          values[field.name] = field.checked;
        } else {
          values[field.name] = matchingCheckboxes.filter((candidate) => candidate.checked).map((candidate) => candidate.value);
        }
      });
      sessionStorage.setItem(storageKey, JSON.stringify({ savedAt: Date.now(), values }));
    };
    form.addEventListener("submit", async (event) => {
      saveRecoveryDraft();
      if (form.dataset.formRecovery !== "profile") return;

      // A profile photo cannot be restored from browser storage.  When a CSRF
      // token becomes stale, refresh it in the background and resend the same
      // FormData so the user does not have to choose the image again.
      event.preventDefault();
      const submitButton = form.querySelector('[type="submit"]');
      const submitState = form.querySelector("[data-profile-submit-state]");
      const originalLabel = submitButton?.innerHTML;
      const payload = new FormData(form);
      if (submitButton) {
        submitButton.disabled = true;
        submitButton.textContent = "Saving…";
      }
      if (submitState) submitState.textContent = "Saving your profile…";
      try {
        const sendProfile = () => fetch(form.action || window.location.href, {
          method: "POST",
          body: payload,
          credentials: "same-origin",
          headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        let response = await sendProfile();
        if (response.headers.get("content-type")?.includes("application/json")) {
          const data = await response.json();
          if (!response.ok || !data.ok) throw new Error(data.message || "Your profile could not be saved.");
          sessionStorage.removeItem(storageKey);
          if (submitState) submitState.textContent = "Saved — sending it for review…";
          window.location.assign(data.redirect || "/dashboard/");
          return;
        }
        const responseUrl = new URL(response.url, window.location.href);
        if (responseUrl.searchParams.get("_form_refresh") === "1") {
          const refreshedPage = new DOMParser().parseFromString(await response.text(), "text/html");
          const freshToken = refreshedPage.querySelector('[name="csrfmiddlewaretoken"]')?.value;
          if (!freshToken) throw new Error("Could not refresh the form security token.");
          payload.set("csrfmiddlewaretoken", freshToken);
          const visibleToken = form.querySelector('[name="csrfmiddlewaretoken"]');
          if (visibleToken) visibleToken.value = freshToken;
          response = await sendProfile();
          if (response.headers.get("content-type")?.includes("application/json")) {
            const data = await response.json();
            if (!response.ok || !data.ok) throw new Error(data.message || "Your profile could not be saved.");
            sessionStorage.removeItem(storageKey);
            if (submitState) submitState.textContent = "Saved — sending it for review…";
            window.location.assign(data.redirect || "/dashboard/");
            return;
          }
        }
        sessionStorage.removeItem(storageKey);
        if (response.redirected) {
          window.location.assign(response.url);
          return;
        }
        document.open();
        document.write(await response.text());
        document.close();
      } catch (error) {
        const message = document.createElement("p");
        message.className = "error-text form-save-error";
        message.textContent = error.message || "Your profile could not be saved. Please try again — your selected photo is still here.";
        form.querySelector(".form-save-error")?.remove();
        submitButton?.before(message);
        if (submitState) submitState.textContent = "";
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.innerHTML = originalLabel;
        }
      }
    });
  });

  const availableInvitationList = () => document.querySelector('.admin-page [data-code-list="available"]');
  const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[character]));
  const showAdminNotice = (message, isError = false) => {
    const stack = document.querySelector(".flash-stack") || document.body.appendChild(Object.assign(document.createElement("div"), { className: "flash-stack", ariaLive: "polite" }));
    const notice = document.createElement("div");
    notice.className = `flash flash-${isError ? "error" : "success"}`;
    notice.innerHTML = `<span>✦</span>${escapeHtml(message)}`;
    stack.appendChild(notice);
    window.setTimeout(() => notice.remove(), 3600);
  };
  const createInvitationCard = (invitation, csrfToken) => {
    const safeCode = escapeHtml(invitation.code);
    const safeRole = escapeHtml(invitation.role);
    const record = document.createElement("article");
    record.className = "invitation-record code-available";
    record.innerHTML = `<form class="code-edit-form" method="post" action="${escapeHtml(invitation.update_url)}"><input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(csrfToken)}"><label>Invitation code<input name="code" value="${safeCode}" maxlength="32" required></label><label>Role<select name="role"><option value="user" ${safeRole === "user" ? "selected" : ""}>User</option><option value="admin" ${safeRole === "admin" ? "selected" : ""}>Administrator</option></select></label><button class="button button-secondary" type="submit">Save</button></form><form method="post" action="${escapeHtml(invitation.delete_url)}" data-confirm="Delete invitation code ${safeCode}?"> <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(csrfToken)}"><button class="text-action delete-code" type="submit">Delete</button></form>`;
    return record;
  };
  document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!form.matches(".admin-page .code-create-form, .admin-page .code-edit-form, .admin-page .invitation-record > form")) return;
    if (event.defaultPrevented) return;
    event.preventDefault();
    const button = form.querySelector('[type="submit"]');
    if (button) button.disabled = true;
    try {
      const response = await fetch(form.action, { method: "POST", body: new FormData(form), headers: { "X-Requested-With": "XMLHttpRequest" } });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error(data.message || "Could not save this change.");
      if (form.classList.contains("code-create-form")) {
        const csrfToken = form.querySelector('[name="csrfmiddlewaretoken"]')?.value || "";
        availableInvitationList()?.prepend(createInvitationCard(data.invitation, csrfToken));
        form.reset();
      } else if (form.closest(".invitation-record") && !form.classList.contains("code-edit-form")) {
        form.closest(".invitation-record").remove();
      }
      showAdminNotice(data.message);
    } catch (error) {
      showAdminNotice(error.message || "Could not save this change.", true);
    } finally {
      if (button) button.disabled = false;
    }
  });

  document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!form.matches(".admin-page .report-actions form")) return;
    if (event.defaultPrevented) return;
    event.preventDefault();
    const button = form.querySelector('[type="submit"]');
    if (button) button.disabled = true;
    try {
      const response = await fetch(form.action, { method: "POST", body: new FormData(form), headers: { "X-Requested-With": "XMLHttpRequest" } });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error(data.message || "Could not update this report.");
      const record = form.closest(".report-record");
      if (data.deleted) {
        record?.remove();
      } else {
        const status = record?.querySelector(".status");
        if (status) {
          status.className = "status status-approved";
          status.textContent = data.status_label;
        }
        form.remove();
      }
      showAdminNotice(data.message);
    } catch (error) {
      showAdminNotice(error.message || "Could not update this report.", true);
      if (button) button.disabled = false;
    }
  });

  const replaceAdminSection = async (url, pushHistory = true) => {
    const response = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
    if (!response.ok) throw new Error("Could not open this section.");
    const documentFromResponse = new DOMParser().parseFromString(await response.text(), "text/html");
    const nextShell = documentFromResponse.querySelector(".admin-shell");
    const currentShell = document.querySelector(".admin-shell");
    if (!nextShell || !currentShell) throw new Error("Could not update this section.");
    currentShell.replaceWith(nextShell);
    if (pushHistory) history.pushState({}, "", url);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
  document.addEventListener("click", async (event) => {
    const link = event.target.closest(".admin-page .admin-nav a, .admin-page .profile-tabs a");
    if (!link || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    try {
      await replaceAdminSection(link.href);
    } catch (error) {
      showAdminNotice(error.message || "Could not open this section.", true);
    }
  });
  document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!form.matches(".admin-page .moderation-filters")) return;
    event.preventDefault();
    const parameters = new URLSearchParams(new FormData(form));
    try {
      await replaceAdminSection(`${window.location.pathname}?${parameters.toString()}`);
    } catch (error) {
      showAdminNotice(error.message || "Could not filter profiles.", true);
    }
  });
  window.addEventListener("popstate", () => {
    if (!document.querySelector(".admin-page .admin-shell")) return;
    replaceAdminSection(window.location.href, false).catch(() => window.location.reload());
  });

  const updateProfileTabCount = (status, change, updateAll = false) => {
    if (!status || status === "all") return;
    const tabLink = Array.from(document.querySelectorAll(".profile-tabs a")).find((link) => link.getAttribute("href")?.includes(`status=${status}`));
    const count = tabLink?.querySelector("b");
    if (!count) return;
    const current = Number.parseInt(count.textContent, 10);
    if (Number.isFinite(current)) count.textContent = Math.max(0, current + change);
    const allTabLink = Array.from(document.querySelectorAll(".profile-tabs a")).find((link) => link.getAttribute("href")?.includes("status=all"));
    const allCount = allTabLink?.querySelector("b");
    if (allCount && updateAll) {
      const allCurrent = Number.parseInt(allCount.textContent, 10);
      if (Number.isFinite(allCurrent)) allCount.textContent = Math.max(0, allCurrent + change);
    }
  };
  document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!form.matches(".admin-page .moderation-actions form")) return;
    if (event.defaultPrevented) return;
    event.preventDefault();
    const button = form.querySelector('[type="submit"]');
    if (button) button.disabled = true;
    try {
      const response = await fetch(form.action, { method: "POST", body: new FormData(form), headers: { "X-Requested-With": "XMLHttpRequest" } });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error(data.message || "Could not update this profile.");
      const record = form.closest(".admin-record");
      const activeTab = document.querySelector(".profile-tabs a.active");
      const selectedStatus = activeTab?.getAttribute("href")?.match(/status=(approved|pending|rejected|all)/)?.[1] || "pending";
      if (data.deleted) {
        record?.remove();
        updateProfileTabCount(data.previous_status, -1, true);
      } else {
        const status = record?.querySelector(".status");
        if (status) {
          status.className = `status status-${data.status}`;
          status.textContent = data.status_label;
        }
        if (data.previous_status !== data.status) {
          updateProfileTabCount(data.previous_status, -1);
          updateProfileTabCount(data.status, 1);
        }
        if (selectedStatus !== "all" && selectedStatus !== data.status) record?.remove();
      }
      showAdminNotice(data.message);
    } catch (error) {
      showAdminNotice(error.message || "Could not update this profile.", true);
    } finally {
      if (button) button.disabled = false;
    }
  });
});
