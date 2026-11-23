/**
 * Once Upon a Page - Storybook Rating & Review System
 * Interactive 1-5 Star Rating Modal with Optional Review & Skip Option.
 */

const StorybookRating = (function () {
    let modalInstance = null;
    let currentBookId = null;
    let currentBookTitle = '';
    let selectedRating = 0;
    let hoveredRating = 0;
    let completionCallback = null;
    let isSubmitting = false;

    const ratingDescriptions = {
        0: 'Tap a star to rate',
        1: '1 · Needs more magic 🌧️',
        2: '2 · It was okay 🌙',
        3: '3 · Good bedtime story! ⭐',
        4: '4 · Loved reading it! 💫',
        5: '5 · Pure magic! 🌟'
    };

    function init() {
        const modalEl = document.getElementById('storybookRatingModal');
        if (!modalEl) return;

        if (window.bootstrap && window.bootstrap.Modal) {
            modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl, {
                backdrop: 'static',
                keyboard: false
            });
        }

        const starSelector = document.getElementById('starRatingSelector');
        const starButtons = starSelector ? starSelector.querySelectorAll('.star-btn') : [];
        const feedbackLabel = document.getElementById('ratingFeedbackLabel');
        const reviewTextarea = document.getElementById('ratingReviewText');
        const charCount = document.getElementById('ratingCharCount');
        const submitBtn = document.getElementById('btnSubmitRating');
        const skipBtn = document.getElementById('btnSkipRating');
        const closeBtn = document.getElementById('btnRatingClose');

        // Star button interactions
        starButtons.forEach(btn => {
            const val = parseInt(btn.dataset.value, 10);

            btn.addEventListener('mouseenter', function () {
                hoveredRating = val;
                highlightStars(val);
                if (feedbackLabel) feedbackLabel.textContent = ratingDescriptions[val] || '';
            });

            btn.addEventListener('mouseleave', function () {
                hoveredRating = 0;
                highlightStars(selectedRating);
                if (feedbackLabel) {
                    feedbackLabel.textContent = ratingDescriptions[selectedRating] || ratingDescriptions[0];
                }
            });

            btn.addEventListener('click', function (e) {
                e.preventDefault();
                selectedRating = val;
                highlightStars(selectedRating);
                if (feedbackLabel) feedbackLabel.textContent = ratingDescriptions[val] || '';
                if (submitBtn) submitBtn.disabled = false;

                // Tiny sparkle at click position if sparkle function is available
                if (typeof window.createSparkleEffect === 'function') {
                    window.createSparkleEffect(e.clientX, e.clientY);
                }
            });
        });

        // Review character counter
        if (reviewTextarea && charCount) {
            reviewTextarea.addEventListener('input', function () {
                charCount.textContent = `${this.value.length} / 500`;
            });
        }

        // Submit action
        if (submitBtn) {
            submitBtn.addEventListener('click', function (e) {
                e.preventDefault();
                if (isSubmitting || selectedRating < 1 || !currentBookId) return;
                submitRating();
            });
        }

        // Skip action
        if (skipBtn) {
            skipBtn.addEventListener('click', function (e) {
                e.preventDefault();
                if (isSubmitting || !currentBookId) return;
                skipRating();
            });
        }

        // Close 'x' button (treated as skip)
        if (closeBtn) {
            closeBtn.addEventListener('click', function (e) {
                e.preventDefault();
                if (isSubmitting || !currentBookId) return;
                skipRating();
            });
        }
    }

    function highlightStars(count) {
        const starSelector = document.getElementById('starRatingSelector');
        if (!starSelector) return;
        const starButtons = starSelector.querySelectorAll('.star-btn');
        starButtons.forEach(btn => {
            const val = parseInt(btn.dataset.value, 10);
            if (val <= count) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    function resetModal() {
        selectedRating = 0;
        hoveredRating = 0;
        isSubmitting = false;

        highlightStars(0);

        const feedbackLabel = document.getElementById('ratingFeedbackLabel');
        if (feedbackLabel) feedbackLabel.textContent = ratingDescriptions[0];

        const reviewTextarea = document.getElementById('ratingReviewText');
        if (reviewTextarea) reviewTextarea.value = '';

        const charCount = document.getElementById('ratingCharCount');
        if (charCount) charCount.textContent = '0 / 500';

        const submitBtn = document.getElementById('btnSubmitRating');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="btn-content"><i class="fa-solid fa-wand-magic-sparkles me-1"></i> Submit Rating</span>';
        }

        const alertBox = document.getElementById('ratingAlertBox');
        if (alertBox) {
            alertBox.classList.add('d-none');
            alertBox.textContent = '';
        }

        const successBox = document.getElementById('ratingSuccessBox');
        if (successBox) successBox.classList.add('d-none');
    }

    function submitRating() {
        isSubmitting = true;
        const submitBtn = document.getElementById('btnSubmitRating');
        const skipBtn = document.getElementById('btnSkipRating');
        const reviewTextarea = document.getElementById('ratingReviewText');
        const alertBox = document.getElementById('ratingAlertBox');
        const successBox = document.getElementById('ratingSuccessBox');

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Saving magic...';
        }
        if (skipBtn) skipBtn.style.pointerEvents = 'none';
        if (alertBox) alertBox.classList.add('d-none');

        const payload = {
            rating: selectedRating,
            review_text: reviewTextarea ? reviewTextarea.value.trim() : ''
        };

        fetch(`/api/book/${currentBookId}/rate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.json().then(data => ({ status: res.status, ok: res.ok, data })))
        .then(result => {
            if (result.ok && result.data && result.data.success) {
                if (successBox) successBox.classList.remove('d-none');
                setTimeout(() => {
                    closeModal(true);
                }, 800);
            } else {
                isSubmitting = false;
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<span class="btn-content"><i class="fa-solid fa-wand-magic-sparkles me-1"></i> Submit Rating</span>';
                }
                if (skipBtn) skipBtn.style.pointerEvents = 'auto';
                if (alertBox) {
                    alertBox.textContent = (result.data && result.data.message) ? result.data.message : 'Could not submit rating. Please try again.';
                    alertBox.classList.remove('d-none');
                }
            }
        })
        .catch(err => {
            console.error('Error submitting rating:', err);
            isSubmitting = false;
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<span class="btn-content"><i class="fa-solid fa-wand-magic-sparkles me-1"></i> Submit Rating</span>';
            }
            if (skipBtn) skipBtn.style.pointerEvents = 'auto';
            if (alertBox) {
                alertBox.textContent = 'Connection error. Please try again.';
                alertBox.classList.remove('d-none');
            }
        });
    }

    function skipRating() {
        isSubmitting = true;
        const skipBtn = document.getElementById('btnSkipRating');
        if (skipBtn) skipBtn.textContent = 'Skipping...';

        fetch(`/api/book/${currentBookId}/skip-rating`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({})
        })
        .catch(err => {
            console.warn('Skip rating call:', err);
        })
        .finally(() => {
            closeModal(false);
        });
    }

    function closeModal(submitted) {
        if (modalInstance) {
            modalInstance.hide();
        } else {
            const modalEl = document.getElementById('storybookRatingModal');
            if (modalEl) modalEl.classList.remove('show');
        }

        const cb = completionCallback;
        completionCallback = null;
        isSubmitting = false;

        if (typeof cb === 'function') {
            cb(submitted, currentBookId);
        }
    }

    return {
        open: function (bookId, bookTitle, callback) {
            currentBookId = bookId;
            currentBookTitle = bookTitle || 'Storybook';
            completionCallback = callback;

            const modalEl = document.getElementById('storybookRatingModal');
            if (!modalEl) {
                console.warn('Rating modal element not found on page.');
                if (typeof callback === 'function') callback(false, bookId);
                return;
            }

            if (!modalInstance && window.bootstrap && window.bootstrap.Modal) {
                modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl, {
                    backdrop: 'static',
                    keyboard: false
                });
            }

            resetModal();

            const titleEl = document.getElementById('ratingModalBookTitle');
            if (titleEl) titleEl.textContent = currentBookTitle;

            if (modalInstance) {
                modalInstance.show();
            } else {
                modalEl.classList.add('show');
                modalEl.style.display = 'block';
            }
        },
        init: init
    };
})();

document.addEventListener('DOMContentLoaded', function () {
    StorybookRating.init();
});
