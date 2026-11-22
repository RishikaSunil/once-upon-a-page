/**
 * Once Upon a Page - Admin Panel JavaScript
 * Handles sidebar toggling, live image previews, dynamic storybook spread builder,
 * spread reordering, and action confirmations.
 */

document.addEventListener('DOMContentLoaded', function () {

    // =========================================================================
    // 1. Mobile Sidebar Toggle
    // =========================================================================
    const sidebarToggle = document.getElementById('adminSidebarToggle');
    const adminSidebar = document.getElementById('adminSidebar');

    if (sidebarToggle && adminSidebar) {
        sidebarToggle.addEventListener('click', function (e) {
            e.stopPropagation();
            adminSidebar.classList.toggle('open');
        });

        document.addEventListener('click', function (e) {
            if (adminSidebar.classList.contains('open') && 
                !adminSidebar.contains(e.target) && 
                e.target !== sidebarToggle) {
                adminSidebar.classList.remove('open');
            }
        });

        // Close sidebar on link click on mobile
        adminSidebar.querySelectorAll('.admin-nav-link').forEach(function (link) {
            link.addEventListener('click', function () {
                if (window.innerWidth < 992) {
                    adminSidebar.classList.remove('open');
                }
            });
        });
    }

    // =========================================================================
    // 2. Image File Input Instant Preview
    // =========================================================================
    document.querySelectorAll('.admin-image-input').forEach(function (input) {
        input.addEventListener('change', function () {
            const previewId = this.dataset.previewTarget;
            const previewEl = document.getElementById(previewId);
            if (previewEl && this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewEl.src = e.target.result;
                    previewEl.style.display = 'block';
                    const placeholder = previewEl.closest('.page-preview-box')?.querySelector('.upload-placeholder');
                    if (placeholder) placeholder.style.display = 'none';
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    // =========================================================================
    // 3. Dynamic Storybook Spread Builder (Add / Remove / Reorder)
    // =========================================================================
    const spreadsContainer = document.getElementById('storybookSpreadsContainer');
    const addSpreadBtn = document.getElementById('addSpreadBtn');

    if (spreadsContainer && addSpreadBtn) {
        addSpreadBtn.addEventListener('click', function () {
            const spreadCards = spreadsContainer.querySelectorAll('.spread-card');
            const newIndex = spreadCards.length + 1;
            const spreadId = `spread_${Date.now()}`;

            const spreadHtml = `
                <div class="spread-card shadow-sm" id="${spreadId}" data-spread-index="${newIndex}">
                    <div class="spread-header d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center gap-2">
                            <span class="badge bg-pastel-lavender text-lavender-deep fw-bold px-2 py-1">Spread ${newIndex}</span>
                            <span class="spread-page-numbers text-muted small">(Pages ${(newIndex * 2) - 1} & ${newIndex * 2})</span>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <button type="button" class="btn btn-sm btn-outline-secondary btn-move-up" title="Move Up"><i class="fa-solid fa-arrow-up"></i></button>
                            <button type="button" class="btn btn-sm btn-outline-secondary btn-move-down" title="Move Down"><i class="fa-solid fa-arrow-down"></i></button>
                            <button type="button" class="btn btn-sm btn-outline-danger btn-delete-spread" title="Delete Spread"><i class="fa-solid fa-trash"></i></button>
                        </div>
                    </div>

                    <div class="row g-3">
                        <!-- Left Page -->
                        <div class="col-md-6 border-end">
                            <div class="p-2">
                                <h6 class="fw-bold text-lavender-deep mb-2">Left Page (Illustration & Details)</h6>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold">Page Illustration</label>
                                    <div class="page-preview-box mb-2">
                                        <img src="" class="page-preview-image" id="preview_left_${spreadId}" style="display: none;">
                                        <div class="upload-placeholder text-center p-3">
                                            <i class="fa-solid fa-cloud-arrow-up fs-2 text-muted mb-2"></i>
                                            <p class="small text-muted mb-0">Choose image or drag here</p>
                                        </div>
                                    </div>
                                    <input type="file" name="spread_illustration_${newIndex}" class="form-control form-control-sm admin-image-input" accept="image/*" data-preview-target="preview_left_${spreadId}">
                                </div>
                                <div class="mb-2">
                                    <label class="form-label small fw-bold">Chapter / Scene Title</label>
                                    <input type="text" name="spread_title_${newIndex}" class="form-control form-control-sm" placeholder="e.g. A New Journey">
                                </div>
                            </div>
                        </div>

                        <!-- Right Page -->
                        <div class="col-md-6">
                            <div class="p-2">
                                <h6 class="fw-bold text-lavender-deep mb-2">Right Page (Story Prose)</h6>
                                <div class="mb-3">
                                    <label class="form-label small fw-bold">Story Text</label>
                                    <textarea name="spread_text_${newIndex}" class="form-control" rows="4" placeholder="Enter bedtime story text for this spread..."></textarea>
                                </div>
                                <div class="mb-2">
                                    <label class="form-label small fw-bold">Character Dialogue or Moral Note (Optional)</label>
                                    <input type="text" name="spread_dialogue_${newIndex}" class="form-control form-control-sm" placeholder="e.g. 'Look at that beautiful star!' whispered Lily.">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            spreadsContainer.insertAdjacentHTML('beforeend', spreadHtml);
            reindexSpreads();
            setupNewSpreadListeners();
        });

        // Event delegation for spread controls (Move up, Move down, Delete)
        spreadsContainer.addEventListener('click', function (e) {
            const btnDelete = e.target.closest('.btn-delete-spread');
            if (btnDelete) {
                const card = btnDelete.closest('.spread-card');
                if (card && confirm('Are you sure you want to delete this spread?')) {
                    card.remove();
                    reindexSpreads();
                }
                return;
            }

            const btnUp = e.target.closest('.btn-move-up');
            if (btnUp) {
                const card = btnUp.closest('.spread-card');
                const prev = card.previousElementSibling;
                if (prev && prev.classList.contains('spread-card')) {
                    spreadsContainer.insertBefore(card, prev);
                    reindexSpreads();
                }
                return;
            }

            const btnDown = e.target.closest('.btn-move-down');
            if (btnDown) {
                const card = btnDown.closest('.spread-card');
                const next = card.nextElementSibling;
                if (next && next.classList.contains('spread-card')) {
                    spreadsContainer.insertBefore(next, card);
                    reindexSpreads();
                }
                return;
            }
        });

        function reindexSpreads() {
            const cards = spreadsContainer.querySelectorAll('.spread-card');
            cards.forEach((card, idx) => {
                const num = idx + 1;
                card.setAttribute('data-spread-index', num);
                const badge = card.querySelector('.badge');
                if (badge) badge.textContent = `Spread ${num}`;
                const pageNumbers = card.querySelector('.spread-page-numbers');
                if (pageNumbers) pageNumbers.textContent = `(Pages ${(num * 2) - 1} & ${num * 2})`;

                // Update input names for sequential processing
                const fileInput = card.querySelector('input[type="file"]');
                if (fileInput) fileInput.name = `spread_illustration_${num}`;
                const titleInput = card.querySelector('input[type="text"][name^="spread_title"]');
                if (titleInput) titleInput.name = `spread_title_${num}`;
                const textInput = card.querySelector('textarea[name^="spread_text"]');
                if (textInput) textInput.name = `spread_text_${num}`;
                const dialogueInput = card.querySelector('input[type="text"][name^="spread_dialogue"]');
                if (dialogueInput) dialogueInput.name = `spread_dialogue_${num}`;
            });

            // Update total spreads hidden counter
            const countInput = document.getElementById('totalSpreadsCount');
            if (countInput) countInput.value = cards.length;
        }

        function setupNewSpreadListeners() {
            spreadsContainer.querySelectorAll('.admin-image-input').forEach(function (input) {
                input.onchange = function () {
                    const previewId = this.dataset.previewTarget;
                    const previewEl = document.getElementById(previewId);
                    if (previewEl && this.files && this.files[0]) {
                        const reader = new FileReader();
                        reader.onload = function (e) {
                            previewEl.src = e.target.result;
                            previewEl.style.display = 'block';
                            const placeholder = previewEl.closest('.page-preview-box')?.querySelector('.upload-placeholder');
                            if (placeholder) placeholder.style.display = 'none';
                        };
                        reader.readAsDataURL(this.files[0]);
                    }
                };
            });
        }
    }

    // =========================================================================
    // 4. Form Action Confirmation Helpers
    // =========================================================================
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            const msg = this.dataset.confirm || 'Are you sure you want to proceed?';
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });

    // =========================================================================
    // 5. Welcome Page Video & Image Media Manager
    // =========================================================================
    const bgTypePlain = document.getElementById('bgTypePlain');
    const bgTypeImage = document.getElementById('bgTypeImage');
    const bgTypeVideo = document.getElementById('bgTypeVideo');
    const inputWelcomeBg = document.getElementById('input_welcome_bg');
    const inputWelcomeVideo = document.getElementById('input_welcome_video');
    const previewWelcomeBg = document.getElementById('preview_welcome_bg');
    const previewWelcomeVideo = document.getElementById('preview_welcome_video');
    const videoPlaceholder = document.getElementById('video_preview_placeholder');
    const mockupBgPlain = document.getElementById('mockup_bg_plain');
    const mockupBgImg = document.getElementById('mockup_bg_img');
    const mockupBgVideo = document.getElementById('mockup_bg_video');

    function syncWelcomeMockupView() {
        if (bgTypePlain && bgTypePlain.checked) {
            if (mockupBgPlain) mockupBgPlain.style.display = 'block';
            if (mockupBgImg) mockupBgImg.style.display = 'none';
            if (mockupBgVideo) mockupBgVideo.style.display = 'none';
        } else if (bgTypeVideo && bgTypeVideo.checked) {
            if (mockupBgPlain) mockupBgPlain.style.display = 'none';
            if (mockupBgImg) mockupBgImg.style.display = 'none';
            if (mockupBgVideo) {
                mockupBgVideo.style.display = 'block';
                mockupBgVideo.play().catch(() => {});
            }
        } else {
            if (mockupBgPlain) mockupBgPlain.style.display = 'none';
            if (mockupBgVideo) mockupBgVideo.style.display = 'none';
            if (mockupBgImg) mockupBgImg.style.display = 'block';
        }
    }

    if (bgTypePlain) bgTypePlain.addEventListener('change', syncWelcomeMockupView);
    if (bgTypeImage) bgTypeImage.addEventListener('change', syncWelcomeMockupView);
    if (bgTypeVideo) bgTypeVideo.addEventListener('change', syncWelcomeMockupView);

    // Video File Selection & Instant Preview
    if (inputWelcomeVideo && previewWelcomeVideo) {
        inputWelcomeVideo.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const videoUrl = URL.createObjectURL(file);

                previewWelcomeVideo.src = videoUrl;
                previewWelcomeVideo.style.display = 'block';
                if (videoPlaceholder) videoPlaceholder.style.display = 'none';
                previewWelcomeVideo.play().catch(() => {});

                if (mockupBgVideo) {
                    mockupBgVideo.src = videoUrl;
                    mockupBgVideo.style.display = 'block';
                    mockupBgVideo.play().catch(() => {});
                }
                if (mockupBgImg) mockupBgImg.style.display = 'none';
                if (bgTypeVideo) bgTypeVideo.checked = true;
            }
        });
    }

    // Image File Selection sync to Mockup
    if (inputWelcomeBg && mockupBgImg) {
        inputWelcomeBg.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    if (mockupBgImg) {
                        mockupBgImg.src = e.target.result;
                        mockupBgImg.style.display = 'block';
                    }
                    if (mockupBgVideo) mockupBgVideo.style.display = 'none';
                    if (bgTypeImage) bgTypeImage.checked = true;
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    // Live typing sync for Welcome Page inputs
    const inputHeading = document.querySelector('input[name="welcome_heading"]');
    const inputLabel = document.querySelector('input[name="welcome_label"]');
    const inputSubtitle = document.querySelector('textarea[name="welcome_subtitle"]');
    const inputBtn = document.querySelector('input[name="welcome_button_text"]');

    if (inputHeading) {
        inputHeading.addEventListener('input', function () {
            const el = document.getElementById('mockup_heading');
            if (el) el.textContent = this.value || 'Welcome to a World of Little Stories';
        });
    }
    if (inputLabel) {
        inputLabel.addEventListener('input', function () {
            const el = document.getElementById('mockup_label');
            if (el) el.textContent = this.value || 'Cozy Bedtime Stories';
        });
    }
    if (inputSubtitle) {
        inputSubtitle.addEventListener('input', function () {
            const el = document.getElementById('mockup_subtitle');
            if (el) el.textContent = this.value || "Every little story holds a little magic. Come, let's explore!";
        });
    }
    if (inputBtn) {
        inputBtn.addEventListener('input', function () {
            const el = document.getElementById('mockup_button');
            if (el) el.textContent = this.value || 'Enter the Story World ✨';
        });
    }

});
