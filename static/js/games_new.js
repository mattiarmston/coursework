
function updateForm() {
  let game = document.getElementById("game");
  let forms = document.querySelectorAll("form");
  for (form of forms) {
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
  document.querySelector("#game").onchange = updateForm;
}

bindFunctions();
