"use strict";

/* ==========================================
   KNIGHT & KNAVE: THE LOGIC QUEST
   Complete Engine with Audio, Map & Persistence
========================================== */

/* ------------------------------------------
   1. SYNTHESIZED AUDIO ENGINE (Web Audio API)
------------------------------------------ */
let audioEnabled = true;
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playSound(type) {
    if (!audioEnabled) return;
    try {
        const now = audioCtx.currentTime;

        if (type === "click") {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.frequency.setValueAtTime(400, now);
            osc.frequency.exponentialRampToValueAtTime(200, now + 0.05);
            gain.gain.setValueAtTime(0.3, now);
            gain.gain.linearRampToValueAtTime(0, now + 0.05);
            osc.start(now);
            osc.stop(now + 0.05);

        } else if (type === "success") {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.frequency.setValueAtTime(523.25, now); // C5
            osc.frequency.setValueAtTime(659.25, now + 0.1); // E5
            osc.frequency.setValueAtTime(783.99, now + 0.2); // G5
            gain.gain.setValueAtTime(0.3, now);
            gain.gain.linearRampToValueAtTime(0, now + 0.4);
            osc.start(now);
            osc.stop(now + 0.4);

        } else if (type === "error") {
            /* NEW: Distinct Descending Double-Tone "Wrong Answer" Sound */
            const osc1 = audioCtx.createOscillator();
            const osc2 = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc1.type = "sawtooth";
            osc2.type = "triangle";

            osc1.connect(gain);
            osc2.connect(gain);
            gain.connect(audioCtx.destination);

            // First low dissonant note
            osc1.frequency.setValueAtTime(220, now); // A3
            osc2.frequency.setValueAtTime(207.65, now); // G#3 (minor second interval for wrong feel)

            // Second lower note drop
            osc1.frequency.setValueAtTime(146.83, now + 0.15); // D3
            osc2.frequency.setValueAtTime(138.59, now + 0.15); // C#3

            gain.gain.setValueAtTime(0.25, now);
            gain.gain.linearRampToValueAtTime(0.01, now + 0.45);

            osc1.start(now);
            osc2.start(now);
            osc1.stop(now + 0.45);
            osc2.stop(now + 0.45);
        }
    } catch (e) {
        console.log("Audio play error", e);
    }
}

/* ------------------------------------------
   2. EXPANDED PUZZLE DATA ARCHITECTURE
   answer: "knight" | "knave" | "spy"
------------------------------------------ */
const levels = [
    {
        name: "EASY",
        puzzles: [
            {
                title: "The First Trial",
                description: "A guard stands before the gate. Examine their statement.",
                characters: [{ name: "Arin", statement: "2 + 2 = 4.", answer: "knight" }],
                hint: "Check if the mathematical equation is true.",
                explanation: "2 + 2 = 4 is true. Arin speaks truth, so Arin is a Knight."
            },
            {
                title: "The Fallen Star",
                description: "A guard speaks about astronomy.",
                characters: [{ name: "Borin", statement: "The Sun is a planet.", answer: "knave" }],
                hint: "The Sun is a star.",
                explanation: "Borin lies, making him a Knave."
            },
            {
                title: "The Simple Claim",
                description: "Determine the role of Guard Caren.",
                characters: [{ name: "Caren", statement: "I am a Knave.", answer: "knave" }],
                hint: "Can a Knight ever say 'I am a Knave'?",
                explanation: "A Knight cannot lie and call himself a Knave. Thus Caren must be lying, so Caren is a Knave."
            }
        ]
    },
    {
        name: "MEDIUM",
        puzzles: [
            {
                title: "The Two Guardians",
                description: "Two guardians make linked declarations.",
                characters: [
                    { name: "Arin", statement: "Borin is a Knave.", answer: "knave" },
                    { name: "Borin", statement: "Arin and I are different types.", answer: "knight" }
                ],
                hint: "If Borin is a Knight, check what his statement implies for Arin.",
                explanation: "Arin is a Knave and Borin is a Knight."
            },
            {
                title: "The Royal Oath",
                description: "Two guardians speak.",
                characters: [
                    { name: "Celia", statement: "Daren is a Knight.", answer: "knight" },
                    { name: "Daren", statement: "Celia and I are the same type.", answer: "knight" }
                ],
                hint: "Check if both being Knights works logically.",
                explanation: "Both are Knights."
            },
            {
                title: "The Spy Infiltration",
                description: "One of these two guards is a Spy who can lie or tell truth!",
                characters: [
                    { name: "Elara", statement: "Finn is a Knight.", answer: "spy" },
                    { name: "Finn", statement: "Elara is a Spy.", answer: "knight" }
                ],
                hint: "Work backwards from Finn's statement.",
                explanation: "Finn is a Knight (telling the truth that Elara is a Spy)."
            }
        ]
    },
    {
        name: "HARD",
        puzzles: [
            {
                title: "The Triple Conspiracy",
                description: "Three guards stand guard. Analyze all three.",
                characters: [
                    { name: "Arin", statement: "Borin is a Knave.", answer: "knave" },
                    { name: "Borin", statement: "Celia is a Knave.", answer: "knight" },
                    { name: "Celia", statement: "Arin and Borin are the same type.", answer: "knave" }
                ],
                hint: "Arin and Borin must be opposite types.",
                explanation: "Arin is a Knave, Borin is a Knight, and Celia is a Knave."
            },
            {
                title: "The Spy Court",
                description: "Three characters: One Knight, one Knave, one Spy.",
                characters: [
                    { name: "Daren", statement: "I am a Spy.", answer: "spy" },
                    { name: "Elara", statement: "Daren speaks the truth.", answer: "knave" },
                    { name: "Finn", statement: "I am a Knight.", answer: "knight" }
                ],
                hint: "Neither a Knight nor Knave can claim 'I am a Spy'.",
                explanation: "Daren is the Spy, Elara is a Knave, and Finn is the Knight."
            },
            {
                title: "The Ultimate Verdict",
                description: "All three guards present circular statements.",
                characters: [
                    { name: "Gideon", statement: "Hala is a Knight.", answer: "knave" },
                    { name: "Hala", statement: "Ivar is a Knight.", answer: "knave" },
                    { name: "Ivar", statement: "Gideon and Hala are the same type.", answer: "knave" }
                ],
                hint: "Test if all three could be Knaves.",
                explanation: "All three are Knaves!"
            }
        ]
    }
];

/* ------------------------------------------
   3. GLOBAL STATE & PERSISTENCE
------------------------------------------ */
let playerName = "Logic Master";
let levelIndex = 0;
let puzzleIndex = 0;
let score = 0;
let hintUsed = false;
let solved = false;
let questCompleted = false;
let selections = [];
let unlockedLevels = [true, false, false];
let achievements = {
    noHint: false,
    speedy: false,
    champion: false
};

function loadSavedData() {
    const saved = localStorage.getItem("knight_knave_save");
    if (saved) {
        try {
            const data = JSON.parse(saved);
            playerName = data.playerName || playerName;
            score = data.score || 0;
            unlockedLevels = data.unlockedLevels || [true, false, false];
            achievements = data.achievements || achievements;
        } catch(e){}
    }
}

function saveData() {
    const data = {
        playerName,
        score,
        unlockedLevels,
        achievements
    };
    localStorage.setItem("knight_knave_save", JSON.stringify(data));
}

/* ------------------------------------------
   4. DOM ELEMENTS & NAVIGATION
------------------------------------------ */
const introScreen = document.getElementById("introScreen");
const welcomeScreen = document.getElementById("welcomeScreen");
const mapScreen = document.getElementById("mapScreen");
const gameScreen = document.getElementById("gameScreen");

const enterButton = document.getElementById("enterButton");
const homeButton = document.getElementById("homeButton");
const backToProfileBtn = document.getElementById("backToProfileBtn");
const audioToggleBtn = document.getElementById("audioToggleBtn");

const nameForm = document.getElementById("nameForm");
const playerNameInput = document.getElementById("playerName");

const playerGreeting = document.getElementById("playerGreeting");
const levelLabel = document.getElementById("levelLabel");
const scoreLabel = document.getElementById("scoreLabel");
const rankLabel = document.getElementById("rankLabel");

const puzzleTitle = document.getElementById("puzzleTitle");
const puzzleDescription = document.getElementById("puzzleDescription");
const difficultyBadge = document.getElementById("difficultyBadge");
const progressText = document.getElementById("progressText");

const charactersContainer = document.getElementById("charactersContainer");
const feedback = document.getElementById("feedback");
const hintBox = document.getElementById("hintBox");
const rewardMessage = document.getElementById("rewardMessage");

const hintButton = document.getElementById("hintButton");
const checkButton = document.getElementById("checkButton");
const resetButton = document.getElementById("resetButton");
const nextButton = document.getElementById("nextButton");

function showScreen(screen) {
    [introScreen, welcomeScreen, mapScreen, gameScreen].forEach(s => s && s.classList.add("hidden"));
    if (screen) screen.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });
}

if (audioToggleBtn) {
    audioToggleBtn.addEventListener("click", () => {
        audioEnabled = !audioEnabled;
        audioToggleBtn.innerHTML = `<span>🔊 AUDIO: ${audioEnabled ? 'ON' : 'OFF'}</span>`;
        playSound("click");
    });
}

if (enterButton) {
    enterButton.addEventListener("click", () => {
        playSound("click");
        showScreen(welcomeScreen);
        renderAchievements();
    });
}

if (backToProfileBtn) {
    backToProfileBtn.addEventListener("click", () => {
        playSound("click");
        showScreen(welcomeScreen);
    });
}

if (homeButton) {
    homeButton.addEventListener("click", () => {
        playSound("click");
        showScreen(mapScreen);
        updateMapNodes();
    });
}

/* ------------------------------------------
   5. MAP & PROFILE MANAGEMENT
------------------------------------------ */
function renderAchievements() {
    const list = document.getElementById("achievementsList");
    if (!list) return;
    list.innerHTML = `
        <div class="achievement-badge ${achievements.noHint ? '' : 'locked'}">🧠 Pure Logic (No Hints)</div>
        <div class="achievement-badge ${achievements.champion ? '' : 'locked'}">👑 Royal Champion</div>
    `;
}

function updateMapNodes() {
    for (let i = 0; i < 3; i++) {
        const node = document.getElementById(`node-${i}`);
        if (node) {
            if (unlockedLevels[i]) {
                node.className = "map-node unlocked";
                node.querySelector(".node-icon").textContent = i === 0 ? "🛡️" : i === 1 ? "⚔️" : "👑";
            } else {
                node.className = "map-node locked";
                node.querySelector(".node-icon").textContent = "🔒";
            }
        }
    }
}

window.selectLevelFromMap = function(idx) {
    if (!unlockedLevels[idx]) {
        playSound("error");
        alert("Unlock previous levels first!");
        return;
    }
    playSound("click");
    levelIndex = idx;
    puzzleIndex = 0;
    showScreen(gameScreen);
    renderPuzzle();
};

if (nameForm) {
    nameForm.addEventListener("submit", (e) => {
        e.preventDefault();
        playSound("click");
        playerName = playerNameInput.value.trim() || "Logic Master";
        saveData();
        if (playerGreeting) playerGreeting.textContent = playerName;
        showScreen(mapScreen);
        updateMapNodes();
    });
}

/* ------------------------------------------
   6. RENDERING PUZZLES & CARDS
------------------------------------------ */
function getCurrentPuzzle() {
    return levels[levelIndex].puzzles[puzzleIndex];
}

function renderPuzzle() {
    const puzzle = getCurrentPuzzle();
    solved = false;
    hintUsed = false;
    selections = puzzle.characters.map(() => null);

    if (levelLabel) levelLabel.textContent = levels[levelIndex].name;
    if (difficultyBadge) difficultyBadge.textContent = levels[levelIndex].name + " LEVEL";
    if (puzzleTitle) puzzleTitle.textContent = puzzle.title;
    if (puzzleDescription) puzzleDescription.textContent = puzzle.description;
    if (progressText) progressText.textContent = `${puzzleIndex + 1} / ${levels[levelIndex].puzzles.length}`;

    if (feedback) feedback.className = "feedback-banner hidden";
    if (hintBox) hintBox.className = "hint-inset hidden";
    if (rewardMessage) rewardMessage.className = "reward-banner hidden";

    if (checkButton) checkButton.classList.remove("hidden");
    if (hintButton) { hintButton.disabled = false; hintButton.classList.remove("hidden"); }
    if (resetButton) resetButton.classList.remove("hidden");
    if (nextButton) nextButton.classList.add("hidden");

    if (charactersContainer) {
        charactersContainer.replaceChildren();
        puzzle.characters.forEach((char, idx) => createCharacterCard(char, idx));
    }

    updateHUD();
}

function createCharacterCard(character, index) {
    const card = document.createElement("article");
    card.className = "character-card";

    const portrait = document.createElement("div");
    portrait.className = "portrait-circle";
    portrait.textContent = character.answer === "knight" ? "⚔️" : character.answer === "knave" ? "☠️" : "🕵️";

    const idTag = document.createElement("div");
    idTag.className = "character-id";
    idTag.textContent = "GUARD " + String.fromCharCode(65 + index);

    const name = document.createElement("h3");
    name.textContent = character.name;

    const speechBox = document.createElement("div");
    speechBox.className = "speech-bubble";
    speechBox.innerHTML = `<p>“${character.statement}”</p>`;

    const btnContainer = document.createElement("div");
    btnContainer.className = "verdict-buttons";

    ["knight", "knave", "spy"].forEach(type => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn-choice";
        btn.dataset.character = String(index);
        btn.dataset.type = type;
        btn.textContent = type === "knight" ? "⚔️ Knight" : type === "knave" ? "☠️ Liar" : "🕵️ Spy";
        btn.addEventListener("click", () => selectRole(index, type));
        btnContainer.appendChild(btn);
    });

    card.append(portrait, idTag, name, speechBox, btnContainer);
    charactersContainer.appendChild(card);
}

function selectRole(index, type) {
    if (solved) return;
    playSound("click");
    selections[index] = type;

    const btns = charactersContainer.querySelectorAll(`.btn-choice[data-character="${index}"]`);
    btns.forEach(btn => {
        btn.classList.remove("selected-knight", "selected-knave", "selected-spy");
        if (btn.dataset.type === type) {
            btn.classList.add(`selected-${type}`);
        }
    });
}

/* ------------------------------------------
   7. CHECKING SOLUTION & CONFETTI POPPER
------------------------------------------ */
function checkAnswer() {
    if (solved) return;

    if (selections.some(ans => ans === null)) {
        playSound("error");
        feedback.className = "feedback-banner error";
        feedback.textContent = "⚠️ Assign a role to every character!";
        return;
    }

    const puzzle = getCurrentPuzzle();
    const correct = puzzle.characters.every((char, idx) => selections[idx] === char.answer);

    if (!correct) {
        playSound("error");
        feedback.className = "feedback-banner error";
        feedback.textContent = "❌ Incorrect verdict! Check the statements carefully.";
        return;
    }

    solved = true;
    playSound("success");
    triggerConfetti();

    const pts = hintUsed ? 5 : 10;
    if (!hintUsed) achievements.noHint = true;
    score += pts;

    feedback.className = "feedback-banner success";
    feedback.textContent = `✓ Correct! ${puzzle.explanation}`;

    rewardMessage.className = "reward-banner";
    rewardMessage.textContent = `🎉 Earned +${pts} Points!`;

    if (checkButton) checkButton.classList.add("hidden");
    if (hintButton) hintButton.disabled = true;

    if (puzzleIndex === levels[levelIndex].puzzles.length - 1) {
        if (levelIndex < 2) {
            unlockedLevels[levelIndex + 1] = true;
        } else {
            achievements.champion = true;
        }
    }

    saveData();
    updateHUD();

    if (nextButton) {
        nextButton.classList.remove("hidden");
        nextButton.onclick = nextPuzzle;
    }
}

if (checkButton) checkButton.addEventListener("click", checkAnswer);

function triggerConfetti() {
    const colors = ["#ffd700", "#5adb28", "#00bfff", "#ff9800", "#b026ff"];
    for (let i = 0; i < 60; i++) {
        const confetti = document.createElement("div");
        confetti.className = "confetti-piece";
        confetti.style.left = Math.random() * 100 + "vw";
        confetti.style.top = "-10px";
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDuration = (1.5 + Math.random() * 1.5) + "s";
        document.body.appendChild(confetti);
        setTimeout(() => confetti.remove(), 3000);
    }
}

function nextPuzzle() {
    playSound("click");
    if (puzzleIndex < levels[levelIndex].puzzles.length - 1) {
        puzzleIndex++;
        renderPuzzle();
    } else {
        showScreen(mapScreen);
        updateMapNodes();
    }
}

/* ------------------------------------------
   8. CANVAS SNOW ANIMATION
------------------------------------------ */
function initSnowCanvas() {
    const canvas = document.getElementById("snowCanvas");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener("resize", () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = Array.from({ length: 70 }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 3 + 1,
        d: Math.random() * 1 + 0.5
    }));

    function draw() {
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = "rgba(255, 255, 255, 0.7)";
        ctx.beginPath();
        particles.forEach(p => {
            ctx.moveTo(p.x, p.y);
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2, true);
        });
        ctx.fill();

        particles.forEach(p => {
            p.y += p.d;
            if (p.y > height) {
                p.y = -10;
                p.x = Math.random() * width;
            }
        });
        requestAnimationFrame(draw);
    }
    draw();
}

function updateHUD() {
    if (scoreLabel) scoreLabel.textContent = String(score);
    if (rankLabel) {
        let r = "Rookie";
        if (score >= 25) r = "Apprentice";
        if (score >= 50) r = "Master";
        if (score >= 80) r = "Champion";
        rankLabel.textContent = r;
    }
}

/* ------------------------------------------
   9. INITIALIZATION
------------------------------------------ */
loadSavedData();
initSnowCanvas();