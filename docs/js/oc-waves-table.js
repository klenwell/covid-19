/*
 * OC Waves Table View Model
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
 */

 class OcWavesModel {
  constructor(jsonData) {
    this.data = jsonData.data
    this.meta = jsonData.meta
    this.dateTime = luxon.DateTime
    console.warn("TODO: my own file")
  }

  get waves() {
    return this.data
  }
}

const OcWavesTable = (function() {
  /*
   * Constants
   */
  const SELECTOR = 'section#oc-covid-waves table'
  const JSON_URL = 'data/json/oc/waves.json'
  const $table = null;

  /*
   * Public Methods
   */
  const render = function() {
    $tableBody = $(SELECTOR).find('tbody')
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
    const model = new OcWavesModel(jsonData)
    populate(model)
  }

  const populate = function(model) {
    console.log("populate table:", model)
    let num = 0
    model.waves.forEach((wave) => {
      num++
      appendWaveRow(wave, num)
    })
  }

  const appendWaveRow = function(wave, num) {
    const $tr = $('<tr />')
    $tr.addClass(wave.type)
    console.log('TODO: append', wave)

    appendCell($tr, 'index', num)
    appendCell($tr, 'cycle', wave.type)
    appendCell($tr, 'start-date', wave.startedOn)
    appendCell($tr, 'end-date', wave.endedOn)
    appendCell($tr, 'days', wave.days)
    appendPeakCell($tr, wave.maxPositiveRate)
    appendGraphCell($tr, wave)
    $tableBody.append($tr)
  }

  const appendCell = function($tr, className, html) {
    const $td = $('<td />')
    $td.addClass(className)
    $td.html(html)
    $tr.append($td)
  }

  const appendPeakCell = function($tr, peak) {
    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(`${peak.value}%`)
    const $dateSpan = $('<span />').addClass('note').html(`on <b>${peak.date}</b>`)
    $div.append($valueSpan).append($dateSpan)
    appendCell($tr, 'peak', $div)
  }

  const appendGraphCell = function($tr, wave) {
    appendCell($tr, 'graph', 'TODO')
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
  OcWavesTable.render()
})
