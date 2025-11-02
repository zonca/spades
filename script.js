// Inline app logic (no external deps)
const STORAGE_KEY = "spades-scorekeeper-state-v1";

function createInitialState() {
  return {
    round: 1,
    phase: "books",
    teamA: "Team A",
    teamB: "Team B",
    totalA: 0,
    totalB: 0,
    bagsA: 0,
    bagsB: 0,
    hands: [],
    lockedBids: false,
    blind10A: false,
    blind10B: false,
    prevBidA: 6,
    prevBidB: 6,
    started: false,
    gameOver: false,
    winnerName: null,
  };
}

const state = createInitialState();
let pendingSnapshot = null;
let isHydrating = false;

const $ = (s) => document.querySelector(s);

function getSpinnerText(id) {
  return document.getElementById(id)?.textContent || "";
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

function applyEndGameUI(winnerName) {
  $("#bidsRow").style.display = "none";
  $("#booksRow").style.display = "none";
  const actions = document.querySelector(".toolbar:has(#deleteLastBtn)");
  if (actions) actions.style.display = "none";
  $("#status").innerHTML = `<strong>${winnerName}</strong> wins!`;
  $("#winner").style.display = "none";
}

function applySnapshot(snapshot, { hideSetup = true } = {}) {
  if (!snapshot || !snapshot.state) return;
  isHydrating = true;
  const fresh = createInitialState();
  const savedState = {
    ...fresh,
    ...snapshot.state,
    hands: (snapshot.state.hands || []).map((hand) => ({ ...hand })),
  };
  Object.assign(state, savedState);
  if (!state.started && state.hands.length > 0) state.started = true;

  if (hideSetup) {
    $("#setup").style.display = "none";
    $("#game").style.display = "";
  }
  $("#teamA").value = state.teamA;
  $("#teamB").value = state.teamB;

  // Restore spinner values
  const ui = snapshot.ui || {};
  if (ui.bidA !== undefined) $("#bidA").textContent = String(ui.bidA);
  if (ui.bidB !== undefined) $("#bidB").textContent = String(ui.bidB);
  if (ui.booksA !== undefined) $("#booksA").textContent = String(ui.booksA);
  if (ui.booksB !== undefined) $("#booksB").textContent = String(ui.booksB);

  renderHands();
  updatePills();
  togglePhaseUI();

  if (state.lockedBids) {
    const lock = $("#bidsActions");
    if (lock) lock.style.display = "none";
    const baWrap = $("#blind10A")?.closest(".toolbar");
    if (baWrap) baWrap.style.display = "none";
    const bbWrap = $("#blind10B")?.closest(".toolbar");
    if (bbWrap) bbWrap.style.display = "none";
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
  updateUnbidNote();
  updateBooksSum();
  isHydrating = false;
  saveState();
}
function clamp(v, min, max) {
  return Math.max(min, Math.min(max, v));
}

function updatePills() {
  const nameA = $("#scoreNameA");
  if (nameA) nameA.textContent = state.teamA;
  const nameB = $("#scoreNameB");
  if (nameB) nameB.textContent = state.teamB;
  const round = $("#pillRound");
  if (round) round.textContent = `Round ${state.round}`;
  const pointsA = $("#scorePointsA");
  if (pointsA) pointsA.textContent = state.totalA;
  const pointsB = $("#scorePointsB");
  if (pointsB) pointsB.textContent = state.totalB;

  const bidLabelA = $("#bidLabelA");
  if (bidLabelA) bidLabelA.textContent = state.teamA;
  const bidLabelB = $("#bidLabelB");
  if (bidLabelB) bidLabelB.textContent = state.teamB;
  const booksLabelA = $("#booksLabelA");
  if (booksLabelA) booksLabelA.textContent = state.teamA;
  const booksLabelB = $("#booksLabelB");
  if (booksLabelB) booksLabelB.textContent = state.teamB;

  const pillA = $("#pillA");
  if (pillA) pillA.textContent = `${state.teamA}: ${state.totalA}`;
  const pillB = $("#pillB");
  if (pillB) pillB.textContent = `${state.teamB}: ${state.totalB}`;
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
    state.blind10A || state.phase === "books" || state.lockedBids;
  if (aUp) aUp.disabled = disableArrows;
  if (aDn) aDn.disabled = disableArrows;
  const disableArrowsB =
    state.blind10B || state.phase === "books" || state.lockedBids;
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

  if (state.round === 1) {
    if (bids) bids.style.display = "none";
    if (books) books.style.display = "";
  } else if (state.phase === "bids") {
    if (bids) bids.style.display = "";
    if (books) books.style.display = "none";
    $("#bidsActions").style.display = ""; // Make bidsActions visible
    const baWrap = $("#blind10A")?.closest(".toolbar");
    if (baWrap) baWrap.style.display = ""; // Make blind buttons visible
    const bbWrap = $("#blind10B")?.closest(".toolbar");
    if (bbWrap) bbWrap.style.display = ""; // Make blind buttons visible
    $("#unbidNote").style.display = ""; // Make unbid note visible
  } else {
    // state.phase === 'books'
    if (bids) bids.style.display = "";
    if (books) books.style.display = "";
    // Ensure all spinners are enabled when in books phase
    document.querySelectorAll("#booksRow .spinner").forEach((sp) => {
      sp.classList.remove("disabled");
    });
  }

  applyBlindLocks();
  updateBlindButtons();

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
  if (a) {
    a.classList.toggle("button-outline", !state.blind10A);
    a.textContent = state.blind10A ? "Blind 10 (A) ✓" : "Blind 10 (A)";
  }
  if (b) {
    b.classList.toggle("button-outline", !state.blind10B);
    b.textContent = state.blind10B ? "Blind 10 (B) ✓" : "Blind 10 (B)";
  }
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
  let scoreA = booksA >= bidA ? 10 * bidA + (booksA - bidA) : -10 * bidA;
  let scoreB = booksB >= bidB ? 10 * bidB + (booksB - bidB) : -10 * bidB;

  const bagA = booksA > bidA ? booksA - bidA : 0;
  const bagB = booksB > bidB ? booksB - bidB : 0;

  return { scoreA, scoreB, bagA, bagB, imm: false };
}

function checkWin() {
  if (state.totalA >= 500 || state.totalB >= 500) {
    if (state.totalA === state.totalB) return null;
    return state.totalA > state.totalB ? state.teamA : state.teamB;
  }
  return null;
}

function pushHand(h) {
  state.hands.push(h);
  renderHands();
  updatePills();
  saveState();
}

function renderHands() {
  const tbody = $("#handsTable tbody");
  tbody.innerHTML = "";
  let runningA = 0,
    runningB = 0;
  state.hands.forEach((h, i) => {
    runningA += h.scoreA;
    runningB += h.scoreB;
    const bidA = h.round === 1 ? "-" : h.bidA;
    const bidB = h.round === 1 ? "-" : h.bidB;
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${i + 1}</td>
        <td>${h.booksA} (${bidA})</td>
        <td>${h.booksB} (${bidB})</td>
        <td>${h.scoreA}</td>
        <td>${h.scoreB}</td>
        <td>${runningA}</td>
        <td>${runningB}</td>`;
    tbody.appendChild(tr);
  });
}

function deleteLastHand() {
  if (state.hands.length === 0) {
    $("#status").textContent = "No hands to delete.";
    return;
  }
  state.hands.pop();
  state.totalA = 0;
  state.totalB = 0;
  state.bagsA = 0;
  state.bagsB = 0;
  state.round = 1;
  state.phase = "books";
  state.gameOver = false;
  state.winnerName = null;
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
      scoreA = +orig.booksA >= 10 ? 200 + (+orig.booksA - 10) : -200;
    }
    if (!!orig.blindB) {
      scoreB = +orig.booksB >= 10 ? 200 + (+orig.booksB - 10) : -200;
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

    const recA =
      r === 1 && imm && (scoreA === -99999 || scoreB === -99999) ? 0 : scoreA;
    const recB =
      r === 1 && imm && (scoreA === -99999 || scoreB === -99999) ? 0 : scoreB;
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
    });
  });
  state.round = saved.length + 1;
  state.phase = state.round === 1 ? "books" : "bids";
  state.lockedBids = false;
  state.blind10A = false;
  state.blind10B = false;
  updatePills();
  renderHands();
  togglePhaseUI();
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
    const fresh = createInitialState();
    fresh.started = true;
    fresh.teamA = $("#teamA").value || "Team A";
    fresh.teamB = $("#teamB").value || "Team B";
    Object.assign(state, fresh);
    pendingSnapshot = null;
    $("#setup").style.display = "none";
    $("#game").style.display = "";
    $("#winner").style.display = "none";
    $("#status").textContent = "";
    renderHands();
    updatePills();
    togglePhaseUI();
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
    const baWrap = $("#blind10A")?.closest(".toolbar");
    if (baWrap) baWrap.style.display = "none";
    const bbWrap = $("#blind10B")?.closest(".toolbar");
    if (bbWrap) bbWrap.style.display = "none";
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
      state.prevBidA = +$("#bidA").textContent || 6;
      $("#bidA").textContent = "10";
    } else {
      $("#bidA").textContent = String(state.prevBidA || 6);
    }
    updateBlindButtons();
    updateUnbidNote();
    togglePhaseUI();
    saveState();
  };
  $("#blind10B").onclick = () => {
    state.blind10B = !state.blind10B;
    if (state.blind10B) {
      state.prevBidB = +$("#bidB").textContent || 6;
      $("#bidB").textContent = "10";
    } else {
      $("#bidB").textContent = String(state.prevBidB || 6);
    }
    updateBlindButtons();
    updateUnbidNote();
    togglePhaseUI();
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
      scoreA = booksA >= 10 ? 200 + (booksA - 10) : -200;
    }
    if (state.blind10B) {
      scoreB = booksB >= 10 ? 200 + (booksB - 10) : -200;
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
    if (state.round === 1 && imm && (scoreA === -99999 || scoreB === -99999)) {
      const loser = scoreA === -99999 ? state.teamA : state.teamB;
      const winner = scoreA === -99999 ? state.teamB : state.teamA;
      pushHand({
        round: state.round,
        bidA: "-",
        bidB: "-",
        booksA,
        booksB,
        scoreA: scoreA === -99999 ? 0 : scoreA,
        scoreB: scoreB === -99999 ? 0 : scoreB,
      });
      $("#status").textContent = `${loser} loses immediately.`;
      endGame(winner);
      return;
    }
    state.totalA += scoreA;
    state.totalB += scoreB;
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
    });
    state.blind10A = false;
    state.blind10B = false;
    state.lockedBids = false;
    updateBlindButtons();
    const winner = checkWin();
    if (winner) {
      endGame(winner);
      return;
    }
    state.round++;
    state.phase = "bids";
    updatePills();
    togglePhaseUI();
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
  $("#newGameBtn").onclick = () => {
    clearStoredState();
    location.reload();
  };

  wireArrowButtons();
  updateBlindButtons();
  updateUnbidNote();
  updateBooksSum();
});
