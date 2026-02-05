/**
 * 1v1 Competitive Programming Interface - Core Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initSplitPane();
    initVerticalSplitPane();
    initTabs();
    initCopyAction();
    initTimer();
    initEditor();
    console.log('1v1 Interface Ready');
});

/**
 * 1. Horizontal Split Pane (Left vs Right)
 */
function initSplitPane() {
    const leftPane = document.getElementById('leftPane');
    const handle = document.getElementById('dragHandle');
    const workspace = document.querySelector('.workspace');

    let isResizing = false;

    handle.addEventListener('mousedown', () => {
        isResizing = true;
        handle.classList.add('resizing');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        const containerRect = workspace.getBoundingClientRect();
        const pointerX = e.clientX - containerRect.left;
        const minWidth = 300;
        const maxWidth = containerRect.width - 300;

        if (pointerX > minWidth && pointerX < maxWidth) {
            const widthPercent = (pointerX / containerRect.width) * 100;
            leftPane.style.width = widthPercent + '%';
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            handle.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}

/**
 * 2. Vertical Split Pane (Editor vs TestPanel)
 */
function initVerticalSplitPane() {
    const editorSection = document.getElementById('editorSection');
    const handle = document.getElementById('dragHandleVertical');
    const rightPane = document.getElementById('rightPane');

    let isResizing = false;

    handle.addEventListener('mousedown', () => {
        isResizing = true;
        handle.classList.add('resizing');
        document.body.style.cursor = 'row-resize';
        document.body.style.userSelect = 'none';
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        const containerRect = rightPane.getBoundingClientRect();
        const pointerY = e.clientY - containerRect.top;

        const minHeight = 100;
        const maxHeight = containerRect.height - 100;

        if (pointerY > minHeight && pointerY < maxHeight) {
            // Set height in px preferred for vertical resizing
            editorSection.style.height = pointerY + 'px';
        }
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            handle.classList.remove('resizing');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}

/**
 * 3. Tab Switching Logic
 */
function initTabs() {
    // Problem Pane Tabs
    const problemTabs = document.querySelectorAll('.problem-tabs .tab-btn');
    problemTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            if (tab.disabled) return;
            // Toggle active state
            tab.parentElement.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Toggle Content
            const target = tab.getAttribute('data-tab');
            document.getElementById('desc').classList.add('hidden');
            document.getElementById('submissions').classList.add('hidden');

            document.getElementById(target).classList.remove('hidden');
        });
    });

    // Test Case Tabs
    const tcTabs = document.querySelectorAll('.tc-tab');
    tcTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tcTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const target = tab.getAttribute('data-target');
            document.querySelectorAll('.tc-view').forEach(v => v.classList.add('hidden'));
            document.getElementById(target).classList.remove('hidden');
            document.getElementById(target).classList.add('active');
        });
    });
}

/**
 * 4. Copy Functionality (Precise)
 */
function initCopyAction() {
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const block = btn.closest('.io-block');
            const content = block.querySelector('.io-content').innerText;

            try {
                await navigator.clipboard.writeText(content);
                const originalText = btn.innerText;
                btn.innerText = 'Copied!';
                btn.style.color = 'var(--accent-green)';
                setTimeout(() => {
                    btn.innerText = originalText;
                    btn.style.color = '';
                }, 1500);
            } catch (err) {
                console.error('Copy failed', err);
            }
        });
    });
}

/**
 * 5. Simple Editor Line Numbers
 */
function initEditor() {
    const editor = document.getElementById('codeEditor');
    const lineNumbers = document.getElementById('lineNumbers');

    const updateLineNumbers = () => {
        const lines = editor.value.split('\n').length;
        lineNumbers.innerHTML = Array(lines).fill(0).map((_, i) => `<span>${i + 1}</span>`).join('');
    };

    editor.addEventListener('input', updateLineNumbers);
    editor.addEventListener('scroll', () => {
        lineNumbers.scrollTop = editor.scrollTop;
    });

    // Tab support
    editor.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = editor.selectionStart;
            const end = editor.selectionEnd;
            editor.value = editor.value.substring(0, start) + "    " + editor.value.substring(end);
            editor.selectionStart = editor.selectionEnd = start + 4;
        }
    });

    updateLineNumbers();
}

/**
 * 6. Timer
 */
function initTimer() {
    const timerEl = document.getElementById('timer');
    let totalSeconds = 0 * 3600 + 15 * 60 + 0;

    setInterval(() => {
        if (totalSeconds > 0) {
            totalSeconds--;
            const h = Math.floor(totalSeconds / 3600);
            const m = Math.floor((totalSeconds % 3600) / 60);
            const s = totalSeconds % 60;
            timerEl.innerText = `${pad(h)}:${pad(m)}:${pad(s)}`;
        }
    }, 1000);
}

function pad(val) {
    return val < 10 ? '0' + val : val;
}

/**
 * 6. Run Code
 */

function submitCode() {
    console.log('Code intialization bruh for submission');
    const language = document.getElementById("languageSelect").selectedOptions[0].getAttribute('value');
    const version = document.getElementById("languageSelect").selectedOptions[0].getAttribute('version');
    const code = document.getElementById("codeEditor").value;
    const battle_id = document.getElementById("battleId").value;

    fetch(`/judge/submit_code/` , {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            language : language,
            version:version,
            code: code,
            battle_id: battle_id
        })
    })

    console.log('Code submitted for execution');
}

async function runCode() {
    console.log('Code intialization bruh for testcase running');
    const language = document.getElementById("languageSelect").selectedOptions[0].getAttribute('value');
    const version = document.getElementById("languageSelect").selectedOptions[0].getAttribute('version');
    const code = document.getElementById("codeEditor").value;
    const battle_id = document.getElementById("battleId").value;
    const input = document.getElementById("customInput").value;
    const outputArea = document.getElementById("customOutput");

    try {
        const response = await fetch(`/judge/run_code/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                language: language,
                version: version,
                code: code,
                battle_id: battle_id,
                input: input,
            })
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json(); // 👈 THIS is the output
        outputArea.value = data.output;

    } catch (error) {
        console.error("Error running code:", error);
    }



    console.log('Code submitted for execution');
}


const submitBtn = document.getElementById('btn-submit');
const runBtn = document.getElementById('btn-run');

if (submitBtn) {
    submitBtn.addEventListener('click', submitCode);
}

if (runBtn) {
    runBtn.addEventListener('click', runCode);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}