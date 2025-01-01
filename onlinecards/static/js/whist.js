function joinGame(websocket, gameID, userID) {
  websocket.onopen = () => {
    let event = {
      type: "join",
      gameID: gameID,
      userID: userID,
    };
    websocket.send(JSON.stringify(event));
  }
}

function addMessages(node, ...messages) {
  for (const message of messages) {
    let p = document.createElement("p");
    if (message.includes("undefined")) {
      continue;
    }
    p.innerHTML = message;
    p.style.margin = "0";
    node.appendChild(p);
  }
}

function rotatePlayers(event) {
  // Rotate array in place so that the current player is at the index 0
  // Future code can use this fact to position players as it wishes
  let currentPlayer = event.players[event.current_user]
  if (currentPlayer == undefined) {
    return;
  }
  while (event.players[0] != currentPlayer) {
    let rem = event.players.shift();
    event.players.push(rem);
    // Ensure cards played point at correct player
    try {
      rem = event.trick.played.shift()
      event.trick.played.push(rem)
    } catch {
    }
    // Ensure index still points at correct player
    event.dealer = event.dealer - 1
    if (event.dealer < 0) {
      event.dealer += event.players.length
    }
  }
}

function renderTableAndPlayers(event) {
  const tableTemplate = document.getElementById("table_template");
  const playerTemplate = document.getElementById("player_template");
  const linebreak = document.getElementById("flex_linebreak_template");

  let table = tableTemplate.content.cloneNode(true).querySelector(".table");
  table.id = "table";

  let players = [];
  for (let i = 0; i < 4; i++) {
    let fragment = playerTemplate.content.cloneNode(true);
    let wrapper = fragment.querySelector(".player");
    wrapper.id = "player" + i;
    wrapper.style.flexFlow = "row wrap";
    players.push(wrapper);
  }

  // Players should be ordered clockwise around the table
  //          player 2
  // player 1          player 3
  //          player 0
  // The current user (player 0) should be at the bottom with the table 'infront' of them
  let html = [
    players[2],
    linebreak.content.cloneNode(true),
    players[1], table, players[3],
    linebreak.content.cloneNode(true),
    players[0]
  ];

  content.replaceChildren(...html);
}

function renderTableInfoBox(event) {
  let table = document.getElementById("table");
  let infoBox = table.querySelector(".info_box");

  let messages = []
  // I am not sure if this is the place where the code should branch. The
  // alternative is to have separate methods for rendering a waiting scene and a
  // normal gameplay scene, as I do currently, and have these either call
  // different methods or pass arguments to the methods they call (such as this
  // one) that changes what is outputted, rather than the method deciding
  // itself.
  if (event.type === "waiting") {
    messages = [
      "Waiting for players to join...",
      `${event.no_players} out of ${event.players_required}`,
    ];
  } else {
    let map = {
      "C": "Clubs",
      "D": "Diamonds",
      "H": "Hearts",
      "S": "Spades",
    };
    let trump_suit = map[event.trump_suit]
    messages = [`Trump Suit: ${trump_suit}`];
  }
  addMessages(infoBox, ...messages);
}

function renderPlayerInfoBoxes(event) {
  for (let i in event.players) {
    let infoBox = document.createElement("div");
    infoBox.style.margin = "0.5em";
    infoBox.className += "info_box";

    let player = event.players[i]
    addMessages(
      infoBox,
      `<strong>${player.username}</strong>`,
      `Bid: ${player.bid}`,
      `Tricks Won: ${player.tricks_won}`
    );
    if (event.players[event.dealer] === player) {
      addMessages(
        infoBox,
        `Dealer`
      )
    }
    const wrapper = document.getElementById("player" + i);
    const hand = wrapper.querySelector(".hand");
    wrapper.insertBefore(infoBox, hand);
  }
}

function getCardHTML(cardName) {
  const wrapper = document.createElement("div");
  let url;
  if (cardName === "") {
    url = `/static/cards-fancy/2B.svg`;
  } else {
    url = `/static/cards-fancy/${cardName}.svg`;
  }
  fetch(url).then((response) => {
    // Add error handling here later
    return response.text();
  }).then((text) => {
    // The card svg has an approx. aspect ratio of 100:72
    wrapper.style.width = `${5 * 0.72}em`;
    wrapper.style.height = "5em";
    wrapper.innerHTML = text;
    let name = document.createElement("p");
    name.style.display = "none";
    name.className += "name";
    name.innerHTML = cardName;
    wrapper.appendChild(name);
  })
  return wrapper;
}

function sortHand(hand) {
  let handCopy = [];
  // Face down cards are first
  [ "", "C", "D", "H", "S" ].forEach((suit) => {
    let sorted = hand
      .filter((el) => {
        // Card if face down
        if (el === "" && suit === "") {return true}
        return el[1] === suit
      })
      .sort((a, b) => {
        if (a === "" || b === "") { return 0 }
        let valueMap = {
          "T": 10,
          "J": 11,
          "Q": 12,
          "K": 13,
          "A": 14,
        };
        const values = [];
        [a, b].forEach((num) => {
          let char = num[0];
          num = Number(char);
          if (Number.isNaN(num)) { num = valueMap[char] }
          values.push(num)
        })
        return values[0] - values[1];
      });
    handCopy.push(...sorted);
  });
  return handCopy
}

function renderHands(event) {
  const content = document.getElementById("content");
  const linebreak = document.createElement("div");
  linebreak.className += "flex_linebreak";
  linebreak.style.marginBottom = "1em";
  content.appendChild(linebreak);
  for (let [i, player] of event.players.entries()) {
    if (player.hand == undefined) {
      continue;
    }
    player.hand = sortHand(player.hand);
    const playerDiv = document.getElementById("player" + i)
    const handWrapper = playerDiv.querySelector(".hand");
    const linebreak = document.createElement("div");
    linebreak.className += "flex_linebreak";
    playerDiv.insertBefore(linebreak, handWrapper);
    for (let [j, card] of player.hand.entries()) {
      cardHTML = getCardHTML(card, j);
      if (j != 0) {
        cardHTML.style.marginLeft = `-${5 * 0.72 * 0.8}em`;
      }
      handWrapper.appendChild(cardHTML);
    }
  }
}

function renderTrick(event) {
  if (event.trick === undefined) {
    return
  }
  if (event.trick.played === undefined) {
    return
  }
  let offset = 40;
  const table = document.getElementById("table");
  const communityCards = table.querySelector(".community_cards");
  communityCards.style.marginTop = `${offset + 5}px`
  // Cards are rendered in the same order as players
  //        card 2
  // card 1        card 3
  //        card 0
  let translations = [ [0, offset], [-offset, 0], [0, -offset], [offset, 0] ];
  let absolute = false;
  for (let [i, card] of event.trick.played.entries()) {
    if (card === null) {
      continue;
    }
    cardHTML = getCardHTML(card);
    let [x, y] = translations[i];
    cardHTML.style.transform = `translate(${x}px, ${y}px)`;
    cardHTML.style.transform += `rotate(${90 * (i + 2)}deg)`;
    // First card must be `position: relative` and all afterwards must be `position: absolute`
    if (!absolute) {
      cardHTML.style.position = "relative";
      absolute = true;
    } else {
      cardHTML.style.position = "absolute";
    }
    communityCards.appendChild(cardHTML);
  }
}

function renderGameState(event) {
  rotatePlayers(event);
  renderTableAndPlayers(event);
  renderTableInfoBox(event);
  renderPlayerInfoBoxes(event);
  renderHands(event);
  renderTrick(event);
}

function renderWaiting(event) {
  rotatePlayers(event);
  renderTableAndPlayers(event);
  renderTableInfoBox(event);
  renderPlayerInfoBoxes(event);
}

function getCard(event, websocket) {
  const player = document.getElementById("player0");
  player.style.justifyContent = "center";
  const hand = player.querySelector(".hand");
  hand.querySelectorAll("div").forEach((card, j) => {
    card.style.marginLeft = 0;
    card.onclick = () => {
      let nameHTML = card.querySelector(".name");
      let name = nameHTML.innerHTML;
      if (event.choice.options.includes(name)) {
        let response = {
          type: "choice",
          gameID: gameID,
          userID: userID,
          choice: {
            type: "play_card",
            chosen: name,
          },
        }
        websocket.send(JSON.stringify(response));
      }
    }
  });
}

function renderChoice(event, websocket) {
  if (event.choice.type === "play_card") {
    getCard(event, websocket);
  }
}

function recieveMessages(websocket) {
  websocket.onmessage = ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "game_state":
        renderGameState(event);
        break;
      case "waiting":
        renderWaiting(event);
        break;
      case "choice":
        renderChoice(event, websocket);
        break;
      case "error":
        console.log(event.message);
        break;
      default:
        console.log(`Unsupported event type '${event.type}'`)
        break;
    }
  }
}

function copyLink(event) {
  event.preventDefault();
  let game_link = document.getElementById("game_link");
  let clipboard = navigator.clipboard;
  if (clipboard != undefined) {
    clipboard.writeText(game_link.href);
    game_link.style.setProperty("--message", '"Copied"');
  } else {
    game_link.style.setProperty("--message", '"Error"');
  }
}

const gameID = document.getElementById("gameID").innerHTML;
const userID = document.cookie
  .split("; ")
  .find((cookie) => cookie.startsWith("userID="))
  // find may return nothing so the `?` means undefined is returned rather than an error
  // split returns an array where we want the second item, right of the `=`
  ?.split("=")[1];

function bindFunctions() {
  // localhost needs to be replaced with hostname in production so this requires a better solution
  const websocket = new WebSocket("ws://localhost:8001/");

  joinGame(websocket, gameID, userID);
  recieveMessages(websocket);

  document.getElementById("game_link").onclick = copyLink;
}

bindFunctions();
