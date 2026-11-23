/**
 * Twinkle - Interactive Storybook Engine
 * Supports:
 * 1. Physical 3D closed book stage with realistic cover, spine & golden glow
 * 2. Fluid 3D cover-swing opening transition into two-page reader
 * 3. Two-page spread reading with StPageFlip.js & Web Audio page turn sound
 * 4. Auto-saving page reading progress to MySQL via AJAX (/api/reading-history/save)
 * 5. Automatic resume at last-read page
 * 6. "Close Book" control to return to 3D closed book stage
 */

document.addEventListener('DOMContentLoaded', function () {
    const readerConfig = document.getElementById('readerConfig');
    const bookId = readerConfig ? parseInt(readerConfig.dataset.bookId || '1', 10) : 1;
    const initialLastPage = readerConfig ? parseInt(readerConfig.dataset.lastReadPage || '1', 10) : 1;
    const totalPages = readerConfig ? parseInt(readerConfig.dataset.totalPages || '16', 10) : 16;

    // Viewport stages
    const closedBookStage = document.getElementById('closedBookStage');
    const openBookStage = document.getElementById('openBookStage');
    const closedBookTrigger = document.getElementById('closedBookTrigger');
    const openBookActionBtn = document.getElementById('openBookActionBtn');
    const closeBookNavBtn = document.getElementById('closeBookNavBtn');
    const closeBookBottomBtn = document.getElementById('closeBookBottomBtn');

    // Controls
    const bookElement = document.getElementById('twinkleBook');
    const pageIndicator = document.getElementById('pageIndicator');
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    const soundToggleBtn = document.getElementById('soundToggleBtn');
    const soundIcon = document.getElementById('soundIcon');

    let pageFlipInstance = null;
    let isBookOpen = false;
    let soundEnabled = true;
    let currentPageIndex = 0;

    // Reading Preferences: Night Sky Atmosphere & Page Turn Whispers
    function isPageTurnWhispersEnabled() {
        const stored = localStorage.getItem('storybook_page_turn_whispers');
        if (stored !== null) return stored === 'true';
        if (window.USER_PREFS && window.USER_PREFS.page_turn_whispers !== undefined) {
            return Boolean(window.USER_PREFS.page_turn_whispers);
        }
        return true;
    }

    function isNightSkyAtmosphereEnabled() {
        const stored = localStorage.getItem('storybook_night_sky');
        if (stored !== null) return stored === 'true';
        if (window.USER_PREFS && window.USER_PREFS.night_sky !== undefined) {
            return Boolean(window.USER_PREFS.night_sky);
        }
        return true;
    }

    function applyNightSkyAtmosphere() {
        const isEnabled = isNightSkyAtmosphereEnabled();
        document.documentElement.setAttribute('data-night-sky', isEnabled ? 'true' : 'false');
        if (isEnabled) {
            document.body.classList.remove('night-sky-disabled');
        } else {
            document.body.classList.add('night-sky-disabled');
        }
    }
    applyNightSkyAtmosphere();

    // Sync settings if changed in another window/tab
    window.addEventListener('storage', function (e) {
        if (e.key === 'storybook_night_sky') {
            applyNightSkyAtmosphere();
            const amb = document.getElementById('ambientToggle');
            if (amb) amb.checked = (e.newValue !== 'false');
        } else if (e.key === 'storybook_page_turn_whispers') {
            const snd = document.getElementById('soundToggle');
            if (snd) snd.checked = (e.newValue !== 'false');
        }
    });

    // =========================================================================
    // 1. Web Audio API Natural Paper Sound Synthesizer (Mobile-Friendly Singleton)
    // =========================================================================
    let sharedAudioCtx = null;
    let cachedPaperNoiseBuffer = null;

    function getAudioContext() {
        if (!sharedAudioCtx) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (AudioContextClass) {
                sharedAudioCtx = new AudioContextClass();
            }
        }
        return sharedAudioCtx;
    }

    // AudioContext unlocking for mobile browsers (iOS Safari & Android Chrome)
    function unlockAudioContext() {
        const ctx = getAudioContext();
        if (!ctx) return;

        if (ctx.state === 'suspended') {
            ctx.resume().catch(() => {});
        }

        // WebKit/iOS audio pipeline unlock: play a silent 1-sample buffer inside user gesture
        try {
            const buffer = ctx.createBuffer(1, 1, 22050);
            const source = ctx.createBufferSource();
            source.buffer = buffer;
            source.connect(ctx.destination);
            source.start(0);
        } catch (e) {}
    }

    // Pre-cache the paper flutter noise buffer once ctx is active
    function getPaperNoiseBuffer(ctx) {
        if (!cachedPaperNoiseBuffer || cachedPaperNoiseBuffer.sampleRate !== ctx.sampleRate) {
            const bufferSize = Math.floor(ctx.sampleRate * 0.22); // 220ms
            const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {
                data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.4));
            }
            cachedPaperNoiseBuffer = buffer;
        }
        return cachedPaperNoiseBuffer;
    }

    function synthesizePaperTurn(ctx) {
        try {
            const buffer = getPaperNoiseBuffer(ctx);
            const noise = ctx.createBufferSource();
            noise.buffer = buffer;

            // Bandpass filter centered around paper swish frequency
            const filter = ctx.createBiquadFilter();
            filter.type = 'bandpass';
            const now = ctx.currentTime;
            filter.frequency.setValueAtTime(1600, now);
            filter.Q.setValueAtTime(1.5, now);
            filter.frequency.exponentialRampToValueAtTime(800, now + 0.2);

            // Gentle volume envelope
            const gain = ctx.createGain();
            gain.gain.setValueAtTime(0.01, now);
            gain.gain.linearRampToValueAtTime(0.32, now + 0.04);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.21);

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(ctx.destination);

            noise.start(now);
            noise.stop(now + 0.22);
        } catch (err) {
            console.warn('Synthesize audio error:', err);
        }
    }

    function playPageTurnSound() {
        if (!soundEnabled) return; // Master reader audio button
        if (!isPageTurnWhispersEnabled()) return; // Page Turn Whispers preference setting
        try {
            const ctx = getAudioContext();
            if (!ctx) return;

            if (ctx.state === 'suspended') {
                ctx.resume().then(() => {
                    synthesizePaperTurn(ctx);
                }).catch(() => {});
                return;
            }

            synthesizePaperTurn(ctx);
        } catch (e) {
            console.warn('Audio note:', e);
        }
    }

    // Register user gesture listeners to unlock AudioContext early
    const audioUnlockEvents = ['touchstart', 'touchend', 'pointerdown', 'mousedown', 'click'];
    function handleAudioUnlockGesture() {
        unlockAudioContext();
        const ctx = getAudioContext();
        if (ctx && ctx.state === 'running') {
            audioUnlockEvents.forEach(evt => {
                window.removeEventListener(evt, handleAudioUnlockGesture, { capture: true });
                document.removeEventListener(evt, handleAudioUnlockGesture, { capture: true });
            });
        }
    }
    audioUnlockEvents.forEach(evt => {
        window.addEventListener(evt, handleAudioUnlockGesture, { capture: true, passive: true });
        document.addEventListener(evt, handleAudioUnlockGesture, { capture: true, passive: true });
    });

    if (soundToggleBtn && soundIcon) {
        soundToggleBtn.addEventListener('click', function () {
            unlockAudioContext();
            soundEnabled = !soundEnabled;
            if (soundEnabled) {
                soundIcon.className = 'fa-solid fa-volume-high';
                soundToggleBtn.title = 'Sound on';
                playPageTurnSound();
            } else {
                soundIcon.className = 'fa-solid fa-volume-xmark text-muted';
                soundToggleBtn.title = 'Sound muted';
            }
        });
    }

    const isPreviewMode = readerConfig ? (readerConfig.dataset.isPreview === 'true') : false;

    // =========================================================================
    // 2. Optimized Reading Progress Saving (Debounced to Avoid DB Contention)
    // =========================================================================
    let saveDebounceTimer = null;
    let lastSavedPage = null;

    function saveReadingProgress(pageNumber, immediate = false) {
        if (isPreviewMode) return;
        if (!pageNumber || pageNumber < 1) return;
        if (pageNumber === lastSavedPage && !immediate) return;

        if (!immediate) {
            if (saveDebounceTimer) clearTimeout(saveDebounceTimer);
            saveDebounceTimer = setTimeout(() => {
                performSave(pageNumber);
            }, 1500);
        } else {
            if (saveDebounceTimer) {
                clearTimeout(saveDebounceTimer);
                saveDebounceTimer = null;
            }
            performSave(pageNumber);
        }
    }

    function performSave(pageNumber) {
        lastSavedPage = pageNumber;
        fetch('/api/reading-history/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({
                book_id: bookId,
                page_number: pageNumber,
                total_pages: totalPages
            })
        }).catch(err => {
            console.error('Failed to save reading history:', err);
        });
    }

    // =========================================================================
    // 3. Page Counter Indicator Formatter
    // =========================================================================
    function updatePageIndicator(pageIndex) {
        if (!pageIndicator) return;
        currentPageIndex = pageIndex;
        
        const isLandscape = pageFlipInstance ? (pageFlipInstance.getOrientation() === 'landscape') : (window.innerWidth >= 768);

        if (isLandscape) {
            const leftPage = pageIndex + 1;
            const rightPage = Math.min(pageIndex + 2, totalPages);
            if (leftPage >= totalPages) {
                pageIndicator.textContent = `Page ${totalPages} of ${totalPages} · The End 💛`;
            } else {
                pageIndicator.textContent = `Pages ${leftPage} - ${rightPage} of ${totalPages}`;
            }
        } else {
            const curPage = Math.min(pageIndex + 1, totalPages);
            pageIndicator.textContent = `Page ${curPage} of ${totalPages}`;
        }
    }

    // =========================================================================
    // 4. Preload & Hardware Decode Upcoming Spread Images
    // =========================================================================
    function prepareUpcomingPages(currentIndex) {
        if (!bookElement) return;
        const pages = bookElement.querySelectorAll('.page');
        if (!pages || pages.length === 0) return;

        const targets = [
            currentIndex, currentIndex + 1,
            currentIndex + 2, currentIndex + 3,
            currentIndex + 4, currentIndex + 5,
            currentIndex - 2, currentIndex - 1
        ];

        targets.forEach(idx => {
            if (idx >= 0 && idx < pages.length) {
                const img = pages[idx].querySelector('.story-scene-img');
                if (img && typeof img.decode === 'function') {
                    img.decode().catch(() => {});
                }
            }
        });
    }

    function preloadAndDecodeSpreadImages() {
        const imgs = document.querySelectorAll('.story-scene-img, .closed-cover-artwork-img');
        imgs.forEach(img => {
            if (img.src) {
                if (typeof img.decode === 'function') {
                    img.decode().catch(() => {});
                }
                const p = new Image();
                p.src = img.src;
                if (typeof p.decode === 'function') {
                    p.decode().catch(() => {});
                }
            }
        });
    }

    // =========================================================================
    // 5. Initialize StPageFlip Instance
    // =========================================================================
    function initializeFlipBook() {
        if (pageFlipInstance) return pageFlipInstance;
        if (!bookElement || !window.St || !window.St.PageFlip) return null;

        const isMobile = window.innerWidth < 768;
        const targetResumeIndex = initialLastPage > 1 ? Math.min(totalPages - 2, Math.floor((initialLastPage - 1) / 2) * 2) : 0;

        const winW = window.innerWidth;
        const baseW = isMobile ? Math.min(360, Math.max(260, winW - 24)) : 490;
        const baseH = isMobile ? Math.min(540, Math.max(380, Math.floor(baseW * 1.38))) : 640;

        pageFlipInstance = new St.PageFlip(bookElement, {
            width: baseW,
            height: baseH,
            size: 'stretch',
            minWidth: 240,
            maxWidth: 580,
            minHeight: 340,
            maxHeight: 740,
            maxShadowOpacity: 0.45,
            showCover: false, // Two-page spread starts right away with Spread 1 (Pages 1 & 2)
            mobileScrollSupport: false,
            usePortrait: isMobile,
            startPage: targetResumeIndex
        });

        const pages = bookElement.querySelectorAll('.page');
        pageFlipInstance.loadFromHTML(pages);

        // Page flip event handler
        pageFlipInstance.on('flip', function (e) {
            playPageTurnSound();
            updatePageIndicator(e.data);
            
            // Auto-save debounced so database I/O never competes with page turn animations
            const savedPage = e.data + 1;
            saveReadingProgress(savedPage, false);

            // Prepare upcoming page illustrations in advance
            prepareUpcomingPages(e.data);

            // Activate 3D Pop-Out & living character effects for the newly visible spread
            if (window.StorybookAnimator) {
                const spreadNum = Math.floor(e.data / 2) + 1;
                window.StorybookAnimator.onSpreadChange(spreadNum, e.data);
            }
        });

        pageFlipInstance.on('init', function () {
            currentPageIndex = targetResumeIndex;
            updatePageIndicator(targetResumeIndex);
            prepareUpcomingPages(targetResumeIndex);

            // Initialize 3D Pop-Out on the starting spread
            if (window.StorybookAnimator) {
                const spreadNum = Math.floor(targetResumeIndex / 2) + 1;
                window.StorybookAnimator.onSpreadChange(spreadNum, targetResumeIndex);
            }
        });

        // Update indicator on orientation change (portrait vs landscape)
        pageFlipInstance.on('changeOrientation', function () {
            updatePageIndicator(currentPageIndex);
        });

        return pageFlipInstance;
    }

    // =========================================================================
    // 6. Smooth 3D Opening Animation Transition (Opens from Current Position)
    // =========================================================================
    function openStorybook() {
        if (isBookOpen) return;
        isBookOpen = true;

        unlockAudioContext();
        playPageTurnSound();

        // 1. Begin fluid 3D physical book cover opening in place
        closedBookStage.classList.add('book-opening-animation');

        // 2. Seamlessly crossfade to the aligned opened reader as cover swings open
        setTimeout(() => {
            openBookStage.classList.add('active');
            closedBookStage.classList.add('book-closed-fade');

            if (closeBookNavBtn) {
                closeBookNavBtn.style.display = 'inline-flex';
            }
        }, 340);

        // 3. Finalize stages after transition finishes
        setTimeout(() => {
            closedBookStage.style.display = 'none';
            closedBookStage.classList.remove('active');
            updatePageIndicator(currentPageIndex);
            prepareUpcomingPages(currentPageIndex);

            // Activate 3D Pop-Out & living character effects for the opened spread
            if (window.StorybookAnimator) {
                const spreadNum = Math.floor(currentPageIndex / 2) + 1;
                window.StorybookAnimator.onSpreadChange(spreadNum, currentPageIndex);
            }
        }, 650);
    }

    // =========================================================================
    // 7. Smooth Closing Animation (Return to Closed 3D Book State)
    // =========================================================================
    function closeStorybook() {
        if (!isBookOpen) return;
        isBookOpen = false;

        // Pause all 3D living character animations
        if (window.StorybookAnimator) {
            window.StorybookAnimator.pauseAll();
        }

        // Save current progress immediately before closing
        const currentPage = currentPageIndex + 1;
        saveReadingProgress(currentPage, true);

        unlockAudioContext();
        playPageTurnSound();

        if (closeBookNavBtn) {
            closeBookNavBtn.style.display = 'none';
        }

        // Fade out opened reader
        openBookStage.classList.remove('active');

        // Restore closed book in place
        closedBookStage.style.display = 'flex';
        requestAnimationFrame(() => {
            closedBookStage.classList.remove('book-opening-animation', 'book-closed-fade');
            closedBookStage.classList.add('active');
        });

        if (pageIndicator) {
            pageIndicator.textContent = 'Closed Book';
        }
    }

    // Pre-initialize StPageFlip so pages, canvases and layouts are 100% prepared
    initializeFlipBook();

    // Preload & hardware decode spread scene illustrations into browser memory
    preloadAndDecodeSpreadImages();

    // Event listeners for Opening the Book
    if (closedBookTrigger) {
        closedBookTrigger.addEventListener('click', function () {
            unlockAudioContext();
            openStorybook();
        });
        closedBookTrigger.addEventListener('touchstart', unlockAudioContext, { passive: true });
    }
    if (openBookActionBtn) {
        openBookActionBtn.addEventListener('click', function () {
            unlockAudioContext();
            openStorybook();
        });
        openBookActionBtn.addEventListener('touchstart', unlockAudioContext, { passive: true });
    }
    const closedBookObj = document.querySelector('.closed-book-3d-object');
    if (closedBookObj) {
        closedBookObj.addEventListener('click', function () {
            unlockAudioContext();
            openStorybook();
        });
        closedBookObj.addEventListener('touchstart', unlockAudioContext, { passive: true });
    }

    // Event listeners for Closing the Book
    if (closeBookNavBtn) {
        closeBookNavBtn.addEventListener('click', function () {
            unlockAudioContext();
            closeStorybook();
        });
    }
    if (closeBookBottomBtn) {
        closeBookBottomBtn.addEventListener('click', function () {
            unlockAudioContext();
            closeStorybook();
        });
    }

    // Touch and pointer interaction on the book canvas
    if (bookElement) {
        bookElement.addEventListener('touchstart', unlockAudioContext, { passive: true });
        bookElement.addEventListener('pointerdown', unlockAudioContext, { passive: true });
    }

    // Previous and Next Button Controls
    if (prevBtn) {
        prevBtn.addEventListener('click', function (e) {
            e.preventDefault();
            unlockAudioContext();
            if (pageFlipInstance) pageFlipInstance.flipPrev();
        });
        prevBtn.addEventListener('touchstart', unlockAudioContext, { passive: true });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', function (e) {
            e.preventDefault();
            unlockAudioContext();
            if (pageFlipInstance) pageFlipInstance.flipNext();
        });
        nextBtn.addEventListener('touchstart', unlockAudioContext, { passive: true });
    }

    // Keyboard Arrow Navigation
    document.addEventListener('keydown', function (e) {
        if (!isBookOpen || !pageFlipInstance) return;
        if (e.key === 'ArrowRight' || e.key === ' ') {
            pageFlipInstance.flipNext();
        } else if (e.key === 'ArrowLeft') {
            pageFlipInstance.flipPrev();
        } else if (e.key === 'Escape') {
            closeStorybook();
        }
    });

    // Save progress on navigating back to bookshelf
    const backBtn = document.getElementById('backToBookshelfBtn');
    if (backBtn) {
        backBtn.addEventListener('click', function () {
            if (isBookOpen && currentPageIndex >= 0) {
                saveReadingProgress(currentPageIndex + 1, true);
            }
        });
    }

    // Save progress on page unload
    window.addEventListener('beforeunload', function () {
        if (isBookOpen && currentPageIndex >= 0) {
            saveReadingProgress(currentPageIndex + 1, true);
        }
    });

    // Reader Settings Modal Controls (Night Sky & Page Turn Whispers)
    const ambientToggle = document.getElementById('ambientToggle');
    const soundToggle = document.getElementById('soundToggle');

    if (ambientToggle) {
        ambientToggle.checked = isNightSkyAtmosphereEnabled();
        ambientToggle.addEventListener('change', function () {
            const enabled = ambientToggle.checked;
            localStorage.setItem('storybook_night_sky', enabled ? 'true' : 'false');
            applyNightSkyAtmosphere();
            try {
                fetch('/api/user/preferences', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ night_sky: enabled })
                }).catch(() => {});
            } catch (e) {}
        });
    }

    if (soundToggle) {
        soundToggle.checked = isPageTurnWhispersEnabled();
        soundToggle.addEventListener('change', function () {
            const enabled = soundToggle.checked;
            localStorage.setItem('storybook_page_turn_whispers', enabled ? 'true' : 'false');
            try {
                fetch('/api/user/preferences', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ page_turn_whispers: enabled })
                }).catch(() => {});
            } catch (e) {}
        });
    }

    // =========================================================================
    // Storybook PDF Download Handler
    // =========================================================================
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const downloadIcon = document.getElementById('downloadIcon');
    const toastEl = document.getElementById('readerNotificationToast');
    const toastMsgEl = document.getElementById('readerToastMessage');
    let toastTimeout = null;

    function showReaderToast(message, duration = 3500) {
        if (!toastEl || !toastMsgEl) return;
        toastMsgEl.textContent = message;
        toastEl.style.display = 'flex';
        toastEl.classList.remove('toast-fade-out');
        if (toastTimeout) clearTimeout(toastTimeout);
        toastTimeout = setTimeout(() => {
            toastEl.classList.add('toast-fade-out');
            setTimeout(() => {
                toastEl.style.display = 'none';
                toastEl.classList.remove('toast-fade-out');
            }, 350);
        }, duration);
    }

    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', async function (e) {
            e.preventDefault();
            unlockAudioContext();

            // Prevent multi-clicks while downloading
            if (downloadPdfBtn.classList.contains('btn-loading')) return;
            downloadPdfBtn.classList.add('btn-loading');
            
            const originalIconClass = downloadIcon ? downloadIcon.className : 'fa-solid fa-arrow-down-to-bracket';
            if (downloadIcon) {
                downloadIcon.className = 'fa-solid fa-spinner fa-spin';
            }
            showReaderToast('Binding your enchanted storybook into a PDF... ✨', 10000);

            try {
                const bookTitle = (readerConfig && readerConfig.dataset.bookTitle) || 'Storybook';
                const defaultFilename = (bookTitle.replace(/[^\w\s-]/g, '').trim().replace(/[-\s]+/g, '_') || 'Storybook') + '.pdf';
                
                const response = await fetch('/api/book/' + bookId + '/pdf');
                if (!response.ok) {
                    throw new Error('Network response was not ok (' + response.status + ')');
                }

                // Check content disposition header for exact filename
                let filename = defaultFilename;
                const disposition = response.headers.get('Content-Disposition');
                if (disposition && disposition.indexOf('filename=') !== -1) {
                    const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                    if (match && match[1]) {
                        filename = match[1].replace(/['"]/g, '').trim();
                    }
                }

                const blob = await response.blob();
                const blobUrl = window.URL.createObjectURL(blob);
                const tempLink = document.createElement('a');
                tempLink.style.display = 'none';
                tempLink.href = blobUrl;
                tempLink.download = filename;
                document.body.appendChild(tempLink);
                tempLink.click();

                setTimeout(() => {
                    window.URL.revokeObjectURL(blobUrl);
                    if (tempLink.parentNode) tempLink.parentNode.removeChild(tempLink);
                }, 2000);

                showReaderToast('Your little story is ready to take home! ✨', 4000);
            } catch (err) {
                console.error('PDF download error:', err);
                showReaderToast('Our scribes encountered a small hiccup. Please try again! ✦', 4000);
            } finally {
                downloadPdfBtn.classList.remove('btn-loading');
                if (downloadIcon) {
                    downloadIcon.className = originalIconClass;
                }
            }
        });
    }
});
