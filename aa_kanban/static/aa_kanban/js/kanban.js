/**
 * aa-kanban - SortableJS and HTMX integration for Drag & Drop Kanban
 */
document.addEventListener("DOMContentLoaded", function () {
    const boardContainer = document.querySelector(".kanban-board-container");
    if (!boardContainer) {
        return;
    }

    const canWrite = boardContainer.dataset.canWrite === "true";
    if (canWrite) {
        const cardContainers = document.querySelectorAll(".kanban-cards");
    cardContainers.forEach(function (container) {
        if (typeof Sortable === "undefined") {
            console.error("SortableJS is not loaded.");
            return;
        }

        new Sortable(container, {
            group: "kanban-cards",
            animation: 150,
            ghostClass: "kanban-card-ghost",
            chosenClass: "kanban-card-chosen",
            dragClass: "kanban-card-dragging",
            handle: ".kanban-card",
            onMove: function (evt) {
                const targetColumnEl = evt.to.closest('.kanban-column');
                if (!targetColumnEl) return true;

                if (evt.from === evt.to) {
                    return true;
                }

                const headerEl = targetColumnEl.querySelector('.card-header');
                const wipLimit = headerEl ? parseInt(headerEl.dataset.wipLimit || '0', 10) : parseInt(targetColumnEl.dataset.wipLimit || '0', 10);

                if (wipLimit > 0) {
                    const currentCards = evt.to.querySelectorAll('.kanban-card:not(.kanban-card-ghost)').length;
                    if (currentCards >= wipLimit) {
                        return false; // Prevent move visually
                    }
                }
                return true;
            },
            onEnd: function (evt) {
                const cardEl = evt.item;
                const cardId = cardEl.dataset.cardId;
                const targetListEl = evt.to;
                const targetListId = targetListEl.dataset.listId;
                const newIndex = evt.newIndex;

                if (!cardId || !targetListId) {
                    return;
                }

                // If same list and same index, no API call needed
                if (evt.from === evt.to && evt.oldIndex === evt.newIndex) {
                    return;
                }

                const moveUrl = cardEl.dataset.moveUrl || `/kanban/cards/${cardId}/move/`;
                const csrfToken = getCsrfToken();

                const formData = new FormData();
                formData.append("target_list_id", targetListId);
                formData.append("new_position", newIndex);

                fetch(moveUrl, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: formData,
                })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error(`Server returned HTTP ${response.status}`);
                    }
                    return response.json();
                })
                .then(function () {
                    updateListCounts();
                })
                .catch(function (error) {
                    console.error("Failed to move card:", error);
                    showToast("Kanban Error", "Failed to move card. The board state has been reverted.", "danger");

                    // Revert card back to original position in DOM
                    if (evt.from && evt.item) {
                        const originalNextSibling = evt.from.children[evt.oldIndex] || null;
                        evt.from.insertBefore(evt.item, originalNextSibling);
                        updateListCounts();
                    }
                });
            },
        });
    });
    }

    function updateListCounts() {
        document.querySelectorAll(".kanban-column").forEach(function (col) {
            const countBadge = col.querySelector(".card-count-badge");
            const cards = col.querySelectorAll(".kanban-card");
            const emptyPlaceholder = col.querySelector(".empty-placeholder");
            if (countBadge) {
                const header = col.querySelector(".card-header");
                const wipLimit = header ? parseInt(header.dataset.wipLimit || '0', 10) : parseInt(col.dataset.wipLimit || '0', 10);

                if (wipLimit > 0) {
                    countBadge.textContent = cards.length + "/" + wipLimit;
                    if (cards.length >= wipLimit) {
                        countBadge.classList.remove("bg-info", "bg-secondary");
                        countBadge.classList.add("bg-danger");
                    } else {
                        countBadge.classList.remove("bg-danger", "bg-secondary");
                        countBadge.classList.add("bg-info");
                    }
                } else {
                    countBadge.textContent = cards.length;
                    countBadge.classList.remove("bg-danger", "bg-info");
                    countBadge.classList.add("bg-secondary");
                }
            }
            if (emptyPlaceholder) {
                if (cards.length > 0) {
                    emptyPlaceholder.style.display = 'none';
                } else {
                    emptyPlaceholder.style.display = 'block';
                }
            }
        });
    }

    function getCsrfToken() {
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input && input.value) {
            return input.value;
        }
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 10) === "csrftoken=") {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        return cookieValue || "";
    }

    function showToast(title, message, variant) {
        let container = document.getElementById("kanban-toast-container");
        if (!container) {
            container = document.createElement("div");
            container.id = "kanban-toast-container";
            container.className = "toast-container position-fixed bottom-0 end-0 p-3";
            container.style.zIndex = "1090";
            document.body.appendChild(container);
        }

        const toastEl = document.createElement("div");
        toastEl.className = `toast align-items-center text-bg-${variant || 'danger'} border-0 show`;
        toastEl.setAttribute("role", "alert");
        toastEl.setAttribute("aria-live", "assertive");
        toastEl.setAttribute("aria-atomic", "true");
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}:</strong> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        container.appendChild(toastEl);
        setTimeout(function () {
            if (toastEl.parentNode) {
                toastEl.remove();
            }
        }, 5000);
    }

    // Modal close event listener for HTMX
    document.body.addEventListener('closeModal', function() {
        // List modal
        const listModalEl = document.getElementById('listModal');
        if (listModalEl) {
            const listModal = bootstrap.Modal.getInstance(listModalEl);
            if (listModal) listModal.hide();
        }

        // Card modal
        const cardModalEl = document.getElementById('cardModal');
        if (cardModalEl) {
            const cardModal = bootstrap.Modal.getInstance(cardModalEl);
            if (cardModal) cardModal.hide();
        }

        // Re-initialize tooltips for new content
        initTooltips();
    });

    // Card modal lifecycle & dynamic loading via Bootstrap show.bs.modal
    const cardModalEl = document.getElementById("cardModal");
    if (cardModalEl) {
        cardModalEl.addEventListener("show.bs.modal", function (event) {
            const triggerEl = event.relatedTarget;
            if (!triggerEl) {
                return;
            }
            const modalUrl = triggerEl.dataset.modalUrl || triggerEl.getAttribute("data-modal-url") || triggerEl.getAttribute("hx-get");
            if (modalUrl) {
                const modalBody = document.getElementById("cardModalBody");
                if (modalBody) {
                    modalBody.innerHTML = `
                        <div class="modal-body text-center py-5">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                        </div>`;
                }
                if (typeof htmx !== "undefined") {
                    htmx.ajax("GET", modalUrl, { target: "#cardModalBody", swap: "innerHTML" });
                }
            }
        });

        cardModalEl.addEventListener("hidden.bs.modal", function () {
            const modalBody = document.getElementById("cardModalBody");
            if (modalBody) {
                modalBody.innerHTML = `
                    <div class="modal-body text-center py-5">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                    </div>`;
            }
        });
    }

    function initTooltips() {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        if (typeof bootstrap !== 'undefined') {
            [...tooltipTriggerList].map(el => {
                const instance = bootstrap.Tooltip.getInstance(el);
                if (instance) {
                    instance.dispose();
                }
                new bootstrap.Tooltip(el);
            });
        }
    }

    // Initialize tooltips on load
    initTooltips();
    initMarkdownImageUploads();

    // Toggle Card Description View/Edit mode
    window.toggleCardDescMode = function (mode) {
        const viewEl = document.getElementById("card-desc-view");
        const formEl = document.getElementById("card-desc-form");
        const editBtn = document.getElementById("btn-card-desc-edit");
        const viewBtn = document.getElementById("btn-card-desc-view");
        const textarea = document.getElementById("card-desc-textarea");

        if (mode === "edit") {
            if (viewEl) viewEl.classList.add("d-none");
            if (formEl) formEl.classList.remove("d-none");
            if (editBtn) editBtn.classList.add("d-none");
            if (viewBtn) viewBtn.classList.remove("d-none");
            if (textarea) textarea.focus();
        } else {
            if (formEl) formEl.classList.add("d-none");
            if (viewEl) viewEl.classList.remove("d-none");
            if (editBtn) editBtn.classList.remove("d-none");
            if (viewBtn) viewBtn.classList.add("d-none");
        }
    };

    // Markdown Image Upload Initialization (Paste, Drag & Drop, File Picker)
    function initMarkdownImageUploads() {
        document.querySelectorAll(".kanban-markdown-textarea").forEach(function (textarea) {
            if (textarea.dataset.imageUploadBound === "true") return;
            textarea.dataset.imageUploadBound = "true";

            const uploadUrl = textarea.dataset.uploadUrl || "/kanban/api/upload-image/";
            const wrapper = textarea.closest(".kanban-markdown-editor-wrapper") || textarea;

            // 1. Paste handler (Ctrl+V)
            textarea.addEventListener("paste", function (e) {
                const clipboardData = e.clipboardData || window.clipboardData;
                if (!clipboardData || !clipboardData.items) return;

                for (let i = 0; i < clipboardData.items.length; i++) {
                    const item = clipboardData.items[i];
                    if (item.type.indexOf("image") === 0) {
                        e.preventDefault();
                        const file = item.getAsFile();
                        if (file) {
                            uploadAndInsert(file, textarea, uploadUrl);
                        }
                        break;
                    }
                }
            });

            // 2. Drag & Drop handler
            wrapper.addEventListener("dragover", function (e) {
                e.preventDefault();
                e.stopPropagation();
                wrapper.classList.add("dragover");
            });

            wrapper.addEventListener("dragleave", function (e) {
                e.preventDefault();
                e.stopPropagation();
                wrapper.classList.remove("dragover");
            });

            wrapper.addEventListener("drop", function (e) {
                e.preventDefault();
                e.stopPropagation();
                wrapper.classList.remove("dragover");

                if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                    const file = e.dataTransfer.files[0];
                    if (file.type.indexOf("image") === 0) {
                        uploadAndInsert(file, textarea, uploadUrl);
                    }
                }
            });

            // 3. Attach Image Button handler (Card or Ticket)
            const parent = textarea.closest("form") || textarea.parentElement;
            const attachBtn = parent ? parent.querySelector("#btn-attach-card-img, #btn-attach-ticket-img") : null;
            if (attachBtn && !attachBtn.dataset.bound) {
                attachBtn.dataset.bound = "true";
                const fileInput = document.createElement("input");
                fileInput.type = "file";
                fileInput.accept = "image/png, image/jpeg, image/gif, image/webp";
                fileInput.style.display = "none";
                document.body.appendChild(fileInput);

                attachBtn.addEventListener("click", function () {
                    fileInput.click();
                });

                fileInput.addEventListener("change", function () {
                    if (fileInput.files && fileInput.files.length > 0) {
                        uploadAndInsert(fileInput.files[0], textarea, uploadUrl);
                        fileInput.value = "";
                    }
                });
            }
        });
    }

    function uploadAndInsert(file, textarea, uploadUrl) {
        if (!file) return;

        if (file.size > 5 * 1024 * 1024) {
            showToast("Upload Error", "Image file exceeds 5MB limit.", "danger");
            return;
        }

        const safeFilename = file.name || "image.png";
        const placeholder = `\n![Uploading ${safeFilename}...]()\n`;
        const startPos = textarea.selectionStart || textarea.value.length;
        const endPos = textarea.selectionEnd || textarea.value.length;
        const textBefore = textarea.value.substring(0, startPos);
        const textAfter = textarea.value.substring(endPos);

        textarea.value = textBefore + placeholder + textAfter;
        textarea.selectionStart = textarea.selectionEnd = startPos + placeholder.length;

        const formData = new FormData();
        formData.append("image", file);

        fetch(uploadUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCsrfToken(),
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData,
        })
        .then(function (response) {
            if (!response.ok) {
                return response.json().then(function (errData) {
                    throw new Error(errData.error || `Upload failed (HTTP ${response.status})`);
                });
            }
            return response.json();
        })
        .then(function (data) {
            const markdownImg = `\n![${data.filename || safeFilename}](${data.url})\n`;
            textarea.value = textarea.value.replace(placeholder, markdownImg);
            textarea.dispatchEvent(new Event("input", { bubbles: true }));
        })
        .catch(function (error) {
            console.error("Image upload failed:", error);
            textarea.value = textarea.value.replace(placeholder, "");
            showToast("Upload Failed", error.message || "Failed to upload image.", "danger");
        });
    }

    // Initialize after HTMX swaps
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        initTooltips();
        updateListCounts();
        initMarkdownImageUploads();
    });

    // Reset forms after successful HTMX post (except description edit form)
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.successful) {
            const elt = evt.detail.elt;
            if (elt && elt.id === 'card-desc-form') {
                toggleCardDescMode('view');
            } else if (elt && elt.tagName === 'FORM' && elt.hasAttribute('hx-post')) {
                elt.reset();
            }
        }
    });
});
