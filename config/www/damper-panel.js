import "https://unpkg.com/wired-card@2.1.0/lib/wired-card.js?module";
import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

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
    this.name = 'World';
    this.myArray = ['a', 'b', 'c']
  }

  render() {
    return html`
      <wired-card elevation="2">
      <table>
      <tr>
      <th>Modbus Address</th>
      <th>State</th>
      <th>Current position</th>
      <th>Last runtime open</th>
      <th>Last runtime close</th>
      <th>Last runtime open indicator</th>
      <th>Last runtime close indicator</th>
      </tr>
      ${Object.keys(this.hass.states)
        .filter(i => i.startsWith("cover."))
        .map(i => html`
        <tr>
          <td> ${this.hass.states[i].attributes["Modbus Address"]} </td>
          <td> ${this.hass.states[i].state} </td>
          <td> ${this.hass.states[i].attributes["current_position"]} </td>
          <td> ${this.hass.states[i].attributes["Last runtime open"]} </td>
          <td> ${this.hass.states[i].attributes["Last runtime close"]} </td>
          <td> ${this.hass.states[i].attributes["Last runtime open indicator"]} </td>
          <td> ${this.hass.states[i].attributes["Last runtime close indicator"]} </td>
        </tr> `)
      }

      </table>
      </wired - card >
  `;
  }

  static get styles() {
    return css`
      : host {
  background - color: #fafafa;
  padding: 16px;
  display: block;
}
wired - card {
  background - color: white;
  padding: 16px;
  display: block;
  font - size: 18px;
  max - width: 1200px;
  margin: 0 auto;
}

table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
  padding: 15px
}

`;
  }
}
customElements.define("damper-panel", DamperPanel);