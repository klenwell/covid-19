/*
 * OcWavesModel
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/

class OcWavesModel {
  constructor(jsonData) {
    this.data = jsonData.data
    this.meta = jsonData.meta
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
  get waves() {
    return this.data
  }

  /*
   * Methods
  **/
}
