import "https://unpkg.com/wired-card@2.1.0/lib/wired-card.js?module";
import "https://unpkg.com/wired-button@2.1.0/lib/wired-button.js?module";
import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

import { classMap } from 'https://unpkg.com/lit-html/directives/class-map.js?module';

// import "https://www.unpkg.com/@material/mwc-button@0.19.1/mwc-button.js?module";

// import { LitElement, html, css } from 'lit-element';
// import { classMap } from 'lit-html/directives/class-map';
// unpkg.com/:package@:version/:file

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
    // this.i1 = this.hass.states[i].attributes["Last runtime open indicator"];
    this.i1 = "WARNING";
    this.showAttributes = ["Modbus Address", "friendly_name", "Type ASN", "current_position", "Last runtime open",
      "Last runtime close", "Last power", "Last runtime open indicator", "Last runtime close indicator", "Last power indicator", "Last tested at"];
  }

  render() {
    // const row = attr => html`<td>: ${this.hass.states["cover.modbus_1"].attributes[attr]}</td>`;
    const header = html`<tr>${this.showAttributes.map(attr => html`<th>${attr}</th>`)}
                  <th>State</th>
                  <th>Test</th>
                  </tr>`;
    const row = entity_id => html`
                            <tr>${this.showAttributes.map(attr =>
      html`<td class=${classMap({
        failure: this.hass.states[entity_id].attributes[attr] == 'FAILURE',
        warning: this.hass.states[entity_id].attributes[attr] == 'WARNING',
        pass: this.hass.states[entity_id].attributes[attr] == 'PASS'
      })}>${this.hass.states[entity_id].attributes[attr]}</td>`)}
                            <td>${this.hass.states[entity_id].state}</td>
                            <td><wired-button @click="${e => this.callServiceTest(entity_id)}">Click me</wired-button></td>
                            </tr>
                            `;
    const rows = Object.keys(this.hass.states)
      .filter((i) => i.startsWith("cover."))
      .map(
        (i) => row(i)
      );

    // <td class=${classMap({ failure: this.hass.states[i].attributes["Last runtime open indicator"] == 'FAILURE' })}>

    this.coverEntityIds = Object.keys(this.hass.states).filter((i) => i.startsWith("cover.")).map((i) => i);
    console.log(this.coverEntityIds);
    this.x = this.hass.states[this.coverEntityIds[0]].attributes;
    console.log(this.x);
    console.log(this.x["Type ASN"]);

    this.renderedView = '';

    this.coverEntityIds.forEach(cover => {
      this.a = this.hass.states[cover].attributes;
      console.log(this.a);
    });

    this.coverEntityIds = Object.keys(this.hass.states).filter((i) => i.startsWith("cover.")).map((i) => {
      console.log(i);
      console.log(this.hass.states[i].attributes);
    });

    return html`
    <wired-card elevation="2">
    <wired-button elevation="3" class="large" @click="${e => this.callServiceTest("all")}">Test all</wired-button>
    <table>
    ${header}
    ${rows}
    </table>
    </wired-card>

    `;




    // return html`
    //   <wired-card elevation="2">
    //   <table>
    //   <tr>
    //   <th>Modbus Address</th>
    //   <th>Name</th>
    //   <th>Model</th>
    //   <th>State</th>
    //   <th>Current position</th>
    //   <th>Entity ID</th>
    //   <th>Test now</th>
    //   <th>Last runtime open</th>
    //   <th>Last runtime close</th>
    //   <th>Last power</th>
    //   <th>Last runtime open indicator</th>
    //   <th>Last runtime open indicator</th>
    //   <th>Last runtime close indicator</th>
    //   <th>Last power indicator</th>
    //   <th>Last tested at</th>
    //   </tr>
    //   ${Object.keys(this.hass.states)
    //     .filter((i) => i.startsWith("cover."))
    //     .map(
    //       (i) =>
    //         html`
    //       <tr>
    //           <td>${this.hass.states[i].attributes["Modbus Address"]}</td>
    //           <td>${this.hass.states[i].attributes["friendly_name"]}</td>
    //           <td>${this.hass.states[i].attributes["Type ASN"]}</td>
    //           <td>${this.hass.states[i].state}</td>
    //           <td>${this.hass.states[i].attributes["current_position"]}</td>
    //           <td>${this.hass.states[i]["entity_id"]}</td>
    //           <td><button @click="${e => this.callServiceTest(this.hass.states[i]["entity_id"])}">Click me</button></td>
    //           <td>${this.hass.states[i].attributes["Last runtime open"]}</td>
    //           <td>${this.hass.states[i].attributes["Last runtime close"]}</td>
    //           <td>${this.hass.states[i].attributes["Last power"]}</td>
    //           <td class=${classMap({ failure: this.i1 == 'FAILURE' })}>
    //           ${this.i1}
    //           </td>
    //           <td class=${classMap({ failure: this.hass.states[i].attributes["Last runtime open indicator"] == 'FAILURE' })}>
    //           ${this.hass.states[i].attributes["Last runtime open indicator"]}
    //           </td>
    //           <td class=${classMap({ failure: this.hass.states[i].attributes["Last runtime close indicator"] == 'FAILURE' })}>
    //           ${this.hass.states[i].attributes[
    //           "Last runtime close indicator"
    //           ]}
    //         </td>
    //         <td class=${classMap({ failure: this.hass.states[i].attributes["Last power indicator"] == 'FAILURE' })}>${this.hass.states[i].attributes["Last power indicator"]}</td>
    //         <td>${this.hass.states[i].attributes["Last tested at"]}</td>
    //         </tr>
    //         `


    //     )
    //   }
    //   </table>
    //   </wired - card >
    //   `;

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
      th {
        background-color: #17a2b8;
        color: white
      }

      .pass {
        background-color: #28a745;
        color: white
      }
      .warning {
        background-color: #ffc107;
        color: black
      }
      .failure {
        background-color: #dc3545;
        color: white
      }
      button {
        background-color: yellow
      }
      wired-button {
        color: #fff;
        background-color: #007bff;
        border-color: #007bff;
      }
      .large {
        font-size: 24px;
      }

      `;
  }

}
customElements.define("damper-panel", DamperPanel);
