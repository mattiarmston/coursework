function setUsername(form, input, main) {
  main.style.display = "none";
  form.onsubmit = (e) => {
    e.preventDefault();
    console.log(username);
    username = input.value;
    console.log(username);
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

function recieveMessages(msg_list, websocket) {
  websocket.onmessage = ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "message":
        message = document.createElement("p");
        message.innerHTML = event.username + ": " + event.message
        msg_list.appendChild(message);
        break;
      default:
        throw new Error(`Unsupported event type '${event.type}'`)
    }
  }
}

function copyLink(event) {
  event.preventDefault();
  let game_link = document.getElementById("game_link");
  navigator.clipboard.writeText(game_link.href);
  game_link.style.setProperty("--message", '"Copied"');
}

var username = "placeholder";

function bindFunctions() {
  const username_form = document.getElementById("username_form");
  const username_input = document.getElementById("username_input");
  const main = document.getElementById("main");
  const msg_form = document.getElementById("msg_form");
  const msg_list = document.getElementById("msg_list");
  const websocket = new WebSocket("ws://localhost:8001/");
  const gameID = document.getElementById("gameID").innerHTML;
  setUsername(username_form, username_input, main);
  joinGame(websocket, gameID);
  sendMessages(msg_form, websocket, gameID);
  recieveMessages(msg_list, websocket);

  document.getElementById("game_link").onclick = copyLink;
}

bindFunctions();
