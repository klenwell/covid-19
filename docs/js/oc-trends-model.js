/*
 * OcTrendsModel
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
// Need to use this IIFE module pattern to interpolate sheetID string.
// Usage: OcTrendsModelConfig.readyEvent
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
}


/*
 * Main block: these are the things that happen on page load.
**/
$(document).ready(function() {
  const model = new OcTrendsModel(OcTrendsModelConfig)
  model.fetchData()
})
