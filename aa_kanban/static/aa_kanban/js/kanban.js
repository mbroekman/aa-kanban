/**
 * aa-kanban - SortableJS and HTMX integration for Drag & Drop Kanban
 */
document.addEventListener("DOMContentLoaded", function () {
    const boardContainer = document.querySelector(".kanban-board-container");
    if (!boardContainer) {
        return;
    }

    const canWrite = boardContainer.dataset.canWrite === "true";
    if (!canWrite) {
        // Read-only access: do not initialize SortableJS
        return;
    }

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

    function updateListCounts() {
        document.querySelectorAll(".kanban-column").forEach(function (col) {
            const countBadge = col.querySelector(".card-count-badge");
            const cards = col.querySelectorAll(".kanban-card");
            if (countBadge) {
                countBadge.textContent = cards.length;
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
        
        // Re-initialize tooltips for new content
        initTooltips();
    });

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
});
