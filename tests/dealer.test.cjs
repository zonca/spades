const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const { test } = require("node:test");
const vm = require("node:vm");

const source = readFileSync(resolve(__dirname, "../script.js"), "utf8");
const dealers = ["Alice", "Bob", "Alex", "Beth"];

function loadGame(handCount) {
  const elements = new Map();
  let initialize;
  const context = vm.createContext({
    document: {
      addEventListener(event, callback) {
        if (event === "DOMContentLoaded") initialize = callback;
      },
      querySelectorAll() { return []; },
      querySelector(selector) {
        if (!elements.has(selector)) {
          elements.set(selector, {
            style: {}, textContent: "",
            classList: { add() {}, remove() {}, toggle() {} },
            closest() { return this; },
          });
        }
        return elements.get(selector);
      },
    },
    window: { addEventListener() {}, localStorage: { getItem() { return null; } } },
  });
  vm.runInContext(source, context);
  // Isolate the deletion logic and real dealer display from unrelated UI effects.
  vm.runInContext(`
    renderHands = updatePills = togglePhaseUI = updateNewGameButtons = saveState = () => {};
    Object.assign(state, {
      playerA1: "Alice", playerB1: "Bob", playerA2: "Alex", playerB2: "Beth",
      started: true,
    });
  `, context);
  context.handCount = handCount;
  vm.runInContext(`
    state.hands = Array.from({ length: handCount }, (_, index) => ({
      round: index + 1,
      bidA: index === 0 ? "-" : 6,
      bidB: index === 0 ? "-" : 7,
      booksA: 6, booksB: 7,
      dealer: getDealerName(index),
    }));
    state.round = handCount + 1;
    state.dealerIndex = handCount % 4;
  `, context);
  return {
    run: (code) => vm.runInContext(code, context),
    initialize: () => initialize(),
    dealerDisplay: elements,
  };
}

// Issue #15: deleting the latest hand must restore its dealer, including wraparound.
for (let handCount = 1; handCount <= 9; handCount++) {
  test(`deleting hand ${handCount} restores its dealer`, () => {
    const game = loadGame(handCount);
    game.run("deleteLastHand()");

    assert.equal(game.run("state.round"), handCount);
    assert.equal(game.run("state.dealerIndex"), (handCount - 1) % 4);
    assert.equal(
      game.dealerDisplay.get("#dealerDisplay").textContent,
      `🂡 Dealer: ${dealers[(handCount - 1) % 4]}`,
    );
    assert.deepEqual(
      Array.from(game.run("state.hands.map(hand => hand.dealer)")),
      Array.from({ length: handCount - 1 }, (_, index) => dealers[index % 4]),
    );
  });
}

test("repeated deletions restore the dealer all the way to round one", () => {
  const game = loadGame(6);
  for (let remaining = 5; remaining >= 0; remaining--) {
    game.run("deleteLastHand()");
    assert.equal(game.run("state.dealerIndex"), remaining % 4);
    assert.equal(game.run("getDealerName(state.dealerIndex)"), dealers[remaining % 4]);
  }
});

test("submitting a locked hand updates the undo label to match its action", () => {
  const game = loadGame(1);
  game.initialize();
  game.run(`
    pushHand = hand => { state.hands.push(hand); updateDeleteButton(); };
    state.phase = "bids";
    $("#bidA").textContent = "6";
    $("#bidB").textContent = "7";
    $("#booksA").textContent = "6";
    $("#booksB").textContent = "7";
    $("#lockBidsBtn").onclick();
  `);
  assert.equal(game.dealerDisplay.get("#deleteLastBtn").textContent, "Unlock Bid");
  game.run('$("#submitHandBtn").onclick()');
  assert.equal(game.run("state.round"), 3);
  assert.equal(game.run("state.dealerIndex"), 2);
  assert.equal(game.dealerDisplay.get("#deleteLastBtn").textContent, "Delete Last Hand");
  game.run('$("#deleteLastBtn").onclick()');
  assert.equal(game.run("state.round"), 2);
  assert.equal(game.run("state.dealerIndex"), 1);
  assert.equal(game.run("state.hands.length"), 1);
});

for (let handCount = 1; handCount <= 4; handCount++) {
  test(`unlocking bids in round ${handCount + 1} preserves the dealer and history`, () => {
    const game = loadGame(handCount);
    const history = game.run("JSON.stringify(state.hands)");
    for (let attempt = 0; attempt < 2; attempt++) {
      game.run(`
        state.lockedBids = true;
        state.phase = "books";
        updateDealerDisplay();
        unlockBids();
      `);
      assert.equal(game.run("state.dealerIndex"), handCount % 4);
      assert.equal(game.run("state.round"), handCount + 1);
      assert.equal(game.run("JSON.stringify(state.hands)"), history);
      assert.equal(game.run("state.lockedBids"), false);
      assert.equal(game.run("state.phase"), "bids");
      assert.equal(
        game.dealerDisplay.get("#dealerDisplay").textContent,
        `🂡 Dealer: ${dealers[handCount % 4]}`,
      );
    }
  });
}
