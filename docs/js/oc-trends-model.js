/*
 * OcTrendsModel
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const OcTrendsModelConfig = {
  readyEvent: 'OcTrendsModel:data:ready',
  extractUrl: 'data/json/oc/trends.json'
}


class OcTrendsModel {
  constructor(config) {
    this.config = config
    this.data = {}
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
  // For use by component as on event string to confirm data loaded:
  // $(document).on(OcTrendsModel.dataReady, (event, model) => {})
  static get dataReady() {
    return OcTrendsModelConfig.readyEvent
  }

  get weeks() {
    return this.data.weeks
  }

  /*
   * Public Methods
  **/
  fetchData() {
    fetch(this.config.extractUrl)
      .then(response => response.json())
      .then(data => this.onFetchComplete(data))
  }

  /*
   * Private Methods
  **/
  onFetchComplete(jsonData) {
    this.data = jsonData
    this.triggerReadyEvent()
  }

  triggerReadyEvent() {
    console.log(this.config.readyEvent, this)
    console.log(this.weeks)
    $(document).trigger(this.config.readyEvent, [this])
  }
}


/*
 * Main block: these are the things that happen on page load.
**/
$(document).ready(function() {
  const model = new OcTrendsModel(OcTrendsModelConfig)
  model.fetchData()
})
