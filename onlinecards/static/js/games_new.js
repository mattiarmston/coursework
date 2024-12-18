
function updateForm() {
  let game = document.getElementById("game_type");
  let forms = document.querySelectorAll("form");
  for (let form of forms) {
    if (form.id == "settings") {
      // Do nothing
    } else if (form.id == game.value) {
      form.style.display = "inline";
    } else {
      form.style.display = "none";
    }
  }
}

function bindFunctions() {
  document.getElementById("game_type").onchange = updateForm;
}

bindFunctions();
