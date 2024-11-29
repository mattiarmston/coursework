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
  console.log(event);
  let messages = []
  for (player of event.players) {
    messages.push("username: " + player.username)
  }

  let html = [];
  for (const message of messages) {
    let p = document.createElement("p");
    p.innerHTML = message;
    html.push(p);
  }

  let center = document.createElement("div");
  center.className += "center";
  /*
  center.replaceChildren(...html);
  content.appendChild(center);
  */
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
