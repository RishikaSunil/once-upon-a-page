/**
 * Once Upon a Page - Subtle Magical Click/Tap Sparkle Effect
 * 
 * Requirements:
 * - Spawns 1 or 2 extremely tiny, delicate four-pointed sparkles at exact click/tap coordinates.
 * - Soft golden and warm-white tones with a quick twinkle animation.
 * - Disappears within 300–400ms (340ms duration).
 * - Fully passive, non-intrusive (pointer-events: none), zero interference with clicks/touches/audio.
 * - Auto-cleans DOM elements immediately upon animation completion.
 */
(function () {
    if (typeof window === 'undefined' || window.__magicSparklesInitialized) return;
    window.__magicSparklesInitialized = true;

    // SVG markup for delicate 4-pointed star sparkle with warm glowing core
    const SPARKLE_SVG = `
        <svg viewBox="0 0 24 24" class="magic-sparkle-svg" aria-hidden="true" focusable="false">
            <path d="M12,0 C12.6,6.8 17.2,11.4 24,12 C17.2,12.6 12.6,17.2 12,24 C11.4,17.2 6.8,12.6 0,12 C6.8,11.4 11.4,6.8 12,0 Z" class="sparkle-star-body"/>
            <circle cx="12" cy="12" r="2.6" class="sparkle-star-core"/>
        </svg>
    `;

    // Maximum concurrent sparkles in DOM to prevent any memory or reflow buildup
    const MAX_CONCURRENT_SPARKLES = 8;
    let activeSparkleCount = 0;

    let lastTapTime = 0;
    let lastTapX = 0;
    let lastTapY = 0;

    function spawnSingleSparkle(x, y, size, delay, isGold) {
        if (activeSparkleCount >= MAX_CONCURRENT_SPARKLES) return;
        activeSparkleCount++;

        const el = document.createElement('div');
        el.className = 'magic-tap-sparkle ' + (isGold ? 'sparkle-gold' : 'sparkle-warm-white');
        el.style.left = x + 'px';
        el.style.top = y + 'px';
        el.style.width = size + 'px';
        el.style.height = size + 'px';
        if (delay > 0) {
            el.style.animationDelay = delay + 'ms';
        }
        el.innerHTML = SPARKLE_SVG;

        function removeSparkle() {
            if (el.parentNode) {
                el.parentNode.removeChild(el);
                activeSparkleCount = Math.max(0, activeSparkleCount - 1);
            }
        }

        el.addEventListener('animationend', removeSparkle, { once: true });
        // Fallback cleanup in case animationend is skipped
        setTimeout(removeSparkle, 420);

        document.body.appendChild(el);
    }

    function createTapSparkles(clientX, clientY) {
        if (!document.body) return;

        // 1. Primary sparkle right at the exact click/tap position (11-13px)
        const primarySize = 11 + Math.random() * 2.5;
        const primaryTone = Math.random() > 0.45; // mix of warm-white and soft gold
        spawnSingleSparkle(clientX, clientY, primarySize, 0, primaryTone);

        // 2. Secondary sparkle (60% chance of second even tinier companion sparkle ~7-9px)
        if (Math.random() < 0.6) {
            const angle = Math.random() * Math.PI * 2;
            const dist = 7 + Math.random() * 8; // 7-15px offset
            const secX = clientX + Math.cos(angle) * dist;
            const secY = clientY + Math.sin(angle) * dist;
            const secondarySize = 7.5 + Math.random() * 2;
            spawnSingleSparkle(secX, secY, secondarySize, 35, !primaryTone);
        }
    }

    function handleInteraction(clientX, clientY) {
        const now = performance.now();
        // Prevent duplicate firing if multiple event types trigger on same tap (pointerdown + click)
        if (now - lastTapTime < 80 && Math.hypot(clientX - lastTapX, clientY - lastTapY) < 18) {
            return;
        }
        lastTapTime = now;
        lastTapX = clientX;
        lastTapY = clientY;

        createTapSparkles(clientX, clientY);
    }

    // Attach passive capture listener so it never stops event propagation or blocks UI actions
    if (window.PointerEvent) {
        window.addEventListener('pointerdown', function (e) {
            if (e.isPrimary === false || (e.button !== undefined && e.button !== 0)) return;
            handleInteraction(e.clientX, e.clientY);
        }, { passive: true, capture: true });
    } else {
        let isTouch = false;
        window.addEventListener('touchstart', function (e) {
            isTouch = true;
            if (e.touches && e.touches.length > 0) {
                handleInteraction(e.touches[0].clientX, e.touches[0].clientY);
            }
        }, { passive: true, capture: true });

        window.addEventListener('mousedown', function (e) {
            if (isTouch) { isTouch = false; return; }
            if (e.button !== 0) return;
            handleInteraction(e.clientX, e.clientY);
        }, { passive: true, capture: true });
    }
})();
