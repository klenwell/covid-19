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
  const JSON_URL = 'data/json/oc/metrics.json'

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
    const model = new OcMetricsModel(jsonData)
    populate(model)
  }

  const populate = function(model) {
    console.log("populate table:", model)

    $(`${SELECTOR} tbody tr`).each((_, el) => {
      const $tr = $(el)
      const rowGetter = $tr.data('metric')
      const metric = model[rowGetter]

      // Update HTML
      $tr.find('td.updated-on span.value').html(metric.html.updatedOn)
      $tr.find('td.latest span.value').html(metric.html.latest)
      $tr.find('td.level span.value').html(metric.html.level)
      $tr.find('td.trend span.value').html(metric.html.trend)
      $tr.find('td.delta-7d span.value').html(metric.html.delta7dValue)
      $tr.find('td.delta-7d span.note').html(metric.html.delta7dNote)
      $tr.find('td.delta-14d span.value').html(metric.html.delta14dValue)
      $tr.find('td.delta-14d span.note').html(metric.html.delta14dNote)

      // Update td classes (styling)
      $tr.find('td.level').addClass(metric.tdClass.level)
      $tr.find('td.trend').addClass(metric.tdClass.trend)
      $tr.find('td.delta-7d').addClass(metric.tdClass.trend)
      $tr.find('td.delta-14d').addClass(metric.tdClass.trend)
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
