// Inline app logic (no external deps)
const STORAGE_KEY = "spades-scorekeeper-state-v1";

function createInitialState() {
  return {
    round: 1,
    phase: "books",
    playerA1: "",
    playerA2: "",
    playerB1: "",
    playerB2: "",
    dealerIndex: 0, // 0: A1, 1: B1, 2: A2, 3: B2
    totalA: 0,
    totalB: 0,
    bagsA: 0,
    bagsB: 0,
    hands: [],
    lockedBids: false,
    blind10A: false,
    blind10B: false,
    nilA: false,
    nilB: false,
    prevBidA: 6,
    prevBidB: 6,
    nilPrevBidA: 6,
    nilPrevBidB: 6,
    started: false,
    gameOver: false,
    winnerName: null,
  };
}

// Helper to get team name from player names
function getTeamName(player1, player2, fallback) {
  if (player1 && player2) {
    return `${player1} & ${player2}`;
  }
  return fallback;
}

function getTeamA() {
  return getTeamName(state.playerA1, state.playerA2, "Team A");
}

function getTeamB() {
  return getTeamName(state.playerB1, state.playerB2, "Team B");
}

const state = createInitialState();
let pendingSnapshot = null;
let isHydrating = false;
let confettiCleanup = null;

const $ = (s) => document.querySelector(s);

function getSpinnerText(id) {
  return document.getElementById(id)?.textContent || "";
}

function getDealerName(dealerIndex) {
  // Dealer order: A1 -> B1 -> A2 -> B2 -> A1 -> ...
  const idx = dealerIndex % 4;
  switch (idx) {
    case 0: return state.playerA1 || "Player A1";
    case 1: return state.playerB1 || "Player B1";
    case 2: return state.playerA2 || "Player A2";
    case 3: return state.playerB2 || "Player B2";
    default: return "Unknown";
  }
}

function updateDealerDisplay() {
  const dealerRow = $("#dealerRow");
  const dealerDisplay = $("#dealerDisplay");
  if (!dealerRow || !dealerDisplay) return;
  
  if (state.gameOver) {
    dealerRow.style.display = "none";
    return;
  }
  
  const dealerName = getDealerName(state.dealerIndex);
  dealerDisplay.textContent = `🂡 Dealer: ${dealerName}`;
  dealerRow.style.display = "";
}

function stopConfetti() {
  if (typeof confettiCleanup === "function") {
    confettiCleanup();
    confettiCleanup = null;
  }
}

function startConfetti() {
  stopConfetti();
  if (typeof window === "undefined") return;
  const canvas = document.getElementById("winnerConfetti");
  if (!(canvas instanceof HTMLCanvasElement)) return;
  const parent = canvas.parentElement;
  if (!parent) return;
  const ctx = canvas.getContext("2d");
  if (!ctx || typeof rough === "undefined") return;
  const dpr = window.devicePixelRatio || 1;
  let width = 0;
  let height = 0;

  function resize() {
    const rect = parent.getBoundingClientRect();
    width = rect.width || parent.clientWidth || window.innerWidth;
    height = rect.height || parent.clientHeight || window.innerHeight;
    canvas.width = Math.max(1, Math.floor(width * dpr));
    canvas.height = Math.max(1, Math.floor(height * dpr));
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
  }

  resize();
  window.addEventListener("resize", resize);

  const colors = ["#2563eb", "#0ea5e9", "#22c55e", "#f59e0b", "#ec4899", "#6366f1"];
  const particleCount = 140;

  const particles = Array.from({ length: particleCount }, () => ({
    x: Math.random() * width,
    y: Math.random() * -height,
    size: 4 + Math.random() * 6,
    velocityX: (Math.random() - 0.5) * 1.4,
    velocityY: 2 + Math.random() * 3,
    rotation: Math.random() * 360,
    rotationSpeed: (Math.random() - 0.5) * 8,
    sway: 0.0015 + Math.random() * 0.003,
    color: colors[Math.floor(Math.random() * colors.length)],
  }));

  let running = true;
  let frameId = null;
  let fadeTimeout = null;
  const duration = 5000;

  canvas.classList.add("active");

  function step(now) {
    if (!running) return;
    ctx.clearRect(0, 0, width, height);
    particles.forEach((p) => {
      p.x += p.velocityX + Math.sin(now * p.sway) * 0.6;
      p.y += p.velocityY;
      p.rotation += p.rotationSpeed;

      if (p.y > height + p.size) {
        p.y = -10;
        p.x = Math.random() * width;
      }
      if (p.x < -30) p.x = width + 30;
      if (p.x > width + 30) p.x = -30;

      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate((p.rotation * Math.PI) / 180);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = 0.85;
      ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 1.1);
      ctx.restore();
    });
    frameId = window.requestAnimationFrame(step);
  }

  frameId = window.requestAnimationFrame(step);

  const endTimeout = window.setTimeout(() => stop(true), duration);

  function finalize() {
    window.removeEventListener("resize", resize);
    if (frameId !== null) {
      window.cancelAnimationFrame(frameId);
      frameId = null;
    }
    if (fadeTimeout !== null) {
      window.clearTimeout(fadeTimeout);
      fadeTimeout = null;
    }
    window.clearTimeout(endTimeout);
    ctx.clearRect(0, 0, width, height);
    confettiCleanup = null;
  }

  function stop(withFade) {
    if (!running) {
      finalize();
      return;
    }
    running = false;
    canvas.classList.remove("active");
    if (withFade) {
      fadeTimeout = window.setTimeout(finalize, 350);
    } else {
      finalize();
    }
  }

  confettiCleanup = () => stop(false);
}

function snapshotForStorage() {
  const stateCopy = {
    ...state,
    hands: state.hands.map((hand) => ({ ...hand })),
  };
  return {
    version: 1,
    state: stateCopy,
    ui: {
      bidA: getSpinnerText("bidA"),
      bidB: getSpinnerText("bidB"),
      booksA: getSpinnerText("booksA"),
      booksB: getSpinnerText("booksB"),
      status: $("#status")?.textContent || "",
      setupHidden: $("#setup")?.style.display === "none",
      gameVisible: $("#game")?.style.display !== "none",
      winnerVisible: $("#winner")?.style.display !== "none",
    },
  };
}

function saveState() {
  if (isHydrating) return;
  try {
    if (typeof window === "undefined" || !window.localStorage) return;
    const payload = snapshotForStorage();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  } catch (err) {
    console.error("Failed to save state", err);
  }
}

function readSnapshotFromStorage() {
  try {
    if (typeof window === "undefined" || !window.localStorage) return null;
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (err) {
    console.error("Failed to read saved game", err);
    return null;
  }
}

function clearStoredState() {
  try {
    if (typeof window === "undefined" || !window.localStorage) return;
    window.localStorage.removeItem(STORAGE_KEY);
  } catch (err) {
    console.error("Failed to clear saved game", err);
  }
}

function restartGame() {
  stopConfetti();
  clearStoredState();
  if (typeof window !== "undefined" && typeof window.location !== "undefined") {
    window.location.reload();
  }
}

function applyEndGameUI(winnerName) {
  $("#bidsRow").style.display = "none";
  $("#booksRow").style.display = "none";
  const actions = document.querySelector(".toolbar:has(#deleteLastBtn)");
  if (actions) actions.style.display = "none";
  const message = `${winnerName} wins!`;
  const status = $("#status");
  if (status) status.textContent = "";
  const winnerSection = $("#winner");
  if (winnerSection) winnerSection.style.display = "";
  const winnerText = $("#winnerText");
  if (winnerText) winnerText.textContent = message;
  startConfetti();
  updateNewGameButtons();
}

function applySnapshot(snapshot, { hideSetup = true } = {}) {
  if (!snapshot || !snapshot.state) return;
  stopConfetti();
  isHydrating = true;
  const fresh = createInitialState();
  const savedState = {
    ...fresh,
    ...snapshot.state,
    hands: (snapshot.state.hands || []).map((hand) => ({ ...hand })),
  };
  if (savedState.nilPrevBidA === undefined) savedState.nilPrevBidA = 6;
  if (savedState.nilPrevBidB === undefined) savedState.nilPrevBidB = 6;
  if (savedState.dealerIndex === undefined) savedState.dealerIndex = 0;
  Object.assign(state, savedState);
  if (!state.started && state.hands.length > 0) state.started = true;

  if (hideSetup) {
    $("#setup").style.display = "none";
    $("#game").style.display = "";
  }
  $("#playerA1").value = state.playerA1 || "";
  $("#playerA2").value = state.playerA2 || "";
  $("#playerB1").value = state.playerB1 || "";
  $("#playerB2").value = state.playerB2 || "";

  // Restore spinner values
  const ui = snapshot.ui || {};
  if (ui.bidA !== undefined) $("#bidA").textContent = String(ui.bidA);
  if (ui.bidB !== undefined) $("#bidB").textContent = String(ui.bidB);
  if (ui.booksA !== undefined) $("#booksA").textContent = String(ui.booksA);
  if (ui.booksB !== undefined) $("#booksB").textContent = String(ui.booksB);

  renderHands();
  updatePills();
  togglePhaseUI();
  updateDealerDisplay();

  if (state.lockedBids) {
    const lock = $("#bidsActions");
    if (lock) lock.style.display = "none";
    const baWrap = $("#blind10A")?.closest(".spinner-actions");
    if (baWrap) baWrap.style.display = "none";
    const bbWrap = $("#blind10B")?.closest(".spinner-actions");
    if (bbWrap) bbWrap.style.display = "none";
    const naWrap = $("#nilA")?.closest(".spinner-actions");
    if (naWrap) naWrap.style.display = "none";
    const nbWrap = $("#nilB")?.closest(".spinner-actions");
    if (nbWrap) nbWrap.style.display = "none";
    const note = $("#unbidNote");
    if (note) note.style.display = "none";
  }

  if (ui.status !== undefined) {
    $("#status").textContent = ui.status;
  }

  if (state.gameOver && state.winnerName) {
    applyEndGameUI(state.winnerName);
  } else {
    const actions = document.querySelector(".toolbar:has(#deleteLastBtn)");
    if (actions) actions.style.display = "";
  }
  updateNewGameButtons();
  updateNilButtons();
  updateUnbidNote();
  updateBooksSum();
  isHydrating = false;
  saveState();
}
function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function updatePills() {
  const teamA = getTeamA();
  const teamB = getTeamB();

  const nameA = $("#scoreNameA");
  if (nameA) nameA.textContent = teamA;
  const nameB = $("#scoreNameB");
  if (nameB) nameB.textContent = teamB;
  const round = $("#pillRound");
  if (round) round.textContent = `Round ${state.round}`;
  const pointsA = $("#scorePointsA");
  if (pointsA) pointsA.textContent = state.totalA;
  const pointsB = $("#scorePointsB");
  if (pointsB) pointsB.textContent = state.totalB;
  
  const bagsA = $("#scoreBagsA");
  if (bagsA) bagsA.textContent = state.bagsA > 0 ? `(${state.bagsA})` : "";
  const bagsB = $("#scoreBagsB");
  if (bagsB) bagsB.textContent = state.bagsB > 0 ? `(${state.bagsB})` : "";

  // Update spinner labels with "Team A: Player1 & Player2" format
  const bidLabelA = $("#bidLabelA");
  if (bidLabelA) bidLabelA.textContent = `Team A: ${state.playerA1 || "Player1"} & ${state.playerA2 || "Player2"}`;
  const bidLabelB = $("#bidLabelB");
  if (bidLabelB) bidLabelB.textContent = `Team B: ${state.playerB1 || "Player1"} & ${state.playerB2 || "Player2"}`;
  const booksLabelA = $("#booksLabelA");
  if (booksLabelA) booksLabelA.textContent = `Team A: ${state.playerA1 || "Player1"} & ${state.playerA2 || "Player2"}`;
  const booksLabelB = $("#booksLabelB");
  if (booksLabelB) booksLabelB.textContent = `Team B: ${state.playerB1 || "Player1"} & ${state.playerB2 || "Player2"}`;

  const pillA = $("#pillA");
  if (pillA) {
    const bagsDisplayA = state.bagsA > 0 ? ` (${state.bagsA})` : "";
    pillA.textContent = `${teamA}: ${state.totalA}${bagsDisplayA}`;
  }
  const pillB = $("#pillB");
  if (pillB) {
    const bagsDisplayB = state.bagsB > 0 ? ` (${state.bagsB})` : "";
    pillB.textContent = `${teamB}: ${state.totalB}${bagsDisplayB}`;
  }
}

function updateBooksSum() {
  const a = +$("#booksA").textContent;
  const b = +$("#booksB").textContent;
  const btn = $("#submitHandBtn");
  if (btn) btn.disabled = !(state.phase === "books" && a + b === 13);
}

function updateUnbidNote() {
  const bA = +($("#bidA")?.textContent || 0);
  const bB = +($("#bidB")?.textContent || 0);
  const note = $("#unbidNote");
  if (note) note.textContent = `Unbid books left: ${13 - (bA + bB)}`;
}

function onSpinnerChange(spinner, newVal, { link = false } = {}) {
  const target = spinner.dataset.target;
  if (target === "booksA" || target === "booksB") {
    if (link) {
      const otherId = target === "booksA" ? "booksB" : "booksA";
      const otherEl = document.getElementById(otherId);
      otherEl.textContent = String(clamp(13 - newVal, 0, 13));
    }
    updateBooksSum();
  } else if (target === "bidA" || target === "bidB") {
    updateUnbidNote();
  }
}

function setValueFor(id, delta) {
  const vEl = document.getElementById(id);
  if (!vEl) return;
  const spinner = vEl.closest(".spinner");
  const min = +spinner.dataset.min,
    max = +spinner.dataset.max;
  const next = clamp((+vEl.textContent || 0) + delta, min, max);
  vEl.textContent = String(next);
  onSpinnerChange(spinner, next, { link: id === "booksA" || id === "booksB" });
  saveState();
}

function wireArrowButtons() {
  document.querySelectorAll("[data-arrow]")?.forEach((btn) => {
    btn.onclick = (ev) => {
      ev.preventDefault();
      ev.stopPropagation();
      const id = btn.getAttribute("data-for");
      const up = btn.getAttribute("data-arrow") === "up";
      setValueFor(id, up ? +1 : -1);
    };
  });
}

function applyBlindLocks() {
  const aUp = document.querySelector(
    '[data-arrow][data-for="bidA"][data-arrow="up"]',
  );
  const aDn = document.querySelector(
    '[data-arrow][data-for="bidA"][data-arrow="down"]',
  );
  const bUp = document.querySelector(
    '[data-arrow][data-for="bidB"][data-arrow="up"]',
  );
  const bDn = document.querySelector(
    '[data-arrow][data-for="bidB"][data-arrow="down"]',
  );

  if (state.phase === "bids" && !state.lockedBids) {
    if (state.blind10A) {
      state.prevBidA = +$("#bidA").textContent || 6;
      $("#bidA").textContent = "10";
    }
    if (state.blind10B) {
      state.prevBidB = +$("#bidB").textContent || 6;
      $("#bidB").textContent = "10";
    }
  }

  const disableArrows =
    state.blind10A || state.nilA || state.phase === "books" || state.lockedBids;
  if (aUp) aUp.disabled = disableArrows;
  if (aDn) aDn.disabled = disableArrows;
  const disableArrowsB =
    state.blind10B || state.nilB || state.phase === "books" || state.lockedBids;
  if (bUp) bUp.disabled = disableArrowsB;
  if (bDn) bDn.disabled = disableArrowsB;

  const bidSpinners = document.querySelectorAll("#bidsRow .spinner");
  bidSpinners.forEach((sp) => {
    const arrows = sp.querySelectorAll(".arrow button");
    const value = sp.querySelector(".value");
    if (state.lockedBids) {
      arrows.forEach((arrow) => (arrow.style.display = "none"));
      if (value) value.style.color = "#777"; // Grey color
    } else {
      arrows.forEach((arrow) => (arrow.style.display = "")); // Restore default
      if (value) value.style.color = ""; // Restore default
    }
  });
}

function togglePhaseUI() {
  const bids = $("#bidsRow");
  const books = $("#booksRow");
  const bidsActions = $("#bidsActions");
  const baWrap = $("#blind10A")?.closest(".spinner-actions");
  const bbWrap = $("#blind10B")?.closest(".spinner-actions");
  const naWrap = $("#nilA")?.closest(".spinner-actions");
  const nbWrap = $("#nilB")?.closest(".spinner-actions");
  const note = $("#unbidNote");

  [baWrap, bbWrap, naWrap, nbWrap].forEach((wrap) => {
    if (wrap) wrap.style.display = "none";
  });

  if (state.round === 1) {
    if (bids) bids.style.display = "none";
    if (books) books.style.display = "";
  } else if (state.phase === "bids") {
    if (bids) bids.style.display = "";
    if (books) books.style.display = "none";
    if (bidsActions) bidsActions.style.display = "";
    if (baWrap) baWrap.style.display = "";
    if (bbWrap) bbWrap.style.display = "";
    if (naWrap) naWrap.style.display = "";
    if (nbWrap) nbWrap.style.display = "";
    if (note) note.style.display = ""; // Make unbid note visible
  } else {
    // state.phase === 'books'
    if (bids) bids.style.display = "";
    if (books) books.style.display = "";
    // Ensure all spinners are enabled when in books phase
    document.querySelectorAll("#booksRow .spinner").forEach((sp) => {
      sp.classList.remove("disabled");
    });
  }

  if (note && state.phase !== "bids") note.style.display = "none";

  applyBlindLocks();
  updateBlindButtons();
  updateNilButtons();

  // Ensure books spinners are never disabled (redundant but for safety)
  document.querySelectorAll("#booksRow .spinner").forEach((sp) => {
    sp.classList.remove("disabled");
  });
  updateUnbidNote();
  updateBooksSum();
}

function updateBlindButtons() {
  const a = $("#blind10A");
  const b = $("#blind10B");
  const disable = state.phase !== "bids" || state.lockedBids;
  if (a) {
    a.disabled = disable;
    a.classList.toggle("button-outline", !state.blind10A);
    a.textContent = state.blind10A ? "Blind 10 ✓" : "Blind 10";
  }
  if (b) {
    b.disabled = disable;
    b.classList.toggle("button-outline", !state.blind10B);
    b.textContent = state.blind10B ? "Blind 10 ✓" : "Blind 10";
  }
}

function updateNilButtons() {
  const disable = state.phase !== "bids" || state.lockedBids;
  const a = $("#nilA");
  const b = $("#nilB");
  if (a) {
    a.disabled = disable;
    a.classList.toggle("button-outline", !state.nilA);
    a.textContent = state.nilA ? "Nil ✓" : "Nil";
  }
  if (b) {
    b.disabled = disable;
    b.classList.toggle("button-outline", !state.nilB);
    b.textContent = state.nilB ? "Nil ✓" : "Nil";
  }
}

function updateNewGameButtons() {
  const main = $("#newGameBtnMain");
  if (main) main.style.display = state.gameOver ? "" : "none";
  updateDeleteButton();
}

function updateDeleteButton() {
  const deleteBtn = $("#deleteLastBtn");
  if (!deleteBtn) return;
  const hasHands = state.hands.length > 0;
  deleteBtn.textContent = hasHands ? "Delete Last Hand" : "New Game";
  deleteBtn.classList.toggle("button-outline", hasHands);
}

function scoreHand(
  round,
  bidA,
  bidB,
  booksA,
  booksB,
  blindA = false,
  blindB = false,
) {
  if (round === 1) {
    if (booksA < 4 || booksB < 4)
      return {
        scoreA: booksA < 4 ? -99999 : 10 * booksA,
        scoreB: booksB < 4 ? -99999 : 10 * booksB,
        bagA: 0,
        bagB: 0,
        imm: true,
      };
    return {
      scoreA: 10 * booksA,
      scoreB: 10 * booksB,
      bagA: 0,
      bagB: 0,
      imm: false,
    };
  }
  let scoreA = booksA >= bidA ? 10 * bidA : -10 * bidA;
  let scoreB = booksB >= bidB ? 10 * bidB : -10 * bidB;

  const bagA = booksA > bidA ? booksA - bidA : 0;
  const bagB = booksB > bidB ? booksB - bidB : 0;

  return { scoreA, scoreB, bagA, bagB, imm: false };
}

function checkWin() {
  if (state.totalA >= 500 || state.totalB >= 500) {
    if (state.totalA === state.totalB) return null;
    return state.totalA > state.totalB ? getTeamA() : getTeamB();
  }
  return null;
}

function updateChart() {
  if (state.hands.length === 0) {
    const chartsSection = $("#charts");
    if (chartsSection) chartsSection.style.display = "none";
    return;
  }

  const chartsSection = $("#charts");
  if (chartsSection) chartsSection.style.display = "";

  const canvas = document.getElementById("scoreChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  // Calculate cumulative scores
  const dataA = [0];
  const dataB = [0];
  let runningA = 0;
  let runningB = 0;

  state.hands.forEach((h) => {
    runningA += h.scoreA;
    runningB += h.scoreB;
    dataA.push(runningA);
    dataB.push(runningB);
  });

  // Set canvas size (accounting for device pixel ratio)
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.scale(dpr, dpr);

  // Chart dimensions
  const padding = { top: 40, right: 60, bottom: 40, left: 60 };
  const chartWidth = rect.width - padding.left - padding.right;
  const chartHeight = rect.height - padding.top - padding.bottom;

  // Find data range
  const allData = [...dataA, ...dataB];
  const minY = Math.min(0, ...allData);
  const maxY = Math.max(500, ...allData);
  const yRange = maxY - minY;

  // Helper functions
  const getX = (index) => padding.left + (index / (dataA.length - 1)) * chartWidth;
  const getY = (value) => padding.top + chartHeight - ((value - minY) / yRange) * chartHeight;

  // Clear canvas
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, rect.width, rect.height);

  // Draw grid with xkcd style (slightly wavy)
  ctx.strokeStyle = "#e5e7eb";
  ctx.lineWidth = 1;
  ctx.setLineDash([]);

  // Draw horizontal grid lines
  const numHLines = 5;
  for (let i = 0; i <= numHLines; i++) {
    const y = padding.top + (i / numHLines) * chartHeight;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    for (let x = padding.left; x <= padding.left + chartWidth; x += 10) {
      const wobble = Math.sin(x * 0.1 + i) * 0.5;
      ctx.lineTo(x, y + wobble);
    }
    ctx.stroke();
  }

  // Draw vertical grid lines
  const numVLines = Math.min(dataA.length - 1, 10);
  for (let i = 0; i <= numVLines; i++) {
    const x = padding.left + (i / numVLines) * chartWidth;
    ctx.beginPath();
    ctx.moveTo(x, padding.top);
    for (let y = padding.top; y <= padding.top + chartHeight; y += 10) {
      const wobble = Math.cos(y * 0.1 + i) * 0.5;
      ctx.lineTo(x + wobble, y);
    }
    ctx.stroke();
  }

  // Draw 500-point line (with dashed xkcd style)
  if (maxY >= 500 && minY <= 500) {
    const y500 = getY(500);
    ctx.strokeStyle = "#16a34a";
    ctx.lineWidth = 2;
    ctx.setLineDash([8, 4]);
    ctx.beginPath();
    ctx.moveTo(padding.left, y500);
    for (let x = padding.left; x <= padding.left + chartWidth; x += 10) {
      const wobble = Math.sin(x * 0.15) * 0.8;
      ctx.lineTo(x, y500 + wobble);
    }
    ctx.stroke();
    ctx.setLineDash([]);

    // Label for 500 line
    ctx.fillStyle = "#16a34a";
    ctx.font = "bold 12px 'Comic Sans MS', cursive, sans-serif";
    ctx.textAlign = "right";
    ctx.fillText("Win at 500", padding.left + chartWidth + 55, y500 + 4);
  }

  // Draw Team A line (blue)
  ctx.strokeStyle = "#2563eb";
  ctx.lineWidth = 3;
  ctx.beginPath();
  dataA.forEach((value, i) => {
    const x = getX(i);
    const y = getY(value);
    const wobble = Math.sin(i * 0.3) * 1.2;
    if (i === 0) ctx.moveTo(x + wobble, y);
    else ctx.lineTo(x + wobble, y);
  });
  ctx.stroke();

  // Draw Team A points
  ctx.fillStyle = "#2563eb";
  dataA.forEach((value, i) => {
    const x = getX(i);
    const y = getY(value);
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  });

  // Draw Team B line (red)
  ctx.strokeStyle = "#dc2626";
  ctx.lineWidth = 3;
  ctx.beginPath();
  dataB.forEach((value, i) => {
    const x = getX(i);
    const y = getY(value);
    const wobble = Math.cos(i * 0.3) * 1.2;
    if (i === 0) ctx.moveTo(x + wobble, y);
    else ctx.lineTo(x + wobble, y);
  });
  ctx.stroke();

  // Draw Team B points
  ctx.fillStyle = "#dc2626";
  dataB.forEach((value, i) => {
    const x = getX(i);
    const y = getY(value);
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fill();
  });

  // Draw axes
  ctx.strokeStyle = "#333";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(padding.left, padding.top);
  ctx.lineTo(padding.left, padding.top + chartHeight);
  ctx.lineTo(padding.left + chartWidth, padding.top + chartHeight);
  ctx.stroke();

  // Y-axis labels
  ctx.fillStyle = "#333";
  ctx.font = "12px 'Comic Sans MS', cursive, sans-serif";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (let i = 0; i <= numHLines; i++) {
    const value = Math.round(maxY - (i / numHLines) * yRange);
    const y = padding.top + (i / numHLines) * chartHeight;
    ctx.fillText(value.toString(), padding.left - 10, y);
  }

  // X-axis labels
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  dataA.forEach((_, i) => {
    if (i % Math.max(1, Math.floor(dataA.length / 10)) === 0 || i === dataA.length - 1) {
      const x = getX(i);
      const label = i === 0 ? "Start" : `R${i}`;
      ctx.fillText(label, x, padding.top + chartHeight + 10);
    }
  });

  // Legend
  const legendX = padding.left + 10;
  const legendY = padding.top + 10;

  // Team A legend
  ctx.fillStyle = "#2563eb";
  ctx.fillRect(legendX, legendY, 20, 3);
  ctx.fillStyle = "#333";
  ctx.font = "bold 14px 'Comic Sans MS', cursive, sans-serif";
  ctx.textAlign = "left";
  ctx.textBaseline = "middle";
  ctx.fillText(getTeamA(), legendX + 25, legendY + 1);

  // Team B legend
  ctx.fillStyle = "#dc2626";
  ctx.fillRect(legendX, legendY + 20, 20, 3);
  ctx.fillStyle = "#333";
  ctx.fillText(getTeamB(), legendX + 25, legendY + 21);
}

function updateStats() {
  if (state.hands.length === 0) {
    const statsSection = $("#stats");
    if (statsSection) statsSection.style.display = "none";
    return;
  }

  const statsSection = $("#stats");
  if (statsSection) statsSection.style.display = "";

  // Update team names in stats headers
  const statsTeamAName = $("#statsTeamAName");
  if (statsTeamAName) statsTeamAName.textContent = getTeamA();
  const statsTeamBName = $("#statsTeamBName");
  if (statsTeamBName) statsTeamBName.textContent = getTeamB();

  // Calculate statistics for Team A
  let bestHandA = -Infinity;
  let worstHandA = Infinity;
  let setsA = 0;
  let totalBagsA = 0;
  let totalScoreA = 0;

  state.hands.forEach((h) => {
    const score = h.scoreA;
    if (score > bestHandA) bestHandA = score;
    if (score < worstHandA) worstHandA = score;
    totalScoreA += score;

    // Count sets (when bid > books and round > 1)
    if (h.round > 1 && !h.blindA && !h.nilA) {
      const bid = parseInt(h.bidA);
      if (!isNaN(bid) && h.booksA < bid) {
        setsA++;
      }
    }
  });

  // Get final bags from state
  totalBagsA = state.bagsA;

  const avgScoreA = state.hands.length > 0 ? (totalScoreA / state.hands.length).toFixed(1) : "0.0";

  // Calculate statistics for Team B
  let bestHandB = -Infinity;
  let worstHandB = Infinity;
  let setsB = 0;
  let totalBagsB = 0;
  let totalScoreB = 0;

  state.hands.forEach((h) => {
    const score = h.scoreB;
    if (score > bestHandB) bestHandB = score;
    if (score < worstHandB) worstHandB = score;
    totalScoreB += score;

    // Count sets (when bid > books and round > 1)
    if (h.round > 1 && !h.blindB && !h.nilB) {
      const bid = parseInt(h.bidB);
      if (!isNaN(bid) && h.booksB < bid) {
        setsB++;
      }
    }
  });

  // Get final bags from state
  totalBagsB = state.bagsB;

  const avgScoreB = state.hands.length > 0 ? (totalScoreB / state.hands.length).toFixed(1) : "0.0";

  // Display stats for Team A
  const statsTeamA = $("#statsTeamA");
  if (statsTeamA) {
    statsTeamA.innerHTML = `
      <p><strong>Best hand:</strong> ${bestHandA === -Infinity ? "N/A" : bestHandA}</p>
      <p><strong>Worst hand:</strong> ${worstHandA === Infinity ? "N/A" : worstHandA}</p>
      <p><strong>Times set:</strong> ${setsA}</p>
      <p><strong>Current bags:</strong> ${totalBagsA}</p>
      <p><strong>Avg score/hand:</strong> ${avgScoreA}</p>
    `;
  }

  // Display stats for Team B
  const statsTeamB = $("#statsTeamB");
  if (statsTeamB) {
    statsTeamB.innerHTML = `
      <p><strong>Best hand:</strong> ${bestHandB === -Infinity ? "N/A" : bestHandB}</p>
      <p><strong>Worst hand:</strong> ${worstHandB === Infinity ? "N/A" : worstHandB}</p>
      <p><strong>Times set:</strong> ${setsB}</p>
      <p><strong>Current bags:</strong> ${totalBagsB}</p>
      <p><strong>Avg score/hand:</strong> ${avgScoreB}</p>
    `;
  }
}

function pushHand(h) {
  state.hands.push(h);
  renderHands();
  updatePills();
  updateDeleteButton();
  updateChart();
  updateStats();
  saveState();
}

function renderHands() {
  const tbody = $("#handsTable tbody");
  tbody.innerHTML = "";
  let runningA = 0,
    runningB = 0,
    runningBagsA = 0,
    runningBagsB = 0;
  state.hands.forEach((h, i) => {
    runningA += h.scoreA;
    runningB += h.scoreB;
    if (h.runningBagsA !== undefined) {
      runningBagsA = h.runningBagsA;
    }
    if (h.runningBagsB !== undefined) {
      runningBagsB = h.runningBagsB;
    }
    const bidA = h.round === 1 ? "-" : h.bidA;
    const bidB = h.round === 1 ? "-" : h.bidB;
    const bagsDisplayA = runningBagsA > 0 ? ` (${runningBagsA})` : "";
    const bagsDisplayB = runningBagsB > 0 ? ` (${runningBagsB})` : "";
    const dealerName = h.dealer || getDealerName(i);

    // Determine color class for Team A books (bid)
    let booksClassA = "";
    if (h.round > 1) {
      const bidANum = parseInt(bidA);
      if (!isNaN(bidANum)) {
        if (h.booksA < bidANum) {
          booksClassA = "books-set"; // Red - team was set
        } else if (h.booksA === bidANum) {
          booksClassA = "books-made"; // Blue - bid equals result
        }
      }
    }

    // Determine color class for Team B books (bid)
    let booksClassB = "";
    if (h.round > 1) {
      const bidBNum = parseInt(bidB);
      if (!isNaN(bidBNum)) {
        if (h.booksB < bidBNum) {
          booksClassB = "books-set"; // Red - team was set
        } else if (h.booksB === bidBNum) {
          booksClassB = "books-made"; // Blue - bid equals result
        }
      }
    }

    // Row for Team A
    const trA = document.createElement("tr");
    trA.className = "row-team-a";
    trA.innerHTML = `<td rowspan="2">${i + 1}</td>
        <td rowspan="2">${dealerName}</td>
        <td class="team-col">A:</td>
        <td class="${booksClassA}">${h.booksA} (${bidA})</td>
        <td>${h.scoreA}</td>
        <td>${runningA}${bagsDisplayA}</td>`;
    tbody.appendChild(trA);

    // Row for Team B
    const trB = document.createElement("tr");
    trB.className = "row-team-b";
    trB.innerHTML = `<td class="team-col">B:</td>
        <td class="${booksClassB}">${h.booksB} (${bidB})</td>
        <td>${h.scoreB}</td>
        <td>${runningB}${bagsDisplayB}</td>`;
    tbody.appendChild(trB);
  });
  updateDeleteButton();
  updateChart();
  updateStats();
}

function deleteLastHand() {
  if (state.hands.length === 0) {
    restartGame();
    return;
  }
  stopConfetti();
  state.hands.pop();
  state.totalA = 0;
  state.totalB = 0;
  state.bagsA = 0;
  state.bagsB = 0;
  state.round = 1;
  state.phase = "books";
  state.gameOver = false;
  state.winnerName = null;
  state.nilA = false;
  state.nilB = false;
  state.nilPrevBidA = 6;
  state.nilPrevBidB = 6;
  const saved = [...state.hands];
  state.hands = [];
  saved.forEach((orig, idx) => {
    const r = idx + 1;
    const bA = orig.bidA === "-" ? 0 : +orig.bidA;
    const bB = orig.bidB === "-" ? 0 : +orig.bidB;
    const {
      scoreA: baseScoreA,
      scoreB: baseScoreB,
      bagA,
      bagB,
      imm,
    } = scoreHand(
      r,
      bA,
      bB,
      +orig.booksA,
      +orig.booksB,
      !!orig.blindA,
      !!orig.blindB,
    );

    let scoreA = baseScoreA;
    let scoreB = baseScoreB;

    // Apply Blind 10 scoring
    if (!!orig.blindA) {
      scoreA = +orig.booksA >= 10 ? 200 : -200;
    }
    if (!!orig.blindB) {
      scoreB = +orig.booksB >= 10 ? 200 : -200;
    }

    state.bagsA += bagA;
    state.bagsB += bagB;

    // Apply bag penalties (only if not a blind bid)
    if (!orig.blindA && state.bagsA >= 10) {
      scoreA -= 100;
      state.bagsA -= 10;
    }
    if (!orig.blindB && state.bagsB >= 10) {
      scoreB -= 100;
      state.bagsB -= 10;
    }

    const immediateLoss =
      r === 1 && imm && (scoreA === -99999 || scoreB === -99999);
    if (!immediateLoss) {
      if (!!orig.nilA) {
        scoreA += +orig.booksA === 0 ? 100 : -100;
      }
      if (!!orig.nilB) {
        scoreB += +orig.booksB === 0 ? 100 : -100;
      }
    }

    const recA =
      immediateLoss && (scoreA === -99999 || scoreB === -99999) ? 0 : scoreA;
    const recB =
      immediateLoss && (scoreA === -99999 || scoreB === -99999) ? 0 : scoreB;
    state.totalA += recA;
    state.totalB += recB;
    state.hands.push({
      round: r,
      bidA: orig.bidA,
      bidB: orig.bidB,
      booksA: orig.booksA,
      booksB: orig.booksB,
      scoreA: recA,
      scoreB: recB,
      blindA: orig.blindA,
      blindB: orig.blindB,
      nilA: orig.nilA,
      nilB: orig.nilB,
      runningBagsA: state.bagsA,
      runningBagsB: state.bagsB,
      dealer: orig.dealer,
    });
  });
  state.round = saved.length + 1;
  state.dealerIndex = saved.length % 4;
  state.phase = state.round === 1 ? "books" : "bids";
  state.lockedBids = false;
  state.blind10A = false;
  state.blind10B = false;
  state.nilA = false;
  state.nilB = false;
  updatePills();
  renderHands();
  togglePhaseUI();
  updateNewGameButtons();
  updateDealerDisplay();
  const actions = document.querySelector(".toolbar:has(#deleteLastBtn)");
  if (actions) actions.style.display = "";
  $("#status").textContent = "Deleted last hand.";
  saveState();
}

function endGame(winnerName) {
  state.gameOver = true;
  state.winnerName = winnerName;
  applyEndGameUI(winnerName);
  saveState();
}

document.addEventListener("DOMContentLoaded", () => {
  const resumeBtn = $("#resumeBtn");
  pendingSnapshot = readSnapshotFromStorage();
  const hasSavedGame =
    pendingSnapshot &&
    pendingSnapshot.state &&
    ((pendingSnapshot.state.started && pendingSnapshot.state.started !== false) ||
      (pendingSnapshot.state.hands?.length || 0) > 0);

  if (resumeBtn) {
    if (hasSavedGame) {
      resumeBtn.style.display = "";
      resumeBtn.onclick = () => {
        applySnapshot(pendingSnapshot);
        resumeBtn.style.display = "none";
      };
      const automation =
        typeof navigator !== "undefined" && navigator.webdriver === true;
      if (!automation) {
        applySnapshot(pendingSnapshot);
        resumeBtn.style.display = "none";
      }
    } else {
      resumeBtn.style.display = "none";
    }
  }

  // Start game
  $("#startBtn").onclick = () => {
    const playerA1 = $("#playerA1").value.trim();
    const playerA2 = $("#playerA2").value.trim();
    const playerB1 = $("#playerB1").value.trim();
    const playerB2 = $("#playerB2").value.trim();
    const errorEl = $("#setupError");
    
    // Validate all 4 player names are provided
    if (!playerA1 || !playerA2 || !playerB1 || !playerB2) {
      if (errorEl) errorEl.style.display = "";
      return;
    }
    
    // Hide error on valid submission
    if (errorEl) errorEl.style.display = "none";
    
    stopConfetti();
    const fresh = createInitialState();
    fresh.started = true;
    fresh.playerA1 = playerA1;
    fresh.playerA2 = playerA2;
    fresh.playerB1 = playerB1;
    fresh.playerB2 = playerB2;
    fresh.dealerIndex = 0;
    Object.assign(state, fresh);
    pendingSnapshot = null;
    $("#setup").style.display = "none";
    $("#game").style.display = "";
    $("#winner").style.display = "none";
    $("#status").textContent = "";
    renderHands();
    updatePills();
    togglePhaseUI();
    updateNewGameButtons();
    updateDealerDisplay();
    $("#bidA").textContent = "6";
    $("#bidB").textContent = "6";
    $("#booksA").textContent = "6";
    $("#booksB").textContent = "7";
    updateBooksSum();
    updateUnbidNote();
    const actions = document.querySelector(".toolbar:has(#deleteLastBtn)");
    if (actions) actions.style.display = "";
    saveState();
    if (resumeBtn) resumeBtn.style.display = "none";
  };

  // Lock bids
  $("#lockBidsBtn").onclick = () => {
    if (state.round === 1) return;
    state.phase = "books";
    state.lockedBids = true;
    const lock = $("#bidsActions");
    if (lock) lock.style.display = "none";
    const baWrap = $("#blind10A")?.closest(".spinner-actions");
    if (baWrap) baWrap.style.display = "none";
    const bbWrap = $("#blind10B")?.closest(".spinner-actions");
    if (bbWrap) bbWrap.style.display = "none";
    const naWrap = $("#nilA")?.closest(".spinner-actions");
    if (naWrap) naWrap.style.display = "none";
    const nbWrap = $("#nilB")?.closest(".spinner-actions");
    if (nbWrap) nbWrap.style.display = "none";
    const note = $("#unbidNote");
    if (note) note.style.display = "none";
    document.querySelectorAll("#bidsRow .spinner").forEach((sp) => {
      sp.classList.add("disabled");
    });
    togglePhaseUI();
    $("#status").textContent = "Bids locked. Now set books.";
    $("#booksA").textContent = "6";
    $("#booksB").textContent = "7";
    updateBooksSum();
    saveState();
  };

  // Blind 10 toggles
  $("#blind10A").onclick = () => {
    state.blind10A = !state.blind10A;
    if (state.blind10A) {
      state.nilA = false;
      state.prevBidA = +$("#bidA").textContent || 6;
      $("#bidA").textContent = "10";
    } else {
      $("#bidA").textContent = String(state.prevBidA || 6);
    }
    applyBlindLocks();
    updateBlindButtons();
    updateNilButtons();
    updateUnbidNote();
    togglePhaseUI();
    saveState();
  };
  $("#blind10B").onclick = () => {
    state.blind10B = !state.blind10B;
    if (state.blind10B) {
      state.nilB = false;
      state.prevBidB = +$("#bidB").textContent || 6;
      $("#bidB").textContent = "10";
    } else {
      $("#bidB").textContent = String(state.prevBidB || 6);
    }
    applyBlindLocks();
    updateBlindButtons();
    updateNilButtons();
    updateUnbidNote();
    togglePhaseUI();
    saveState();
  };

  // Nil toggles
  $("#nilA").onclick = () => {
    if (state.phase !== "bids" || state.lockedBids) return;
    state.nilA = !state.nilA;
    const bidDisplay = $("#bidA");
    if (state.nilA) {
      if (state.blind10A) {
        state.blind10A = false;
        if (bidDisplay)
          bidDisplay.textContent = String(Math.max(state.prevBidA || 6, 4));
      }
      state.nilPrevBidA = +(bidDisplay?.textContent || 6);
      if (bidDisplay) bidDisplay.textContent = "0";
    } else {
      const restored = Math.max(
        state.nilPrevBidA ?? state.prevBidA ?? 6,
        4,
      );
      if (bidDisplay) bidDisplay.textContent = String(restored);
      state.nilPrevBidA = restored;
    }
    applyBlindLocks();
    updateNilButtons();
    updateBlindButtons();
    updateUnbidNote();
    saveState();
  };
  $("#nilB").onclick = () => {
    if (state.phase !== "bids" || state.lockedBids) return;
    state.nilB = !state.nilB;
    const bidDisplay = $("#bidB");
    if (state.nilB) {
      if (state.blind10B) {
        state.blind10B = false;
        if (bidDisplay)
          bidDisplay.textContent = String(Math.max(state.prevBidB || 6, 4));
      }
      state.nilPrevBidB = +(bidDisplay?.textContent || 6);
      if (bidDisplay) bidDisplay.textContent = "0";
    } else {
      const restored = Math.max(
        state.nilPrevBidB ?? state.prevBidB ?? 6,
        4,
      );
      if (bidDisplay) bidDisplay.textContent = String(restored);
      state.nilPrevBidB = restored;
    }
    applyBlindLocks();
    updateNilButtons();
    updateBlindButtons();
    updateUnbidNote();
    saveState();
  };

  // Submit hand
  $("#submitHandBtn").onclick = () => {
    if (state.phase === "bids") return;
    const bidA = +($("#bidA")?.textContent || 0);
    const bidB = +($("#bidB")?.textContent || 0);
    const booksA = +$("#booksA").textContent;
    const booksB = +$("#booksB").textContent;
    if (booksA + booksB !== 13) {
      $("#status").textContent = "Books must sum to 13";
      return;
    }
    const {
      scoreA: baseScoreA,
      scoreB: baseScoreB,
      bagA,
      bagB,
      imm,
    } = scoreHand(
      state.round,
      bidA,
      bidB,
      booksA,
      booksB,
      state.blind10A,
      state.blind10B,
    );

    let scoreA = baseScoreA;
    let scoreB = baseScoreB;

    if (state.blind10A) {
      scoreA = booksA >= 10 ? 200 : -200;
    }
    if (state.blind10B) {
      scoreB = booksB >= 10 ? 200 : -200;
    }
    state.bagsA += bagA;
    state.bagsB += bagB;

    console.log(
      `Before bag penalty: scoreA=${scoreA}, bagsA=${state.bagsA}, blind10A=${state.blind10A}`,
    );
    if (!state.blind10A && state.bagsA >= 10) {
      scoreA -= 100;
      state.bagsA -= 10;
      console.log(`After bag penalty: scoreA=${scoreA}, bagsA=${state.bagsA}`);
    }
    if (!state.blind10B && state.bagsB >= 10) {
      scoreB -= 100;
      state.bagsB -= 10;
    }
    const immediateLoss =
      state.round === 1 && imm && (scoreA === -99999 || scoreB === -99999);
    if (immediateLoss) {
      const loser = scoreA === -99999 ? getTeamA() : getTeamB();
      const winner = scoreA === -99999 ? getTeamB() : getTeamA();
      const priorNilA = state.nilA;
      const priorNilB = state.nilB;
      const currentDealer = getDealerName(state.dealerIndex);
      pushHand({
        round: state.round,
        bidA: "-",
        bidB: "-",
        booksA,
        booksB,
        scoreA: scoreA === -99999 ? 0 : scoreA,
        scoreB: scoreB === -99999 ? 0 : scoreB,
        blindA: state.blind10A,
        blindB: state.blind10B,
        nilA: priorNilA,
        nilB: priorNilB,
        runningBagsA: state.bagsA,
        runningBagsB: state.bagsB,
        dealer: currentDealer,
      });
      state.nilA = false;
      state.nilB = false;
      updateNilButtons();
      $("#status").textContent = `${loser} loses immediately.`;
      endGame(winner);
      return;
    }
    if (state.nilA) {
      scoreA += booksA === 0 ? 100 : -100;
    }
    if (state.nilB) {
      scoreB += booksB === 0 ? 100 : -100;
    }
    state.totalA += scoreA;
    state.totalB += scoreB;
    const priorNilA = state.nilA;
    const priorNilB = state.nilB;
    const currentDealer = getDealerName(state.dealerIndex);
    pushHand({
      round: state.round,
      bidA: state.round === 1 ? "-" : bidA,
      bidB: state.round === 1 ? "-" : bidB,
      booksA,
      booksB,
      scoreA,
      scoreB,
      blindA: state.blind10A,
      blindB: state.blind10B,
      nilA: priorNilA,
      nilB: priorNilB,
      runningBagsA: state.bagsA,
      runningBagsB: state.bagsB,
      dealer: currentDealer,
    });
    state.blind10A = false;
    state.blind10B = false;
    state.nilA = false;
    state.nilB = false;
    state.lockedBids = false;
    updateBlindButtons();
    updateNilButtons();
    const winner = checkWin();
    if (winner) {
      endGame(winner);
      return;
    }
    state.round++;
    state.dealerIndex = (state.dealerIndex + 1) % 4;
    state.phase = "bids";
    updatePills();
    togglePhaseUI();
    updateDealerDisplay();
    $("#bidA").textContent = "6";
    $("#bidB").textContent = "6";
    updateUnbidNote();
    $("#booksA").textContent = "6";
    $("#booksB").textContent = "7";
    updateBooksSum();
    $("#status").textContent = "Next round: set bids first.";
    saveState();
  };

  // Other buttons
  $("#deleteLastBtn").onclick = () => deleteLastHand();
  const newGameBtn = $("#newGameBtn");
  if (newGameBtn) newGameBtn.onclick = restartGame;
  const newGameBtnMain = $("#newGameBtnMain");
  if (newGameBtnMain) newGameBtnMain.onclick = restartGame;

  wireArrowButtons();
  updateBlindButtons();
  updateNilButtons();
  updateNewGameButtons();
  updateUnbidNote();
  updateBooksSum();
});

// Add window resize handler to redraw chart
window.addEventListener("resize", () => {
  if (state.hands.length > 0) {
    updateChart();
  }
});
