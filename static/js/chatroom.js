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

function sendMessages(form, websocket, gameID) {
  form.onsubmit = (e) => {
    e.preventDefault()
    let msg_input = document.getElementById("msg_input");
    const message = msg_input.value;
    msg_input.value = "";
    const event = {
      type: "message",
      gameID: gameID,
      username: username,
      message: message,
    };
    websocket.send(JSON.stringify(event));
  }
}

function renderGameState(msg_list, event) {
  let message_list = event.message_list
  let paragraphs = []
  for (message of message_list) {
    let paragraph = document.createElement("p");
    paragraph.innerHTML = message.username + ": " + message.message;
    paragraphs.push(paragraph);
  }
  msg_list.replaceChildren(...paragraphs);
}

function renderUpdate(msg_list, event) {
  let message = event.message;
  let paragraph = document.createElement("p");
  paragraph.innerHTML = message.username + ": " + message.message;
  msg_list.appendChild(paragraph);
  msg_list.scrollTo(0, msg_list.scrollHeight);
}

function recieveMessages(msg_list, websocket) {
  websocket.onmessage = ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "game_state":
        renderGameState(msg_list, event)
        break;
      case "update":
        renderUpdate(msg_list, event)
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

var username = "placeholder";

function bindFunctions() {
  const username_form = document.getElementById("username_form");
  const username_input = document.getElementById("username_input");
  const main = document.getElementById("main");
  const msg_form = document.getElementById("msg_form");
  const msg_list = document.getElementById("msg_list");
  // localhost needs to be replaced with hostname in production so this requires a better solution
  const websocket = new WebSocket("ws://localhost:8001/");
  const gameID = document.getElementById("gameID").innerHTML;
  setUsername(username_form, username_input, main);
  joinGame(websocket, gameID);
  sendMessages(msg_form, websocket, gameID);
  recieveMessages(msg_list, websocket);

  document.getElementById("game_link").onclick = copyLink;
}

bindFunctions();
