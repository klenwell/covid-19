/*
 * OcTimeSeriesModel
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const OcTimeSeriesModelConfig = {
  readyEvent: 'OcTimeSeriesModel:data:ready',
  extractUrl: 'data/json/oc/time-series.json'
}


class OcTimeSeriesModel {
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
    return OcTimeSeriesModelConfig.readyEvent
  }

  get timeSeries() {
    return this.data.dates
  }

  get maxValues() {
    return this.data['max-values']
  }

  get dates() {
    return this.timeSeries.map((dated) => dated.date)
  }

  get wastewaterSeries() {
    return this.timeSeries.map((dated) => dated.wastewater)
  }

  get positiveRateSeries() {
    return this.timeSeries.map((dated) => dated['positive-rate'])
  }

  get caseSeries() {
    return this.timeSeries.map((dated) => dated.cases)
  }

  get hospitalCaseSeries() {
    return this.timeSeries.map((dated) => dated['hospital-cases'])
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
    $(document).trigger(this.config.readyEvent, [this])
  }
}


/*
 * Main block: these are the things that happen on page load.
**/
$(document).ready(function() {
  const model = new OcTimeSeriesModel(OcTimeSeriesModelConfig)
  model.fetchData()
})
