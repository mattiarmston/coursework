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
  addMessages(table, ...messages);
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
    const wrapper = document.getElementById("player" + i);
    const hand = wrapper.querySelector(".hand");
    wrapper.insertBefore(infoBox, hand);
  }
}

function getCardHTML(cardName, i) {
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
    if (i != 0) {
      wrapper.style.marginLeft = `-${5 * 0.72 * 0.8}em`;
    }
    wrapper.innerHTML = text;
  })
  return wrapper;
}

function renderHands(event) {
  const content = document.getElementById("content");
  const linebreak = document.createElement("div");
  linebreak.className += "flex_linebreak";
  linebreak.style.marginBottom = "1em";
  content.appendChild(linebreak);
  for (let i in event.players) {
    player = event.players[i];
    if (player.hand == undefined) {
      continue;
    }
    const playerDiv = document.getElementById("player" + i)
    const handWrapper = playerDiv.querySelector(".hand");
    const linebreak = document.createElement("div");
    linebreak.className += "flex_linebreak";
    playerDiv.insertBefore(linebreak, handWrapper);
    let j = 0;
    for (let card of player.hand) {
      handWrapper.appendChild(getCardHTML(card, j));
      j++;
    }
  }
}

function renderGameState(event) {
  rotatePlayers(event);
  renderTableAndPlayers(event);
  renderTableInfoBox(event);
  renderPlayerInfoBoxes(event);
  renderHands(event);
}

function renderWaiting(event) {
  rotatePlayers(event);
  renderTableAndPlayers(event);
  renderTableInfoBox(event);
  renderPlayerInfoBoxes(event);
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

function bindFunctions() {
  // localhost needs to be replaced with hostname in production so this requires a better solution
  const websocket = new WebSocket("ws://localhost:8001/");
  const gameID = document.getElementById("gameID").innerHTML;
  const userID = document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith("userID="))
    // find may return nothing so the `?` means undefined is returned rather than an error
    // split returns an array where we want the second item, right of the `=`
    ?.split("=")[1];

  joinGame(websocket, gameID, userID);
  recieveMessages(websocket);

  document.getElementById("game_link").onclick = copyLink;
}

bindFunctions();
