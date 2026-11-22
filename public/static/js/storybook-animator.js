/**
 * Once Upon a Page - Universal 3D Pop-Out & Living Storybook Animator Engine
 * 
 * Features:
 * 1. 3D Pop-Out Depth Stage: Layered depth planes (scenery at Z:0, atmosphere at Z:14px,
 *    characters/focal features at Z:28px, overlays at Z:38px, paper rim & sheen at Z:44px).
 * 2. Interactive & Idle 3D Tilt Parallax: Gentle cursor-following perspective on desktop
 *    and organic breathing 3D depth on mobile/idle.
 * 3. Semantic Living Character Effects: Automatically identifies scene characters and objects
 *    (stars, fairies, animals, birds, nature/trees, clouds, moon, children, fireflies, water)
 *    and applies gentle, child-friendly, non-random living animations.
 * 4. Transparent Overlay Layer Support: Seamlessly renders transparent PNG character cutouts
 *    as distinct floating 3D pop-out layers.
 * 5. Lifecycle Management: Activates animations only for the currently visible spread and
 *    pauses inactive spreads (.scene-paused), guaranteeing zero wasted background processing.
 * 6. Accessibility: Full compliance with prefers-reduced-motion.
 */

(function (window, document) {
    'use strict';

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const StorybookAnimator = {
        initialized: false,
        activeSpreadNumber: 1,

        init: function () {
            if (this.initialized) return;
            this.initialized = true;

            if (prefersReducedMotion) {
                document.body.classList.add('reduced-motion-active');
            }

            this.enhanceAllIllustrations();
            this.attachGlobalInteractions();
        },

        /**
         * Enhances all illustration frames in the document with 3D pop-out stages
         */
        enhanceAllIllustrations: function () {
            const frames = document.querySelectorAll('.story-illustration-frame');
            frames.forEach((frame, index) => {
                const spreadNum = parseInt(frame.getAttribute('data-spread') || (index + 1), 10);
                this.decorateSpreadIllustration(frame, spreadNum);
            });
        },

        /**
         * Converts a flat illustration frame into a living 3D Pop-Out stage
         */
        decorateSpreadIllustration: function (frame, spreadNum) {
            if (frame.classList.contains('popout-enhanced')) return;

            const baseImg = frame.querySelector('.story-scene-img');
            if (!baseImg) return;

            // Extract context metadata for universal semantic character detection
            const bookTitle = (frame.getAttribute('data-book-title') || 
                               document.querySelector('#readerConfig')?.dataset?.bookTitle || 
                               document.title || '').toLowerCase();
            const chapterTitle = (frame.getAttribute('data-title') || 
                                  frame.closest('.page')?.nextElementSibling?.querySelector('.story-chapter-title')?.textContent || '').toLowerCase();
            const proseEl = frame.closest('.page')?.nextElementSibling?.querySelector('.story-prose-container');
            const storyText = (proseEl ? proseEl.textContent : '').toLowerCase();
            const overlaySrc = frame.getAttribute('data-character-overlay') || null;

            // Mark enhanced
            frame.classList.add('popout-enhanced', 'scene-paused');

            // 1. Construct 3D Pop-Out Viewport and Depth Layers
            const viewport = document.createElement('div');
            viewport.className = 'popout-scene-viewport';

            // Layer 1: Scenery / Background Plane (Z: 0px)
            const layerScenery = document.createElement('div');
            layerScenery.className = 'popout-depth-layer popout-layer-scenery';
            
            // Move original image inside scenery layer
            baseImg.parentNode.insertBefore(viewport, baseImg);
            layerScenery.appendChild(baseImg);

            const vignette = document.createElement('div');
            vignette.className = 'popout-scenery-vignette';
            layerScenery.appendChild(vignette);
            viewport.appendChild(layerScenery);

            // Layer 2: Atmosphere & Ambient Particles (Z: 14px)
            const layerAtmosphere = document.createElement('div');
            layerAtmosphere.className = 'popout-depth-layer popout-layer-atmosphere';
            viewport.appendChild(layerAtmosphere);

            // Layer 3: Living Characters & Focal Features (Z: 28px) - 3D POP-OUT
            const layerCharacter = document.createElement('div');
            layerCharacter.className = 'popout-depth-layer popout-layer-character';
            viewport.appendChild(layerCharacter);

            // Layer 4: Optional Transparent Pop-Out Character Overlay (Z: 38px)
            if (overlaySrc) {
                const layerOverlay = document.createElement('div');
                layerOverlay.className = 'popout-depth-layer popout-layer-overlay';
                const overlayImg = document.createElement('img');
                overlayImg.src = overlaySrc;
                overlayImg.alt = "Pop-out Character";
                overlayImg.className = 'popout-overlay-character-img';
                layerOverlay.appendChild(overlayImg);
                viewport.appendChild(layerOverlay);
            }

            // Layer 5: Paper Edge Rim & Directional Light Sheen (Z: 44px)
            const layerSheen = document.createElement('div');
            layerSheen.className = 'popout-depth-layer popout-layer-sheen';
            viewport.appendChild(layerSheen);

            frame.appendChild(viewport);

            // 2. Identify and Inject Living Character Effects
            const themes = this.detectSceneThemes(spreadNum, bookTitle, chapterTitle, storyText);
            this.injectLivingEffects(layerAtmosphere, layerCharacter, themes, spreadNum, bookTitle);

            // 3. Attach Interactive 3D Mouse Parallax Tilt
            this.attachParallaxTilt(frame, viewport);
        },

        /**
         * Universal Semantic Scene Archetype Classifier
         * Evaluates story text, chapter titles and book themes
         */
        detectSceneThemes: function (spreadNum, bookTitle, chapterTitle, storyText) {
            const combined = `${bookTitle} ${chapterTitle} ${storyText}`;
            const themes = new Set();

            // Stars & Night Sky
            if (/star|twinkle|starlight|constellation|brightest|night sky|sparkling night/.test(combined)) {
                themes.add('stars');
            }

            // Fairies & Magic
            if (/fairy|pixie|wings|magic wand|fairytale|enchanted dust|spell/.test(combined)) {
                themes.add('fairy');
            }

            // Fireflies & Tiny Bugs
            if (/firefly|fireflies|tiny bug|beetle|caterpillar|glow|lantern|little light|darkness|afraid of the dark/.test(combined)) {
                themes.add('firefly');
            }

            // Animals (Bears, Bunnies, Squirrels, Dogs, Pets)
            if (/bear|benny|bunny|rabbit|teddy|squirrel|fox|dog|cat|wolf|cub|cuddled|burrow|sleepy/.test(combined)) {
                themes.add('animal');
            }

            // Birds
            if (/bird|birds|owl|sparrow|feather|nest|flying|wings|hen|rooster/.test(combined)) {
                themes.add('bird');
            }

            // Nature, Trees & Flowers
            if (/flower|flowers|garden|tree|trees|willow|forest|blossom|leaves|branches|picnic|woods|canopy/.test(combined)) {
                themes.add('nature');
            }

            // Clouds & Daytime Sky
            if (/cloud|clouds|sunny|morning|breeze|sky|daytime|wind/.test(combined)) {
                themes.add('cloud');
            }

            // Moon
            if (/moon|moonlight|crescent|lunar/.test(combined)) {
                themes.add('moon');
            }

            // Children
            if (/girl|boy|child|children|mia|kid|friend|smile|crying|window|bedroom|bedtime/.test(combined)) {
                themes.add('child');
            }

            // Water & Aquatic
            if (/fish|water|river|lake|sea|ocean|pond|swimming|stream/.test(combined)) {
                themes.add('water');
            }

            // If empty, fall back to universal storybook ambient magic
            if (themes.size === 0) {
                themes.add('default');
            }

            return themes;
        },

        /**
         * Injects appropriate, gentle living animations into the atmosphere and character layers
         */
        injectLivingEffects: function (layerAtmosphere, layerCharacter, themes, spreadNum, bookTitle) {
            // Is this the flagship Twinkle book?
            const isTwinkle = bookTitle.includes('twinkle');
            const isFairyBug = bookTitle.includes('fairy') || bookTitle.includes('bug');
            const isPicnic = bookTitle.includes('picnic');

            // --- 1. STARS & CELESTIAL ---
            if (themes.has('stars')) {
                // Ambient twinkling stars floating at Z:14px
                for (let i = 0; i < 5; i++) {
                    const star = document.createElement('span');
                    star.className = 'living-ambient-star';
                    star.textContent = ['✦', '✧', '⋆', '✨'][i % 4];
                    star.style.left = `${12 + (i * 18) + (Math.random() * 8)}%`;
                    star.style.top = `${10 + (i * 12) + (Math.random() * 10)}%`;
                    star.style.animationDelay = `${(i * 0.7).toFixed(1)}s`;
                    star.style.animationDuration = `${(2.8 + Math.random() * 1.5).toFixed(1)}s`;
                    layerAtmosphere.appendChild(star);
                }

                // Focal Twinkle Star Center Glow at Z:28px
                const starGlow = document.createElement('div');
                starGlow.className = 'living-star-glow';
                
                // Position tuning for Twinkle or universal scenes
                if (isTwinkle && spreadNum === 4) {
                    starGlow.style.cssText = 'width: 110px; height: 110px; top: 22%; left: 66%; transform: translate(-50%, -50%);';
                } else if (isTwinkle && spreadNum === 7) {
                    starGlow.style.cssText = 'width: 120px; height: 120px; top: 32%; left: 52%; transform: translate(-50%, -50%);';
                } else {
                    starGlow.style.cssText = 'width: 135px; height: 135px; top: 30%; left: 50%; transform: translate(-50%, -50%);';
                }
                layerCharacter.appendChild(starGlow);

                // Sparkling Star Eye Glint
                const glint = document.createElement('div');
                glint.className = 'living-glint-flash';
                if (isTwinkle && spreadNum === 4) {
                    glint.style.cssText = 'top: 19%; left: 68%;';
                } else {
                    glint.style.cssText = 'top: 27%; left: 53%;';
                }
                layerCharacter.appendChild(glint);

                // Radiating Light Beam for Courage / Chapter 6
                if (isTwinkle && spreadNum === 6) {
                    const beam = document.createElement('div');
                    beam.className = 'living-light-beam';
                    beam.style.cssText = 'top: 18%; left: 45%;';
                    layerCharacter.appendChild(beam);
                }
            }

            // --- 2. FAIRIES ---
            if (themes.has('fairy')) {
                // Translucent Fluttering Gossamer Wings (Z:28px)
                const wings = document.createElement('div');
                wings.className = 'living-fairy-wings';
                if (isFairyBug && spreadNum >= 5) {
                    wings.style.cssText = 'top: 32%; left: 45%; transform: translate(-50%, -50%);';
                } else {
                    wings.style.cssText = 'top: 36%; left: 48%; transform: translate(-50%, -50%);';
                }
                layerCharacter.appendChild(wings);

                // Gentle Fairy Dust Sparkles (Z:14px)
                for (let i = 0; i < 4; i++) {
                    const dust = document.createElement('span');
                    dust.className = 'living-fairy-dust';
                    dust.textContent = ['✨', '✦', '⋆'][i % 3];
                    dust.style.left = `${38 + (i * 8)}%`;
                    dust.style.top = `${32 + (i * 10)}%`;
                    dust.style.animationDelay = `${(i * 0.8).toFixed(1)}s`;
                    layerAtmosphere.appendChild(dust);
                }

                // Ethereal Fairy Luminescence Aura
                const fairyAura = document.createElement('div');
                fairyAura.className = 'living-fairy-aura';
                fairyAura.style.cssText = 'width: 140px; height: 140px; top: 35%; left: 46%; transform: translate(-50%, -50%);';
                layerCharacter.appendChild(fairyAura);
            }

            // --- 3. FIREFLIES & GLOWING BUGS ---
            if (themes.has('firefly')) {
                // Drifting Hovering Firefly Orbs (Z:14px)
                const fireflyCount = (isFairyBug || themes.has('nature')) ? 4 : 3;
                for (let i = 0; i < fireflyCount; i++) {
                    const fly = document.createElement('div');
                    fly.className = 'living-firefly-orb';
                    fly.style.left = `${20 + (i * 22) + (Math.random() * 6)}%`;
                    fly.style.top = `${28 + (i * 14) + (Math.random() * 8)}%`;
                    fly.style.animationDelay = `${(i * 1.1).toFixed(1)}s`;
                    fly.style.animationDuration = `${(3.5 + Math.random() * 2).toFixed(1)}s`;
                    layerAtmosphere.appendChild(fly);
                }

                // Warm Pulsing Bug / Lantern Abdomen Glow (Z:28px)
                const bugGlow = document.createElement('div');
                bugGlow.className = 'living-bug-glow';
                if (isFairyBug && spreadNum === 1) {
                    bugGlow.style.cssText = 'width: 90px; height: 90px; bottom: 32%; left: 52%; transform: translate(-50%, -50%);';
                } else if (isFairyBug && spreadNum === 2) {
                    bugGlow.style.cssText = 'width: 80px; height: 80px; bottom: 26%; left: 44%; transform: translate(-50%, -50%);';
                } else {
                    bugGlow.style.cssText = 'width: 95px; height: 95px; bottom: 35%; left: 50%; transform: translate(-50%, -50%);';
                }
                layerCharacter.appendChild(bugGlow);
            }

            // --- 4. ANIMALS (BEARS, BUNNIES, SQUIRRELS) ---
            if (themes.has('animal')) {
                // Soft Rhythmic Chest Breathing Rise and Fall (Z:28px)
                const animalBreathe = document.createElement('div');
                animalBreathe.className = 'living-animal-breathe';
                if (isPicnic && spreadNum === 2) { // Benny the Bear
                    animalBreathe.style.cssText = 'width: 170px; height: 130px; top: 48%; left: 52%; transform: translate(-50%, -50%);';
                } else if (isTwinkle && spreadNum === 4) { // Teddy bear
                    animalBreathe.style.cssText = 'width: 100px; height: 100px; bottom: 20%; right: 28%; transform: translate(-50%, -50%);';
                } else {
                    animalBreathe.style.cssText = 'width: 130px; height: 110px; bottom: 30%; left: 45%; transform: translate(-50%, -50%);';
                }
                layerCharacter.appendChild(animalBreathe);

                // Subtle Occasional Ear Twitch Accent
                const earTwitch = document.createElement('div');
                earTwitch.className = 'living-ear-twitch';
                if (isPicnic && spreadNum === 2) {
                    earTwitch.style.cssText = 'top: 38%; left: 42%;';
                } else {
                    earTwitch.style.cssText = 'top: 35%; left: 46%;';
                }
                layerCharacter.appendChild(earTwitch);

                // Cozy Snuggle Aura
                const snuggle = document.createElement('div');
                snuggle.className = 'living-cozy-snuggle';
                snuggle.style.cssText = 'width: 180px; height: 140px; bottom: 25%; left: 48%; transform: translate(-50%, -50%);';
                layerCharacter.appendChild(snuggle);
            }

            // --- 5. BIRDS ---
            if (themes.has('bird')) {
                const birdWing = document.createElement('div');
                birdWing.className = 'living-bird-wing';
                birdWing.style.cssText = 'top: 32%; left: 45%;';
                layerCharacter.appendChild(birdWing);
            }

            // --- 6. NATURE & TREES & FLOWERS ---
            if (themes.has('nature')) {
                // Gentle Nature Breeze Sway (Z:14px)
                const natureSway = document.createElement('div');
                natureSway.className = 'living-nature-sway';
                layerAtmosphere.appendChild(natureSway);

                // Floating Pollen & Blossom Spores (Z:14px)
                for (let i = 0; i < 4; i++) {
                    const pollen = document.createElement('div');
                    pollen.className = 'living-pollen-spore';
                    pollen.style.left = `${15 + (i * 24)}%`;
                    pollen.style.top = `${40 + (i * 12)}%`;
                    pollen.style.animationDelay = `${(i * 1.2).toFixed(1)}s`;
                    layerAtmosphere.appendChild(pollen);
                }
            }

            // --- 7. CLOUDS & SKY ---
            if (themes.has('cloud')) {
                const cloudMist = document.createElement('div');
                cloudMist.className = 'living-cloud-mist';
                cloudMist.style.cssText = 'width: 45%; top: 12%; left: 25%;';
                layerAtmosphere.appendChild(cloudMist);
            }

            // --- 8. MOON ---
            if (themes.has('moon')) {
                const moonGlow = document.createElement('div');
                moonGlow.className = 'living-moon-glow';
                if (isTwinkle && spreadNum === 7) {
                    moonGlow.style.cssText = 'width: 110px; height: 110px; top: 10%; right: 10%; transform: translate(-50%, -50%);';
                } else {
                    moonGlow.style.cssText = 'width: 100px; height: 100px; top: 14%; right: 15%; transform: translate(-50%, -50%);';
                }
                layerAtmosphere.appendChild(moonGlow);
            }

            // --- 9. CHILDREN ---
            if (themes.has('child')) {
                // Warm Window / Room Candle Glow (Z:28px)
                const childGlow = document.createElement('div');
                childGlow.className = 'living-child-glow';
                if (isTwinkle && (spreadNum === 4 || spreadNum === 7)) {
                    childGlow.style.cssText = 'width: 145px; height: 145px; bottom: 20%; left: 26%; transform: translate(-50%, -50%);';
                } else if (isPicnic) {
                    childGlow.style.cssText = 'width: 120px; height: 120px; top: 40%; left: 35%; transform: translate(-50%, -50%);';
                } else {
                    childGlow.style.cssText = 'width: 130px; height: 130px; bottom: 25%; left: 32%; transform: translate(-50%, -50%);';
                }
                layerCharacter.appendChild(childGlow);

                // Natural Eye Twinkle
                const twinkle = document.createElement('div');
                twinkle.className = 'living-child-twinkle';
                if (isTwinkle && spreadNum === 4) {
                    twinkle.style.cssText = 'top: 61%; left: 27%;';
                } else {
                    twinkle.style.cssText = 'top: 45%; left: 34%;';
                }
                layerCharacter.appendChild(twinkle);
            }

            // --- 10. WATER & FISH ---
            if (themes.has('water')) {
                const caustic = document.createElement('div');
                caustic.className = 'living-water-caustic';
                layerAtmosphere.appendChild(caustic);

                for (let i = 0; i < 4; i++) {
                    const bubble = document.createElement('div');
                    bubble.className = 'living-water-bubble';
                    bubble.style.cssText = `width: ${6 + i * 2}px; height: ${6 + i * 2}px; left: ${25 + i * 18}%; bottom: 15%; animation-delay: ${(i * 0.9).toFixed(1)}s;`;
                    layerAtmosphere.appendChild(bubble);
                }
            }

            // --- 11. DEFAULT UNIVERSAL STORYBOOK MAGIC ---
            if (themes.has('default')) {
                for (let i = 0; i < 4; i++) {
                    const star = document.createElement('span');
                    star.className = 'living-ambient-star';
                    star.textContent = ['✦', '✨', '⋆'][i % 3];
                    star.style.left = `${15 + (i * 22)}%`;
                    star.style.top = `${15 + (i * 16)}%`;
                    star.style.animationDelay = `${(i * 0.9).toFixed(1)}s`;
                    layerAtmosphere.appendChild(star);
                }
                const ambientGlow = document.createElement('div');
                ambientGlow.className = 'living-star-glow';
                ambientGlow.style.cssText = 'width: 120px; height: 120px; top: 40%; left: 50%; transform: translate(-50%, -50%);';
                layerCharacter.appendChild(ambientGlow);
            }
        },

        /**
         * Attaches natural 3D Perspective Parallax Tilt on Cursor Move
         */
        attachParallaxTilt: function (frame, viewport) {
            if (prefersReducedMotion) return;

            let isHovered = false;

            frame.addEventListener('mouseenter', () => {
                isHovered = true;
            });

            frame.addEventListener('mousemove', (e) => {
                if (!isHovered) return;
                const rect = frame.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) return;

                // Normalized mouse coordinates from center (-0.5 to 0.5)
                const nx = (e.clientX - rect.left) / rect.width - 0.5;
                const ny = (e.clientY - rect.top) / rect.height - 0.5;

                // Subtle, natural tilt angles (max 6-8 degrees)
                const rotX = (ny * -10).toFixed(2);
                const rotY = (nx * 12).toFixed(2);

                viewport.style.setProperty('--rx', `${rotX}deg`);
                viewport.style.setProperty('--ry', `${rotY}deg`);

                // Directional light sheen reflection follows the light source
                const sheenX = ((nx + 0.5) * 100).toFixed(1);
                const sheenY = ((ny + 0.5) * 100).toFixed(1);
                viewport.style.setProperty('--sheen-x', `${sheenX}%`);
                viewport.style.setProperty('--sheen-y', `${sheenY}%`);
            });

            frame.addEventListener('mouseleave', () => {
                isHovered = false;
                // Smoothly reset tilt back to neutral
                viewport.style.setProperty('--rx', '0deg');
                viewport.style.setProperty('--ry', '0deg');
            });
        },

        /**
         * Page Turn Integration:
         * Activates 3D and living effects on the visible spread and pauses inactive spreads
         */
        onSpreadChange: function (activeSpreadNum, pageIndex) {
            this.activeSpreadNumber = activeSpreadNum;
            const frames = document.querySelectorAll('.story-illustration-frame');

            frames.forEach((frame) => {
                const frameSpread = parseInt(frame.getAttribute('data-spread') || '1', 10);
                if (frameSpread === activeSpreadNum) {
                    // Activate newly visible spread
                    frame.classList.remove('scene-paused');
                    const viewport = frame.querySelector('.popout-scene-viewport');
                    if (viewport) {
                        viewport.style.setProperty('--rx', '0deg');
                        viewport.style.setProperty('--ry', '0deg');
                    }
                } else {
                    // Suspend inactive spread to eliminate 100% background processing
                    frame.classList.add('scene-paused');
                }
            });
        },

        /**
         * Pauses all animations across all spreads (e.g. when book is closed)
         */
        pauseAll: function () {
            const frames = document.querySelectorAll('.story-illustration-frame');
            frames.forEach(frame => frame.classList.add('scene-paused'));
        },

        /**
         * Resumes animations for the active spread
         */
        resumeActive: function () {
            this.onSpreadChange(this.activeSpreadNumber, (this.activeSpreadNumber - 1) * 2);
        },

        /**
         * Interactive click magic bursts on illustration frame taps
         */
        triggerMagicBurst: function (x, y, container) {
            if (prefersReducedMotion) return;
            const burst = document.createElement('div');
            burst.className = 'interactive-magic-burst';
            burst.style.left = `${x}px`;
            burst.style.top = `${y}px`;

            for (let i = 0; i < 8; i++) {
                const particle = document.createElement('span');
                particle.className = 'burst-particle';
                particle.textContent = ['✨', '⭐', '✦', '💛', '🌸'][i % 5];
                const angle = (i / 8) * (Math.PI * 2);
                const distance = 35 + Math.random() * 25;
                const px = Math.cos(angle) * distance;
                const py = Math.sin(angle) * distance;

                particle.style.setProperty('--dx', `${px}px`);
                particle.style.setProperty('--dy', `${py}px`);
                burst.appendChild(particle);
            }

            container.appendChild(burst);
            setTimeout(() => {
                if (burst.parentNode) burst.parentNode.removeChild(burst);
            }, 850);
        },

        attachGlobalInteractions: function () {
            // Listen for taps / clicks on illustration frames to trigger friendly magic bursts
            document.addEventListener('click', (e) => {
                const frame = e.target.closest('.story-illustration-frame');
                if (frame) {
                    const rect = frame.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;
                    this.triggerMagicBurst(x, y, frame);
                }
            });
        }
    };

    window.StorybookAnimator = StorybookAnimator;

    document.addEventListener('DOMContentLoaded', function () {
        StorybookAnimator.init();
    });

})(window, document);
