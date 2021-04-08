class LEDStripUI {
    constructor(config, parentDiv, websocket){
        this.config = config;
        this.parentDiv = parentDiv
        this.websocket = websocket;
        this.div = document.createElement("div");
        this.title = document.createElement("h3")
        this.colorpicker = document.createElement("input");
        this.colorpicker.type = "color";
        this.colorpicker.addEventListener('input', e => this.onColorChanged(e));
        /*this.sigmaSlider = document.createElement("sgima");
        this.sigmaSlider.type = "range";
        this.sigmaSlider.addEventListener('input', this.onSigmaChanged);
        this.freqRangeSlider = document.createElement("sgima");
        $(this.freqRangeSlider).slider({
            range: true,
            min: 0,
            max: 12000,
            values: [ 50, 1000 ],
            slide: function( event, ui ) {
                $("#freq").val(ui.values[0] + " - " + ui.values[1]);
                let value = JSON.stringify({
                    action: 'frequency',
                    value: {
                        min: ui.values[0],
                        max: ui.values[1]
                    }
                })
                console.log(value);
                this.websocket.send(value);
            }
        });
        $( "#freq" ).val(
            $(this.freqRangeSlider).slider("values", 0) + " - " + $(this.freqRangeSlider).slider("values", 1)
        );
        this.div.appendChild(this.sigmaSlider)
        this.div.appendChild(this.freqRangeSlider)
        */
        this.div.appendChild(this.title);
        this.div.appendChild(this.colorpicker);
        this.parentDiv.appendChild(this.div);
        this.draw()
    }

    onColorChanged(e) {
        let new_color = this.hexToRgb(e.target.value)
        if(new_color != null){
            this.config.led_strip_params.color = new_color;
            let message = JSON.stringify({
                type: messageId.CLIENT_VALUE_UPDATED,
                config: this.config
            })
            this.websocket.send(message);
        }
    }

    onSigmaChanged(e) {
        // TODO implement websocket protocol
        let value = JSON.stringify({
            action: 'sigma',
            value: e.target.value
        })
        websocket.send(value);
    }

    hexToRgb(hex) {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    }

    componentToHex(c) {
        var hex = c.toString(16);
        return hex.length == 1 ? "0" + hex : hex;
    }

    rgbToHex(c) {
        return "#" + this.componentToHex(c.r) + this.componentToHex(c.g) + this.componentToHex(c.b);
    }

    update(config){
        this.config = config;
        this.draw();
    }

    isValidColor(hexColor){
        return /^#([0-9A-F]{3}){1,2}$/i.test(hexColor)
    }

    draw(){
        this.title.textContent = this.config.name
        let hexColor = this.rgbToHex(this.config.led_strip_params.color)
        if(this.isValidColor(hexColor)){
            this.colorpicker.value = hexColor
        }
    }
}
