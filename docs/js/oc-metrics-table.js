/*
 * OC Metrics Table View Model
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
 */
const OcMetricTable = (function() {
  /*
   * Constants
   */
  const SELECTOR = 'section#oc-covid-metrics table'
  const JSON_URL = 'https://raw.githubusercontent.com/klenwell/covid-19/master/data/api/oc/metrics.json'

  /*
   * Public Methods
   */
  const render = function() {
    extractJsonData(JSON_URL)
  }

  /*
   * Private Methods
   */
  const extractJsonData = function(jsonUrl) {
    fetch(jsonUrl)
      .then(response => response.json())
      .then(data => onFetchComplete(data))
  }

  const onFetchComplete = function(jsonData) {
    console.log('onFetchComplete:', jsonData)
    //const model = new OcMetricModel(jsonData)
    let model = {
      'cases': {
        updatedOn: jsonData.testPositiveRate.updatedOn,
        latest: jsonData.testPositiveRate.latest,
        trend: jsonData.testPositiveRate.trend,
        delta7dValue: jsonData.testPositiveRate.d7Value,
        delta7dDelta: jsonData.testPositiveRate.d7DeltaPct
      }
    }
    populate(model)
  }

  const populate = function(model) {
    console.log("populate:", model)

     $(`${SELECTOR} tbody tr`).each((_, el) => {
       const $tr = $(el)
       const rowGetter = $tr.data('getter')
       const rowData = model[rowGetter]
       console.debug($tr, rowGetter, rowData)

       $tr.find('td.latest span.value').html(rowData.latest)
       $tr.find('td.level span.value').html(rowData.level)
       $tr.find('td.trend span.value').html(rowData.trend)
       $tr.find('td.delta-7d span.value').html(rowData.delta7dValue)
       $tr.find('td.delta-7d span.delta').html(rowData.delta7dDelta)
       $tr.find('td.delta-14d span.value').html(rowData.delta14dValue)
       $tr.find('td.delta-14d span.delta').html(rowData.delta14dDelta)
     })
  }

  /*
   * Public API
   */
  return {
    render: render
  }
})()

/*
 * Main block: these are the things that happen on page load.
 */
$(document).ready(function() {
  OcMetricTable.render()
})
