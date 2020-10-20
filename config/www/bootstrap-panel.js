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

class BootstrapPanel extends LitElement {
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

    // // Code backup of a modern approach to automatically create a table from an array of attributes:
    // this.showAttributes = ["Modbus Address", "friendly_name", "Type ASN", "current_position", "Last runtime open",
    //   "Last runtime close", "Last power", "Last runtime open indicator", "Last runtime close indicator", "Last power indicator", "Last tested at"];
  }

  render() {

    return html`
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css" integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2" crossorigin="anonymous">

    <div class="container">

    <div class="row align-items-end">
    ${Object.keys(this.hass.states)
        .filter((i) => i.startsWith("cover."))
        .map(
          (i) =>
            html`
            <div class="'col-12 col-sm-6 col-md-4 col-lg-4 col-xl-3 pb-1">
            <button type="button" class="btn w-100 btn-success" @click="${e => this.callServiceTest(this.hass.states[i]["entity_id"])}">
            <div>${this.hass.states[i].attributes["friendly_name"]}</div>
            </button>
            </div>
            `)}
            </div>
            <div class="row align-items-end">
            ${Object.keys(this.hass.states)
        .filter((i) => i.startsWith("cover."))
        .map(
          (i) =>
            html`
                <div class='col-12 col-sm-6 col-md-4 col-lg-4 col-xl-3 pb-1'>

                <button type="button"
                class="
                btn
                w-74
                test-running"
                >
                <div>${this.hass.states[i].attributes["friendly_name"]}</div>
                </button>

                <button @click="${e => this.callServiceTest(this.hass.states[i]["entity_id"])} type="button"
                class="
                btn w-25 float-right btn-primary">
                Test
                </button>
                </div>
                `)}

        </div>
        </div>






      <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ/JpcUGGOn+Y7RsweNrtN/tE3MoK7ZeZDyx" crossorigin="anonymous"></script>
    `;

  }

  callServiceTest(entity_id) {
    // this.hass.callService(this.domain, this.service, this.serviceData);
    console.log('Clicked me!');
    console.log(entity_id);
    // if (navigator.platform != 'iPhone' || 'iPad') { window.navigator.vibrate(200); }
    try {  // Apple devices don't support vibrate
      window.navigator.vibrate(200);
    } catch (err) { console.log(err); };

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
      border - collapse: collapse;
      padding: 15px
    }
    th {
      background - color: #17a2b8;
      color: white
    }

      .pass {
      background - color: #28a745;
      color: white
    }
      .warning {
      background - color: #ffc107;
      color: black
    }
      .failure {
      background - color: #dc3545;
      color: white
    }
    button {
      background - color: yellow
    }
    wired - button {
      color: #fff;
      background - color: #007bff;
      border - color: #007bff;
    }
      .large {
      font - size: 24px;
    }

    .test-running {
      background: linear-gradient(to right,lightgrey 50%, white 50%);
      background-size: 200% 100%;
      transition: all 1s linear;
      border: 1px solid black;
    }

    .w-74 {
      width: 74% !important;
    }



    `;
  }

}
customElements.define("bootstrap-panel", BootstrapPanel);
