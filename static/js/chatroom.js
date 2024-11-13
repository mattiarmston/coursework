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

function sendMessages(form, websocket, gameID, config) {
  form.onsubmit = (e) => {
    e.preventDefault()
    let msg_input = document.getElementById("msg_input");
    const message = msg_input.value;
    msg_input.value = "";
    const event = {
      type: "message",
      gameID: gameID,
      config: config,
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
        message.innerHTML = event.username + ": " + event.message;
        msg_list.appendChild(message);
        msg_list.scrollTo(0, msg_list.scrollHeight);
        break;
      case "error":
        console.log(event.message);
        break;
      default:
        console.log(`Unsupported event type '${event.type}'`)
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
  const config = document.getElementById("config").innerHTML;
  setUsername(username_form, username_input, main);
  joinGame(websocket, gameID);
  sendMessages(msg_form, websocket, gameID, config);
  recieveMessages(msg_list, websocket);

  document.getElementById("game_link").onclick = copyLink;
}

bindFunctions();
