import "https://unpkg.com/wired-card@2.1.0/lib/wired-card.js?module";
import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

import { classMap } from 'https://unpkg.com/lit-html/directives/class-map.js?module';

// import { LitElement, html, css } from 'lit-element';
// import { classMap } from 'lit-html/directives/class-map';


class DamperPanel extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      narrow: { type: Boolean },
      route: { type: Object },
      panel: { type: Object },
    };
  }

  constructor() {
    super();
    // this.name = "World";
    // this.myArray = ["a", "b", "c"];
  }

  render() {
    return html`
      <wired-card elevation="2">
      <table>
      <tr>
      <th>Modbus Address</th>
      <th>Name</th>
      <th>Model</th>
      <th>State</th>
      <th>Current position</th>
      <th>Entity ID</th>
      <th>Test now</th>
      <th>Last runtime open</th>
      <th>Last runtime close</th>
      <th>Last power</th>
      <th>Last runtime open indicator</th>
      <th>Last runtime close indicator</th>
      <th>Last power indicator</th>
      <th>Last tested at</th>
      </tr>
      ${Object.keys(this.hass.states)
        .filter((i) => i.startsWith("cover."))
        .map(
          (i) => html`
          <tr>
              <td>${this.hass.states[i].attributes["Modbus Address"]}</td>
              <td>${this.hass.states[i].attributes["friendly_name"]}</td>
              <td>${this.hass.states[i].attributes["Type ASN"]}</td>
              <td>${this.hass.states[i].state}</td>
              <td>${this.hass.states[i].attributes["current_position"]}</td>
              <td>${this.hass.states[i]["entity_id"]}</td>
              <td><button @click="${e => this.callServiceTest(this.hass.states[i]["entity_id"])}">Click me</button></td>
              <td>${this.hass.states[i].attributes["Last runtime open"]}</td>
              <td>${this.hass.states[i].attributes["Last runtime close"]}</td>
              <td>${this.hass.states[i].attributes["Last power"]}</td>
              <td class=${classMap({ failure: this.hass.states[i].attributes["Last runtime open indicator"] == 'FAILURE' })}>
              ${this.hass.states[i].attributes["Last runtime open indicator"]}
              </td>
              <td class=${classMap({ failure: this.hass.states[i].attributes["Last runtime close indicator"] == 'FAILURE' })}>
              ${this.hass.states[i].attributes[
            "Last runtime close indicator"
            ]}
            </td>
            <td class=${classMap({ failure: this.hass.states[i].attributes["Last power indicator"] == 'FAILURE' })}>${this.hass.states[i].attributes["Last power indicator"]}</td>
            <td>${this.hass.states[i].attributes["Last tested at"]}</td>
            </tr>
            `
        )}

            </table>
            </wired - card >
            `;
  }

  callServiceTest(entity_id) {
    // this.hass.callService(this.domain, this.service, this.serviceData);
    console.log('Clicked me!');
    console.log(entity_id);
    this.hass.callService('damper', 'test_damper', { 'entity_id': entity_id })
  }

  static get styles() {
    return css`
      : host {
        // background - color: #fafafa;
        background - color: grey;
        padding: 16px;
        display: block;
      }
      wired - card {
        // background - color: white;
        padding: 16px;
        display: block;
        font - size: 18px;
        max - width: 800;
        margin: 0 auto;
      }

      table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        padding: 15px
      }

      .pass {
        background-color: green;
      }
      .warning {
        background-color: yellow;
      }
      .failure {
        background-color: red;
      }

      `;
  }

}
customElements.define("damper-panel", DamperPanel);
