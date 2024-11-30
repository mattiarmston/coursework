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

function renderTable(event) {
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
    if (1 <= i && i <= 2) {
      wrapper.style.flexDirection = "column";
    } else {
      wrapper.style.flexDirection = "row";
    }
    players.push(wrapper);
  }

  let html = [
    players[0],
    linebreak.content.cloneNode(true),
    players[1], table, players[2],
    linebreak.content.cloneNode(true),
    players[3]
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
    let wrapper = document.getElementById("player" + i);
    wrapper.appendChild(infoBox);
  }
}

function renderGameState(event) {
  renderTable(event);
  renderTableInfoBox(event);
  renderPlayerInfoBoxes(event);
}

function renderWaiting(event) {
  renderTable(event);
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
