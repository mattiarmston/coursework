function setRedirect() {
  const gameID = document.getElementById("gameID").value;
  const form = document.getElementById("join_form");
  form.action = "/games/join/" + gameID;
}

function bindFunctions() {
  let form = document.getElementById("join_form");
  form.onsubmit = setRedirect;
}

bindFunctions();
