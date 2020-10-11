class ContentCardDamper extends HTMLElement {
    set hass(hass) {
        if (!this.content) {
            const card = document.createElement('ha-card');
            card.header = 'Damper';
            this.content = document.createElement('div');
            this.content.style.padding = '0 16px 16px';
            card.appendChild(this.content);
            this.appendChild(card);
        }

        const entityId = this.config.entity;
        const state = hass.states[entityId];
        const stateStr = state ? state.state : 'unavailable';
        const attr = state.attributes

        this.content.innerHTML = `
        <h2>The state of ${attr["friendly_name"]} is <b> ${stateStr}</b > ! </h2>
            <table>
                <tr> <td><b>Modbus Address:</b> </td> <td>${attr["Modbus Address"]} </td>  </tr>
                <tr> <td><b>Type ASN:</b> </td> <td>${attr["Type ASN"]}</td>  </tr>
                <tr> <td><b>Manufacturing Date:</b> </td> <td>${attr["Manufacturing Date"]}</td>  </tr>
                <tr> <td><b>Factory Index:</b> </td> <td>${attr["Factory Index"]}</td>  </tr>
                <tr> <td><b>Factory Seq Number:</b> </td> <td>${attr["Factory Seq Num"]}</td>  </tr>
                <tr> <td><b>Last runtime close:</b> </td> <td>${attr["Last runtime close"]}</td>  </tr>
                <tr> <td><b>Last runtime оpen:</b> </td> <td>${attr["Last runtime оpen"]}</td>  </tr>
                <tr> <td><b>Last power:</b> </td> <td>${attr["Last power"]}</td>  </tr>
                <tr> <td><b>Last overall indicator:</b> </td> <td>${attr["Last overall indicator"]}</td>  </tr>
                <tr> <td><b>Last runtime close indicator:</b> </td> <td>${attr["Last runtime close indicator"]}</td>  </tr>
                <tr> <td><b>Runtime open indicator:</b> </td> <td>${attr["Runtime open indicator"]}</td>  </tr>
                <tr> <td><b>Last power indicator:</b> </td> <td>${attr["Last power indicator"]}</td>  </tr>
            </table>
            <paper-textarea>Hello paper-textarea</paper-textarea>

        `;
    }

    static getStubConfig() {
        return { entity: "cover.modbus_1" }
    }

    setConfig(config) {
        if (!config.entity) {
            throw new Error('You need to define an entity');
        }
        this.config = config;
    }

    // The height of your card. Home Assistant uses this to automatically
    // distribute all cards over the available columns.
    getCardSize() {
        return 3;
    }
}

customElements.define('content-card-damper', ContentCardDamper);
window.customCards = window.customCards || [];
window.customCards.push({
    type: "content-card-damper",
    name: "Content Card Damper",
    preview: true, // Optional - defaults to false
    description: "A custom card made by me!" // Optional
})