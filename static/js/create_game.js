
function_map = {
  "whist": updateWhist,
  "promise": updatePromise,
  "poker": updatePoker,
}

function updateForm() {
  let default_game = document.querySelector("#default_game");
  if (default_game != null) {
    default_game.remove();
  }
  let game = document.querySelector("#game");
  func = function_map[game.value];
  func(document.querySelector("#settings"));
}

function updateWhist(form) {
  // Create elements
  let players_label = document.createElement("label");
  players_label.innerHTML = "Players:";
  let players_4 = document.createElement("p");
  players_4.innerHTML = "4";

  let scoring_label = document.createElement("label");
  scoring_label.innerHTML = "Scoring:";
  let scoring = document.createElement("select");
  let scoring_opts = [
    ["british_short_whist", "British Short Whist"],
    ["american_short_whist", "American Short Whist"],
    ["long_whist", "Long Whist"],
  ]
  for (pair of scoring_opts) {
    let opt = document.createElement("option");
    opt.value = pair[0];
    opt.innerHTML = pair[1];
    scoring.appendChild(opt);
  }

  let length_label = document.createElement("label");
  length_label.innerHTML = "Length:";
  let length = document.createElement("select");
  let length_opts = [
    ["game", "1 game"],
    ["rubber", "1 rubber"],
  ]
  for (pair of length_opts) {
    let opt = document.createElement("option");
    opt.value = pair[0];
    opt.innerHTML = pair[1];
    length.appendChild(opt);
  }

  // Wrap elements in div to place each one on a separate line
  let children = [
    players_label, players_4, scoring_label, scoring, length_label, length
  ];
  for (i = 0; i < children.length; i++) {
    let wrapper = document.createElement("div");
    wrapper.appendChild(children[i]);
    children[i] = wrapper;
  }

  let select_label = document.createElement("div");
  select_label.appendChild(document.querySelector("#game_label"))
  let select = document.querySelector("#game");
  let submit = document.createElement("input");
  submit.type = "submit";
  submit.value = "Create Game";
  children = [select_label, select, ...children, submit];
  form.replaceChildren(...children);
}

function updatePromise(form) {
  let label = document.createElement("p")
  label.innerHTML = "Coming soon!"

  let children = [label]
  for (i = 0; i < children.length; i++) {
    let wrapper = document.createElement("div");
    wrapper.appendChild(children[i]);
    children[i] = wrapper;
  }

  let select_label = document.createElement("div");
  select_label.appendChild(document.querySelector("#game_label"));
  let select = document.querySelector("#game");
  children = [select_label, select, ...children];
  form.replaceChildren(...children);
}

function updatePoker(form) {
  let label = document.createElement("p")
  label.innerHTML = "Coming soon!"

  let children = [label]
  for (i = 0; i < children.length; i++) {
    let wrapper = document.createElement("div");
    wrapper.appendChild(children[i]);
    children[i] = wrapper;
  }

  let select_label = document.createElement("div");
  select_label.appendChild(document.querySelector("#game_label"));
  let select = document.querySelector("#game");
  children = [select_label, select, ...children];
  form.replaceChildren(...children);
}


function bindFunctions() {
  document.querySelector("#game").onchange = updateForm;
}

bindFunctions();
