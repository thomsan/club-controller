// DEPRECATED

function initUI() {
    const url = 'http://' + server_ip + ':5000/gpio'
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log("Received GPIO status: " + json);
            console.log(json)
            addButton("smoke-button", "Smoke", 4, json[4])
        })
}

function onGpioButtonClick(buttonEl, id) {
    if (buttonEl.className == "disabled") {
        buttonEl.className = "";
        console.log("enabled")
        setGpioPin(id, true);
    } else {
        buttonEl.className = "disabled";
        console.log("disabled");
        setGpioPin(id, false);
    }
}

function addButton(elementId, text, id, active) {
    var buttonEl = document.createElement("button");
    if (!active) {
        buttonEl.className = "disabled";
    } else {
        buttonEl.className = "";
    }
    buttonEl.id = "button-gpio-" + id;
    buttonEl.addEventListener('click', function () { onGpioButtonClick(buttonEl, id); }, false);

    var buttonTextEl = document.createElement("span");
    buttonTextEl.className = "button-text";
    buttonTextEl.innerText = text;
    buttonEl.appendChild(buttonTextEl);
    document.getElementById(elementId).appendChild(buttonEl);
}
