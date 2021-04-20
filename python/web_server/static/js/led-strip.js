
const EffectId = {
    COLORED_ENERGY: 1,
    ENERGY: 2,
    SCROLL: 3,
    SPECTRUM: 4
}


function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(c) {
    return "#" + this.componentToHex(c.r) + this.componentToHex(c.g) + this.componentToHex(c.b);
}

function isValidColor(hexColor){
    return /^#([0-9A-F]{3}){1,2}$/i.test(hexColor)
}

class LEDStripMasterUi {
    constructor(parentDiv, websocket){
        this.parentDiv = parentDiv
        this.websocket = websocket;
        this.div = document.createElement("div");
        this.title = document.createElement("h3")
        this.title.textContent = "All LED strips"
        this.colorpicker = document.createElement("input");
        this.colorpicker.type = "color";
        this.colorpicker.value = "#ff0000"
        this.colorpicker.addEventListener('input', e => this.onColorChanged(e));
        this.effectSelector = document.createElement("select")
        this.effectSelector.onchange = () => this.onEffectChanged();
        for (let [key, value] of Object.entries(EffectId)){
            this.effectSelector.options.add( new Option(key,value) )
        }
        this.effectSelector.value = EffectId.COLORED_ENERGY
        this.div.appendChild(this.title);
        this.div.appendChild(this.colorpicker);
        this.div.appendChild(this.effectSelector);
        this.parentDiv.appendChild(this.div);
    }

    send_all_led_strips_update(data){
        let message = JSON.stringify({
            type: messageId.ALL_LED_STRIPS_UPDATED,
            data: data
        })
        this.websocket.send(message);
    }

    onColorChanged(e) {
        let new_color = hexToRgb(e.target.value)
        if(new_color != null){
            this.send_all_led_strips_update({color: new_color})
        }
    }

    onEffectChanged() {
        this.send_all_led_strips_update({effect_id: this.effectSelector.value});
    }
}

class LEDStripClientUI {
    constructor(config, parentDiv, websocket){
        this.config = config;
        this.parentDiv = parentDiv
        this.websocket = websocket;
        this.div = document.createElement("div");
        this.title = document.createElement("h3")
        this.colorpicker = document.createElement("input");
        this.colorpicker.type = "color";
        this.colorpicker.addEventListener('input', e => this.onColorChanged(e));
        this.effectSelector = document.createElement("select")
        this.effectSelector.onchange = () => this.onEffectChanged();
        for (let [key, value] of Object.entries(EffectId)){
            this.effectSelector.options.add( new Option(key,value) )
        }
        this.effectSelector.value = config.led_strip_params.effect_id
        this.sigmaSlider = document.createElement("input");
        this.sigmaSlider.type = "range";
        this.sigmaSlider.min = 1.0
        this.sigmaSlider.max = 30.0
        this.sigmaSlider.addEventListener('input', e => this.onSigmaChanged(e));
        this.freqSliderMin = document.createElement("input");
        this.freqSliderMin.type = "range";
        this.freqSliderMin.min = 1
        this.freqSliderMin.max = 12000
        this.freqSliderMin.addEventListener('input', e => this.onFreqMinChanged(e));
        this.freqSliderMax = document.createElement("input");
        this.freqSliderMax.type = "range";
        this.freqSliderMax.min = 50
        this.freqSliderMax.max = 12000
        this.freqSliderMax.addEventListener('input', e => this.onFreqMaxChanged(e));
        this.div.appendChild(this.title);
        this.div.appendChild(this.colorpicker);
        this.div.appendChild(this.effectSelector);
        this.div.appendChild(this.sigmaSlider)
        this.div.appendChild(this.freqSliderMin)
        this.div.appendChild(this.freqSliderMax)
        this.parentDiv.appendChild(this.div);
        this.draw()
    }

    send_config_update(){
        let message = JSON.stringify({
            type: messageId.CLIENT_VALUE_UPDATED,
            config: this.config
        })
        this.websocket.send(message);
    }

    onColorChanged(e) {
        let new_color = hexToRgb(e.target.value)
        if(new_color != null){
            this.config.led_strip_params.color = new_color;
            this.send_config_update()
        }
    }

    onEffectChanged() {
        this.config.led_strip_params.effect_id = parseInt(this.effectSelector.value)
        this.send_config_update();
    }

    onSigmaChanged(e) {
        let new_sigma = Math.min(Math.max(e.target.value, this.sigmaSlider.min), this.sigmaSlider.max)
        this.config.led_strip_params.sigma = new_sigma;
        this.send_config_update()
    }

    onFreqMinChanged(e) {
        let new_freq_min = e.target.value
        if(parseInt(new_freq_min) > parseInt(this.freqSliderMax.value)){
            this.freqSliderMax.value = new_freq_min;
        }
        this.config.led_strip_params.frequency.min = parseInt(new_freq_min);
        this.send_config_update()
    }

    onFreqMaxChanged(e) {
        let new_freq_max = e.target.value
        if(parseInt(new_freq_max) < parseInt(this.freqSliderMin.value)){
            this.freqSliderMin.value = new_freq_max;
        }
        this.config.led_strip_params.frequency.max = parseInt(new_freq_max);
        this.send_config_update()
    }

    update(config){
        this.config = config;
        this.draw();
    }

    draw(){
        this.title.textContent = this.config.name
        let hexColor = rgbToHex(this.config.led_strip_params.color)
        if(isValidColor(hexColor)){
            this.colorpicker.value = hexColor
        }
        if(this.effectSelector.value != this.config.led_strip_params.effect_id){
            this.effectSelector.value = this.config.led_strip_params.effect_id
        }
        this.sigmaSlider.value = this.config.led_strip_params.sigma
        this.freqSliderMin.value = this.config.led_strip_params.frequency.min
        this.freqSliderMax.value = this.config.led_strip_params.frequency.max
    }

    remove(){
        this.div.remove()
    }
}
