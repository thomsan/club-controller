class UiCoordinator {
    constructor(websocket){
        this.clientUis = []
        this.websocket = websocket
        this.ledParentDiv = document.getElementById('led-strip-clients')
        this.gpioParentDiv = document.getElementById('gpio-clients')
        this.ledMasterUi = new LEDStripMasterUi(this.ledParentDiv, websocket)
    }

    createClientUI(config){
        switch (config.typeId){
            case clientTypeId.LED_STRIP_CLIENT:
                this.clientUis.push(new LEDStripClientUI(config, this.ledParentDiv, this.websocket))
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

    getClientUi(config){
        return new Promise((resolve, reject) => {
            let clientUi = this.clientUis.find(c => c.config.ip == config.ip)
            if(clientUi){
                resolve(clientUi)
            } else{
                reject()
            }
        });
    }

    update(client_configs){
        client_configs.forEach(config  => {
            this.getClientUi(config)
                .then(clientUi => {
                    clientUi.update(config)
                },
                () => {
                    this.createClientUI(config)
                })
                .catch(e => console.error(e));
        });
    }

    remove(config){
        this.getClientUi(config)
            .then(clientUi => {
                clientUi.remove()
                const index = this.clientUis.indexOf(clientUi);
                if(index > -1){
                    this.clientUis.splice(index, 1);
                }
            },
            () => {
                // local client reference is already removed
            });
    }
}

const hostname = location.hostname;
const websocketPort = 6789
const ws = new WebSocket('ws://' + hostname + ':'+ websocketPort + '/');
let uiCoordinator = new UiCoordinator(ws)
ws.onmessage = ({data}) => {
    let message = JSON.parse(data);
    switch (message.type) {
        case messageId.CLIENT_LIST:
            uiCoordinator.update(message.client_configs)
            break;
        case messageId.CLIENT_CONNECTED:
            uiCoordinator.createClientUI(message.config)
            break;
        case messageId.CLIENT_DISCONNECTED:
            uiCoordinator.remove(message.config)
            break;
        default:
            console.error("Received messageId which is not implemented: ", message.type);
    }
};
