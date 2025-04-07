document.addEventListener('DOMContentLoaded', function () {
    // Extra numeric-only validation for math pages
    const numericPages = [4,6,8,28,34,40];
    const pageNumber = Number(document.body.dataset.page || 0);

    if (numericPages.includes(pageNumber)) {
        const answerInput = document.getElementById("answerInput");
        if (answerInput) {
            answerInput.addEventListener("input", function () {
                this.value = this.value.replace(/[^0-9]/g, "");
            });
        }
    }

    const form = document.getElementById('taskForm');
    const countdown = document.getElementById('countdown');
    const progressBar = document.getElementById('progress-bar');

    // ------------------------------------------
    // ⏲️ Timed Tasks: Countdown + Progress Bar
    // ------------------------------------------
    if (countdown && progressBar) {
        let secondsLeft = parseFloat(countdown.textContent);
        const totalTime = secondsLeft;

        const timerInterval = setInterval(() => {
            secondsLeft -= 0.05;

            if (secondsLeft <= 0) {
                countdown.textContent = '0.0';
                progressBar.style.width = '0%';
                clearInterval(timerInterval);
                if (form) form.submit();
            } else {
                countdown.textContent = secondsLeft.toFixed(1);
                const progress = (secondsLeft / totalTime) * 100;
                progressBar.style.width = `${progress}%`;
            }
        }, 100);
    }
    
    
    

    // ------------------------------------------
// 🎯 Letter Grid Task Logic
if (document.querySelector('.grid-btn')) {
    const gridForm = document.querySelector('form');
    const currentPage = Number(document.body.dataset.page);

    // Global 30-second timer (persisted across reloads)
    const keyExpire = `grid_expire_time_${currentPage}`;
    const keyCount = `grid_letter_count_${currentPage}`;
    const now = Date.now();

    let expireTime = sessionStorage.getItem(keyExpire);
    let letterCount = parseInt(sessionStorage.getItem(keyCount) || "0");

    if (!expireTime) {
        expireTime = now + 15000;
        sessionStorage.setItem(keyExpire, expireTime);
        sessionStorage.setItem(keyCount, "0");
    } else {
        expireTime = parseInt(expireTime);
    }

    // Timer
    const interval = setInterval(() => {
        const timeLeft = expireTime - Date.now();
        if (timeLeft <= 0) {
            clearInterval(interval);
            sessionStorage.removeItem(keyExpire);
            document.getElementById("letter_count").value = letterCount;
            gridForm.submit();
        }
    }, 100);

    // Click detection
    const gridButtons = document.querySelectorAll('.grid-btn');
    const targetElem = document.querySelector("p strong");
    if (targetElem) {
        const targetLetter = targetElem.textContent;
        gridButtons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                if (btn.textContent === targetLetter) {
                    letterCount++;
                    sessionStorage.setItem(keyCount, letterCount.toString());
                    window.location.reload();
                }
            });
        });
    }
}


    // ------------------------------------------
    // 🪜 Ladder Selection
    const ladderContainer = document.getElementById("ladderContainer");
    if (ladderContainer) {
        const rungs = ladderContainer.getElementsByClassName("rung");
        const hiddenInput = document.getElementById("ladder_value");
        const nextBtn = document.getElementById("nextBtn");

        Array.from(rungs).forEach(function (rung) {
            rung.addEventListener("click", function () {
                Array.from(rungs).forEach(el => el.classList.remove("selected"));
                rung.classList.add("selected");
                hiddenInput.value = rung.getAttribute("data-value");
                nextBtn.disabled = false;
            });
        });

        // 🪜 Position rungs from top (10) to bottom (1)
        const totalSteps = rungs.length;
        Array.from(rungs).forEach((rung, index) => {
            rung.style.top = `${(index * (100 / totalSteps))}%`;
        });
    }


    // ------------------------------------------
    // ⏱️ Task Time Capture
    // ------------------------------------------
    if (form) {
        const startTime = performance.now();

        form.addEventListener('submit', function () {
            const endTime = performance.now();
            const duration = ((endTime - startTime) / 1000).toFixed(3);
            const input = form.querySelector('.task-time');
            if (input) input.value = duration;
        });
    }

// === STEP 1: Redirect to Page 24 if "Do you have any parental figures?" = No ===
const hasParentRadios = document.querySelectorAll('input[name="has_parent"]');
if (hasParentRadios.length > 0) {
    hasParentRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.value === "No") {
                window.location.href = "/page/24";  // Redirect if no parental figure
            }
        });
    });
}

// === STEP 2: Dynamic show/hide for data-show-if ===
function evaluateShowIfConditions() {
    const tasks = document.querySelectorAll('.task[data-show-if]');
    const form = document.getElementById('demographicsForm');
    if (!form) return;
    const formData = new FormData(form);

    tasks.forEach(task => {
        const conditionStr = task.dataset.showIf;
        if (!conditionStr) {
            task.style.display = '';  // Show by default
            return;
        }

        let condition = {};
        try {
            condition = JSON.parse(conditionStr);
        } catch (e) {
            console.warn("Invalid show_if condition:", conditionStr);
        }

        let shouldShow = true;
        for (const key in condition) {
            const expectedValue = condition[key];
            const actualValue = formData.get(key);
            if (actualValue !== expectedValue) {
                shouldShow = false;
                break;
            }
        }

        
    task.style.display = shouldShow ? '' : 'none';
    const inputs = task.querySelectorAll('input, select, textarea');
    inputs.forEach(input => input.disabled = !shouldShow);
    
    });
}

const demographicForm = document.getElementById('demographicsForm');
if (demographicForm) {
    demographicForm.addEventListener('input', evaluateShowIfConditions);
    demographicForm.addEventListener('change', evaluateShowIfConditions);
    evaluateShowIfConditions();  // Run on load
}

});

/**
 * For continuous scale pages:
 * Update the displayed value next to the slider.
 */
function updateRangeValue(val) {
    var rangeValElem = document.getElementById("range_val");
    if (rangeValElem) {
        rangeValElem.textContent = val;
    }
}