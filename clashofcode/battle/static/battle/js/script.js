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
    initRealtimeBattle();
    console.log('1v1 Interface Ready');
});

const TYPING_THROTTLE_MS = 800;
const TYPING_TIMEOUT_MS = 2500;

const ACTION_LABELS = {
    RUNNING: 'Opponent is Running code',
    SUBMITTED: 'Opponent has Submitted their code',
    FAILED_TC1: 'Opponents code Failed on test 1',
    TLE: 'Opponent\'s code got TLE, lol!',
    MLE: 'Opponent\'s code got MLE, lol!',
    WA: 'Opponent\'s code got Wrong answer, such a loser!',
    AC: 'Opponent\'s code got Accepted. You Lose! :(',
    RUN_COMPLETE: 'Opponent finished running code'
};

let battleSocket = null;
let battleClientId = null;
let lastTypingSentAt = 0;
let opponentLastTypingAt = 0;
let opponentAction = '';
let opponentStatusEl = null;

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

function updateLineNumbers(editor, lineNumbers) {
    const lines = editor.value.split('\n').length;
    lineNumbers.innerHTML = Array(lines).fill(0).map((_, i) => `<span>${i + 1}</span>`).join('');

};

function initEditor() {
    const editor = document.getElementById('codeEditor');
    const lineNumbers = document.getElementById('lineNumbers');

    updateLineNumbers(editor, lineNumbers);

    editor.addEventListener('input', () => {
        updateLineNumbers(editor, lineNumbers);
        sendTypingPing();
    });
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

    updateLineNumbers(editor, lineNumbers);
}

function initRealtimeBattle() {
    const battleIdInput = document.getElementById('battleId');
    const roomNameEl = document.getElementById('room-name');
    const roomName = battleIdInput?.value || (roomNameEl ? JSON.parse(roomNameEl.textContent) : null);

    if (!roomName || !('WebSocket' in window)) {
        return;
    }

    opponentStatusEl = document.getElementById('opponentStatus');

    battleClientId = window.crypto && window.crypto.randomUUID
        ? window.crypto.randomUUID()
        : Math.random().toString(36).slice(2);

    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const socketUrl = `${protocol}://${window.location.host}/ws/battle/${roomName}/`;

    battleSocket = new WebSocket(socketUrl);

    battleSocket.onmessage = (event) => {
        let payload = null;
        try {
            payload = JSON.parse(event.data);
        } catch (error) {
            return;
        }

        if (payload.clientId && payload.clientId === battleClientId) {
            return;
        }

        if (payload.type === 'typing') {
            opponentLastTypingAt = Date.now();
            renderOpponentStatus();
            return;
        }

        if (payload.type === 'action') {
            opponentAction = payload.action || '';
            renderOpponentStatus();
        }
    };

    battleSocket.onerror = () => {
        console.error('WebSocket error');
    };

    battleSocket.onclose = () => {
        battleSocket = null;
    };

    setInterval(renderOpponentStatus, 500);
}

function renderOpponentStatus() {
    if (!opponentStatusEl) {
        return;
    }

    const isTyping = Date.now() - opponentLastTypingAt <= TYPING_TIMEOUT_MS;

    if (isTyping) {
        opponentStatusEl.textContent = 'Typing...';
        return;
    }

    if (opponentAction) {
        opponentStatusEl.textContent = ACTION_LABELS[opponentAction] || opponentAction;
        return;
    }

    opponentStatusEl.textContent = 'Opponent is Thinking...';
}

function sendTypingPing() {
    if (!battleSocket || battleSocket.readyState !== WebSocket.OPEN) {
        return;
    }

    const now = Date.now();
    if (now - lastTypingSentAt < TYPING_THROTTLE_MS) {
        return;
    }

    lastTypingSentAt = now;
    battleSocket.send(JSON.stringify({
        type: 'typing',
        clientId: battleClientId,
        ts: now
    }));
}

function sendAction(action) {
    if (!battleSocket || battleSocket.readyState !== WebSocket.OPEN) {
        return;
    }

    battleSocket.send(JSON.stringify({
        type: 'action',
        clientId: battleClientId,
        action: action
    }));
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
 * 6. Submit Code
 */

async function submitCode() {
    console.log('Code intialization bruh for submission');
    sendAction('SUBMITTED');
    const language = document.getElementById("languageSelect").selectedOptions[0].getAttribute('value');
    const version = document.getElementById("languageSelect").selectedOptions[0].getAttribute('version');
    const code = document.getElementById("codeEditor").value;
    const battle_id = document.getElementById("battleId").value;

    try{
        const response = await fetch(`/judge/submit_code/` , {
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
        });

        if (!response.ok) {
                throw new Error("Server error");
            }
            
        console.log('Code submitted for execution');

        const data = await response.json();
        
        if (data.status === 'AC') {
            sendAction('AC');
            alert('Passed all Test Cases successfully!');
        } else if (data.status) {
            sendAction(data.status);
        } else {
            sendAction('WA');
            alert(data.message);
        }
        
        

    } catch (error) {
        console.error("Error submitting code:", error);
    }
}

/**
 * 7. Run Code
 */

async function runCode() {
    console.log('Code intialization bruh for testcase running');
    sendAction('RUNNING');
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
        sendAction('RUN_COMPLETE');

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


// Get cookie function for CSRF token retrieval
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







const resetBtn = document.getElementById('btn-reset');
resetBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to reset your code? This cannot be undone.')) {
        const editor = document.getElementById('codeEditor');
        const lineNumbers = document.getElementById('lineNumbers');

        document.getElementById('codeEditor').value = '';
        updateLineNumbers(editor, lineNumbers);
        sendTypingPing();
    }
});
