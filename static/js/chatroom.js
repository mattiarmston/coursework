function sendMessages(form, websocket) {
  form.onsubmit = (e) => {
    e.preventDefault()
    let msg_input = document.getElementById("msg_input");
    const message = msg_input.value;
    msg_input.value = "";
    const event = {
      type: "message",
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
        message.innerHTML = event.message
        msg_list.appendChild(message);
        break;
      default:
        throw new Error(`Unsupported event type '${event.type}'`)
    }
  }
}

function bindFunctions() {
  const form = document.getElementById("msg_form");
  const msg_list = document.getElementById("msg_list");
  const websocket = new WebSocket("ws://localhost:8001/");
  sendMessages(form, websocket);
  recieveMessages(msg_list, websocket);
}

bindFunctions();
