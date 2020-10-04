// import { LitElement, html, property, customElement } from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

// @customElement('example-panel')
// export class ExamplePanel extends LitElement {
//   @property() name = 'World';

//   render() {
//     return html`<p>Hello, ${this.name}!</p>`;
//   }
// }

import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class ExamplePanel extends LitElement {
  static get properties() {
    return {
      name: { type: String },
      myArray: { type: Array }
    };

  }

  constructor() {
    super();
    this.name = 'World';
    this.myArray = ['a', 'b', 'c']
  }

  render() {
    return html`
    <p>Hello, ${this.name}!</p>
    ${this.myArray.map(i => html`<li>${i}</li>`)}

    `;
  }
}

customElements.define("example-panel", ExamplePanel);

