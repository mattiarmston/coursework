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

function renderGameState(event) {
  const tableTemplate = document.getElementById("table");
  const playerTemplate = document.getElementById("player");
  const linebreak = document.getElementById("flex_linebreak");
  let table = tableTemplate.cloneNode(true);

  let players = [];
  for (let i in event.players) {
    let player = event.players[i]
    let wrapper = playerTemplate.cloneNode(true);
    if (1 <= i && i <= 2) {
      console.log(i + "column");
      wrapper.style.flexDirection = "column";
    } else {
      console.log(i + "row");
      wrapper.style.flexDirection = "row";
    }

    let infoBox = document.createElement("div");
    infoBox.style.margin = "0.5em";
    let username = document.createElement("p");
    username.innerHTML = `Username: ${player.username}`;
    username.style.margin = "0";
    infoBox.appendChild(username);
    wrapper.appendChild(infoBox);

    players.push(wrapper);
  }

  let html = [
    players[0],
    linebreak.cloneNode(true),
    players[1], table, players[2],
    linebreak.cloneNode(true),
    players[3]
  ];

  content.replaceChildren(...html);
}

function renderWaiting(event) {
  const content = document.getElementById("content");
  const messages = [
    "Waiting for players to join...",
    `${event.players} out of ${event.players_required}`,
  ];
  let html = [];
  for (const message of messages) {
    let p = document.createElement("p");
    p.innerHTML = message;
    html.push(p);
  }

  let center = document.createElement("div");
  center.className += "center";
  center.replaceChildren(...html);
  content.replaceChildren(center);
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
