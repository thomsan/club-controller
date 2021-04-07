class LEDStrip {
    constructor(parentDiv, state, websocket){
        this.id = id;
        this.websocket = websocket;
        this.div = document.createElement("div");
        this.colorpicker = document.createElement("input");
        this.colorpicker.type = "color";
        this.colorpicker.addEventListener('input', onColorChanged);
        this.sigmaSlider = document.createElement("sgima");
        this.sigmaSlider.type = "range";
        this.sigmaSlider.addEventListener('input', onSigmaChanged);
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
                websocket.send(value);
            }
        });
        $( "#freq" ).val(
            $(this.freqRangeSlider).slider("values", 0) + " - " + $(this.freqRangeSlider).slider("values", 1)
        );
        this.div.appendChild(this.colorpicker)
        this.div.appendChild(this.sigmaSlider)
        this.div.appendChild(this.freqRangeSlider)
        parentDiv.appendChild(this.div)
    }

    onColorChanged(e) {
        // TODO implement websocket protocol
        let value = JSON.stringify({
            action: 'color',
            value: hexToRgb(e.target.value)
        })
        console.log("Color changed to " + value);
        websocket.send(value);
    }

    onSigmaChanged(e) {
        // TODO implement websocket protocol
        let value = JSON.stringify({
            action: 'sigma',
            value: e.target.value
        })
        console.log(value);
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
}
