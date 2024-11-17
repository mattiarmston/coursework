function setUsername(form, input, main) {
  main.style.display = "none";
  form.onsubmit = (e) => {
    e.preventDefault();
    username = input.value;
    form.style.display = "none";
    main.style.display = "unset";
  }
}

function joinGame(websocket, gameID) {
  websocket.onopen = () => {
    let event = { type: "join", gameID: gameID};
    websocket.send(JSON.stringify(event));
  }
}

function recieveMessages(websocket) {
  websocket.onmessage = ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "waiting":
        render_waiting(event);
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

function render_waiting(event) {
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
  content.replaceChildren(...html);
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

var username;

function bindFunctions() {
  const username_form = document.getElementById("username_form");
  const username_input = document.getElementById("username_input");
  const main = document.getElementById("main");
  // localhost needs to be replaced with hostname in production so this requires a better solution
  const websocket = new WebSocket("ws://localhost:8001/");
  const gameID = document.getElementById("gameID").innerHTML;
  const config = document.getElementById("config").innerHTML;

  setUsername(username_form, username_input, main);
  joinGame(websocket, gameID);
  recieveMessages(websocket);

  document.getElementById("game_link").onclick = copyLink;
}

bindFunctions();
