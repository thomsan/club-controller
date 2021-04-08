let clientUis = []
const hostname = location.hostname;
const websocketPort = 6789
const ws = new WebSocket('ws://' + hostname + ':'+ websocketPort + '/');
ws.onmessage = ({data}) => {
    let message = JSON.parse(data);
    switch (message.type) {
        case messageId.CLIENT_LIST:
            message.client_configs.forEach(config  => {
                getClientUi(config)
                    .then(clientUi => {
                        clientUi.update(config)
                    },
                    () => {
                        createClientUI(config)
                    });
            });
            break;
        case messageId.CLIENT_CONNECTED:
            createClientUI(message.config)
            break;
        case messageId.CLIENT_DISCONNECTED:
            getClientUi(message.config)
                .then(clientUi => {
                    clientUi.remove()
                    const index = clientUis.indexOf(clientUi);
                    if(index > -1){
                        clientUis.splice(index, 1);
                    }
                },
                () => {
                    // local client reference is already removed
                });
            break;
        default:
            console.error("Received messageId which is not implemented: ", message.type);
    }
};

function getClientUi(config){
    return new Promise((resolve, reject) => {
        let clientUi = clientUis.find(c => c.config.ip == config.ip)
        if(clientUi){
            resolve(clientUi)
        } else{
            reject()
        }
    });
}

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
