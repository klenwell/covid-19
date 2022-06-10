/*
 * OcWavesModel
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const OcWavesModelConfig = {
  readyEvent: 'OcWavesModel:data:ready',
  extractUrl: 'data/json/oc/waves.json'
}


class OcWavesModel {
  constructor(config) {
    this.config = config
    this.data = []
    this.meta = {}
    this.url = config.extractUrl
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
  // For use by component as on event string to confirm data loaded:
  // $(document).on(OcWavesModel.dataReady, (event, model) => {})
  static get dataReady() {
    return OcWavesModelConfig.readyEvent
  }

  get waves() {
    return this.data
  }

  /*
   * Public Methods
  **/
  fetchData() {
    fetch(this.url)
      .then(response => response.json())
      .then(data => this.onFetchComplete(data))
  }

  /*
   * Private Methods
  **/
  onFetchComplete(jsonData) {
    this.data = jsonData.data
    this.meta = jsonData.meta
    this.triggerReadyEvent()
  }

  triggerReadyEvent() {
    console.log(this.config.readyEvent, this)
    $(document).trigger(this.config.readyEvent, [this])
  }
}


$(document).ready(function() {
  const model = new OcWavesModel(OcWavesModelConfig)
  model.fetchData()
})
