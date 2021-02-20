
function setGpioPin(id, value) {
    const url = 'http://127.0.0.1:5000/gpio'
    let data = { id: id, value: value };

    fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(res => {
        console.log("Request complete! response:", res);
    });
}

function setColor(value) {
    const url = 'http://127.0.0.1:5000/color'
    let data = { value: value };

    fetch(url, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(res => {
        console.log("Request complete! response:", res);
    });
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

const colorpicker = document.getElementById('colorpicker');
colorpicker.addEventListener('input', onColorChanged);
function onColorChanged(e) {
    //setColor(e.target.value);
    value = JSON.stringify({
        action: 'color',
        value: hexToRgb(e.target.value)
    })
    console.log(value);
    audioServerWebsocket.send(value);
}

const sigma = document.getElementById('sigma');
sigma.addEventListener('input', onSigmaChanged);
function onSigmaChanged(e) {
    //setColor(e.target.value);
    value = JSON.stringify({
        action: 'sigma',
        value: e.target.value
    })
    console.log(value);
    audioServerWebsocket.send(value);
}

function initUI() {
    const url = 'http://127.0.0.1:5000/gpio'
    fetch(url)
        .then(response => response.json())
        .then(json => {
            console.log("Received GPIO status: " + json);
            console.log(json)
            addButton("smoke-button", "Smoke", 4, json[4])
        })
}
function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

$(function() {
    $("#freq-slider-range").slider({
        range: true,
        min: 0,
        max: 12000,
        values: [ 50, 1000 ],
        slide: function( event, ui ) {
            $("#freq").val(ui.values[0] + " - " + ui.values[1]);
            value = JSON.stringify({
                action: 'frequency',
                value: {
                    min: ui.values[0],
                    max: ui.values[1]
                }
            })
            console.log(value);
            audioServerWebsocket.send(value);
        }
    });
    $( "#freq" ).val(
        $("#freq-slider-range").slider("values", 0) + " - " + $("#freq-slider-range").slider("values", 1)
    );
});

audioServerWebsocket = new WebSocket("ws://127.0.0.1:6789/");
audioServerWebsocket.onmessage = function (event) {
    data = JSON.parse(event.data);
    switch (data.type) {
        case 'state':
            //value.textContent = data.value;
            break;
        case 'users':
            //users.textContent = (
            //    data.count.toString() + " user" +
            //    (data.count == 1 ? "" : "s"));
            break;
        default:
            console.error(
                "unsupported event", data);
    }
};

initUI()
