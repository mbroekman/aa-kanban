/**
 * aa-kanban - SortableJS and HTMX integration for Drag & Drop Kanban
 */
document.addEventListener("DOMContentLoaded", function () {
    // Board-specific drag-and-drop setup (Sortable) only applies on pages
    // that render a board (.kanban-board-container). Markdown image uploads
    // and the rest of this script run unconditionally below, since they're
    // also used on standalone pages like the ticket submission form.
    function initSortable(rootNode) {
        const boardContainer = document.querySelector(".kanban-board-container");
        const canWrite = boardContainer && boardContainer.dataset.canWrite === "true";
        if (!boardContainer || !canWrite) {
            return;
        }
        if (typeof Sortable === "undefined") {
            console.error("SortableJS is not loaded.");
            return;
        }

        const scope = (rootNode && rootNode.querySelectorAll) ? rootNode : boardContainer;
        let cardContainers = [];
        if (scope.classList && scope.classList.contains("kanban-cards")) {
            cardContainers = [scope];
        } else {
            cardContainers = scope.querySelectorAll(".kanban-cards");
        }

        cardContainers.forEach(function (container) {
            if (Sortable.get(container) || container.dataset.sortableBound === "true") {
                return;
            }
            container.dataset.sortableBound = "true";

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

                    updateListCounts();

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
                    .then(function (data) {
                        updateListCounts();
                        if (data && data.prompt_close_thread) {
                            showCloseThreadConfirm(data.card_id);
                        }
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

    function initColumnSortable() {
        const boardContainer = document.querySelector(".kanban-board-container");
        const canWrite = boardContainer && boardContainer.dataset.canWrite === "true";
        if (!boardContainer || !canWrite) {
            return;
        }
        if (typeof Sortable === "undefined") {
            return;
        }
        if (Sortable.get(boardContainer) || boardContainer.dataset.columnSortableBound === "true") {
            return;
        }
        boardContainer.dataset.columnSortableBound = "true";

        let columnsBeforeDrag = [];

        new Sortable(boardContainer, {
            group: "kanban-columns",
            draggable: ".kanban-column",
            handle: ".card-header",
            filter: "button, button *, input, a, a *, .btn, .btn *, .delete-list-btn, #add-column-placeholder",
            preventOnFilter: false,
            animation: 150,
            ghostClass: "kanban-column-ghost",
            chosenClass: "kanban-column-chosen",
            dragClass: "kanban-column-dragging",
            onStart: function () {
                columnsBeforeDrag = Array.from(boardContainer.querySelectorAll(".kanban-column"));
            },
            onMove: function (evt) {
                if (evt.related && evt.related.id === "add-column-placeholder") {
                    return false;
                }
                return true;
            },
            onEnd: function (evt) {
                const columnEl = evt.item;
                const listId = columnEl.dataset.listId;

                // Ensure add-column-placeholder stays at the very end
                const placeholder = boardContainer.querySelector("#add-column-placeholder");
                if (placeholder && placeholder.parentNode === boardContainer) {
                    boardContainer.appendChild(placeholder);
                }

                if (!listId) {
                    return;
                }

                const columns = Array.from(boardContainer.querySelectorAll(".kanban-column"));
                const newIndex = columns.indexOf(columnEl);

                if (newIndex === -1) {
                    return;
                }

                if (evt.oldDraggableIndex !== undefined && evt.newDraggableIndex !== undefined) {
                    if (evt.oldDraggableIndex === evt.newDraggableIndex) {
                        return;
                    }
                } else if (evt.oldIndex === evt.newIndex) {
                    return;
                }

                const moveUrl = columnEl.dataset.moveUrl || `/kanban/lists/${listId}/move/`;
                const csrfToken = getCsrfToken();
                const formData = new FormData();
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
                .catch(function (error) {
                    console.error("Failed to move column:", error);
                    showToast("Kanban Error", "Failed to move column. The board state has been reverted.", "danger");

                    // Revert all columns to original order
                    if (columnsBeforeDrag && columnsBeforeDrag.length > 0) {
                        columnsBeforeDrag.forEach(function (col) {
                            if (placeholder) {
                                boardContainer.insertBefore(col, placeholder);
                            } else {
                                boardContainer.appendChild(col);
                            }
                        });
                    }
                });
            },
        });
    }

    window.initKanbanSortable = initSortable;
    window.initKanbanColumnSortable = initColumnSortable;
    initSortable();
    initColumnSortable();

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

    // Card modal lifecycle & fallback
    const cardModalEl = document.getElementById("cardModal");
    if (cardModalEl) {
        cardModalEl.addEventListener("show.bs.modal", function (event) {
            const triggerEl = event.relatedTarget;
            if (!triggerEl) return;
            const cardEl = triggerEl.closest ? triggerEl.closest(".kanban-card") : null;
            if (!cardEl) return;
            // Native fallback only if HTMX is unavailable
            if (typeof htmx === "undefined") {
                const modalUrl = cardEl.getAttribute("hx-get") || cardEl.dataset.modalUrl;
                if (modalUrl) {
                    fetch(modalUrl, { credentials: "same-origin", headers: { "X-Requested-With": "XMLHttpRequest" } })
                        .then(function (res) { return res.text(); })
                        .then(function (html) {
                            const modalBody = document.getElementById("cardModalBody");
                            if (modalBody) {
                                modalBody.innerHTML = html;
                                initTooltips();
                                initMarkdownImageUploads();
                            }
                        })
                        .catch(function (err) {
                            console.error("Failed to load card modal:", err);
                        });
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

    // Prompt to close a ticket's Discord thread when moved to the last column
    window.showCloseThreadConfirm = function (cardId) {
        const modalEl = document.getElementById("closeThreadModal");
        if (!modalEl || typeof bootstrap === "undefined") return;

        const confirmBtn = document.getElementById("btn-confirm-close-thread");
        confirmBtn.dataset.cardId = cardId;

        if (!confirmBtn.dataset.bound) {
            confirmBtn.dataset.bound = "true";
            confirmBtn.addEventListener("click", function () {
                const targetCardId = confirmBtn.dataset.cardId;
                fetch(`/kanban/cards/${targetCardId}/close-thread/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCsrfToken(),
                        "X-Requested-With": "XMLHttpRequest",
                    },
                })
                .then(function (response) {
                    if (!response.ok) {
                        throw new Error(`Server returned HTTP ${response.status}`);
                    }
                    showToast("Kanban", "Discord thread closed.", "success");
                })
                .catch(function (error) {
                    console.error("Failed to close thread:", error);
                    showToast("Kanban Error", "Failed to close the Discord thread.", "danger");
                })
                .finally(function () {
                    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                    modal.hide();
                });
            });
        }

        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
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
        initSortable();
        initColumnSortable();
        initTooltips();
        updateListCounts();
        initMarkdownImageUploads();
    });

    // Also listen to htmx:load when dynamic content is inserted
    document.body.addEventListener('htmx:load', function(evt) {
        initSortable(evt.detail && evt.detail.elt ? evt.detail.elt : document);
        initColumnSortable();
        initTooltips();
        updateListCounts();
    });

    // Reset forms after successful HTMX post (description form is fully
    // replaced via its own OOB swap, so it never needs a reset here)
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.successful) {
            const elt = evt.detail.elt;
            if (elt && elt.id !== 'card-desc-form' && elt.tagName === 'FORM' && elt.hasAttribute('hx-post')) {
                elt.reset();
            }
        }
    });
});
