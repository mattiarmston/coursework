// Display a banner that informs users that the website uses cookies
// When the user clicks accept, store a cookie to reflect this and hide the banner
// If a user has already accepted cookies do not display the banner

function createBanner() {
  let wrapper = document.createElement("div");
  wrapper.className += "cookie_banner";
  let notice = document.createElement("p");
  notice.innerHTML = "This website uses cookies to work";
  notice.style.display = "inline-block";
  let accept_btn = document.createElement("button");
  accept_btn.innerHTML = "Ok";
  accept_btn.onclick = () => {
    wrapper.style.display = "none";
    document.cookie = `accepted_cookies=true; max-age=${60*60*24*365}`;
  }

  wrapper.append(notice, accept_btn);
  return wrapper
}

function displayBanner() {
  if (document.cookie.split("; ").some((cookie) =>
    cookie.includes("accepted_cookies=true"))
  ) {
    return
  }
  document.body.appendChild(createBanner());
}

displayBanner();
