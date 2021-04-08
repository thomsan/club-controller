let clientUis = []
const hostname = location.hostname;
const websocketPort = 6789
const ws = new WebSocket('ws://' + hostname + ':'+ websocketPort + '/');
ws.onmessage = ({data}) => {
    let message = JSON.parse(data);
    switch (message.type) {
        case messageId.CLIENT_LIST:
            message.client_configs.forEach(config  => {
                let clientUi = clientUis.find(c => c.config.ip == config.ip)
                if(clientUi){
                    clientUi.update(config)
                } else{
                    createClientUI(config)
                }
            });
            break;
        case messageId.CLIENT_CONNECTED:
            createClientUI(message.config)
            break;
        default:
            console.error(
                "unsupported message", data);
    }
};

function createClientUI(config){
    let parentDiv = document.getElementById('clients')
    switch (config.typeId){
        case clientTypeId.LED_STRIP_CLIENT:
            clientUis.push(new LEDStripUI(config, parentDiv, ws))
            break;
        case clientTypeId.CONTROLLER_CLIENT:
            console.warn("CONTROLLER_CLIENT not implemented yet")
            break;
        case clientTypeId.GPIO_CLIENT:
            console.warn("GPIO_CLIENT not implemented yet")
            break;
        default:
            console.error("Client typeId not implemented: " + config.typeId)
            break;
    }
}

function getLedStripsHtml(ledStripConfigs){
    const html = ledStripConfigs.map((config) => {
        return `
            <div id=${config.ip}">
                <label for="favcolor">Color:</label>
                <input id="colorpicker" type="color" id="colorpicker" value="${rgbToHex(config.led_strip_params.color)}">
            </div>
            `;
    }).join('');
    return `<div class="led-strips">${html}</div>`;
}

function drawClientUis(configs){
    let ledStripConfigs = configs.filter(config => config.typeId == clientTypeId.LED_STRIP_CLIENT);
    let ledStripsHtml = getLedStripsHtml(ledStripConfigs)
    const html = ledStripsHtml;
    document.getElementById('clients').innerHTML = html;
}
