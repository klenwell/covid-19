/*
 * OC Waves Table Component
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
**/
const OcWavesTable = (function() {
  /*
   * Constants
   */
  const SELECTOR = 'section#oc-covid-waves table'

  /*
   * Public Methods
   */
  const render = function(model) {
    $(SELECTOR).find('caption').html('')
    $tableBody = $(SELECTOR).find('tbody')
    populate(model)
  }

  /*
   * Private Methods
   */
  const populate = function(model) {
    //console.log("populate table:", model)
    model.waves.forEach((wave, num) => {
      let $tr = appendWaveRow(wave, num + 1)
      let $canvas = appendChartCell($tr, wave)
      let $chart = enableChart($canvas, wave)
    })
  }

  const appendWaveRow = function(wave, num) {
    const $tr = $('<tr />')
    $tr.addClass(wave.type)

    appendCell($tr, 'index', num)
    appendCell($tr, 'cycle', wave.type)
    appendCell($tr, 'start-date', wave.startedOn)
    appendCell($tr, 'end-date', wave.endedOn)
    appendCell($tr, 'days', wave.days)
    appendPeakCell($tr, wave.maxPositiveRate)
    appendCasesCell($tr, wave)
    appendHospitalizationsCell($tr, wave)
    appendDeathsCell($tr, wave)

    $tableBody.append($tr)
    return $tr
  }

  const appendCell = function($tr, className, html) {
    const $td = $('<td />')
    $td.addClass(className)
    $td.html(html)
    $tr.append($td)
    return $td
  }

  const appendPeakCell = function($tr, peak) {
    const valueHtml = `<b>${peak.value}</b>%`
    const noteHtml = `on <b>${peak.date}</b>`

    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(valueHtml)
    const $dateSpan = $('<span />').addClass('note').html(noteHtml)

    $div.append($valueSpan).append($dateSpan)
    appendCell($tr, 'peak', $div)
  }

  const appendCasesCell = function($tr, wave) {
    const dailyAvg = (wave.totalCases / wave.days).toFixed(1)
    const valueText = `<b>${dailyAvg}</b>/day`
    const noteHtml = `Total: <b>${wave.totalCases}</b>`

    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(valueText)
    const $noteSpan = $('<span />').addClass('note').html(noteHtml)

    $div.append($valueSpan).append($noteSpan)
    appendCell($tr, 'cases', $div)
  }

  const appendHospitalizationsCell = function($tr, wave) {
    const valueText = `<b>${wave.maxHospitalizations.value}</b>`
    const noteHtml = `on <b>${wave.maxHospitalizations.date}</b>`

    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(valueText)
    const $noteSpan = $('<span />').addClass('note').html(noteHtml)

    $div.append($valueSpan).append($noteSpan)
    appendCell($tr, 'hospitalizations', $div)
  }

  const appendDeathsCell = function($tr, wave) {
    const dailyAvg = (wave.totalDeaths / wave.days).toFixed(1)
    const valueText = `<b>${dailyAvg}</b>/day`
    const noteHtml = `Total: <b>${wave.totalDeaths}</b>`

    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(valueText)
    const $noteSpan = $('<span />').addClass('note').html(noteHtml)

    $div.append($valueSpan).append($noteSpan)
    appendCell($tr, 'deaths', $div)
  }

  const appendChartCell = function($tr, wave) {
    const canvasId = `mini-chart-${wave.startedOn}`
    const height = 60

    // Set widths proportional to length in days
    const maxWidth = 120
    const refDuration = 90 // days
    const canvasWidth = Math.round(wave.days / refDuration * maxWidth)

    // See https://www.chartjs.org/docs/latest/getting-started/usage.html
    const $canvas = $('<canvas />')
      .attr('id', canvasId)
      .attr('width', canvasWidth)
      .attr('height', height)

    // To center things
    const $chartWrapper = $('<div />')
      .addClass('chart-wrapper')
      .append($canvas)

    appendCell($tr, 'chart', $chartWrapper)
    return $canvas
  }

  const enableChart = function($chart, wave) {
    //console.debug('enableChart', $chart, wave)
    const waveColor = '#cb3c2c'
    const lullColor = '#f1c78a'
    const chartColor = wave.type === 'wave' ? waveColor : lullColor

    // Refer: https://www.ethangunderson.com/writing/sparklines-in-chart.js/
    const options = {
      events: [],
      responsive: false,
      borderColor: chartColor,
      backgroundColor: `${chartColor}75`,
      fill: true,
      borderWidth: 1,
      scales: {
        x: { display: false },
        y: {
          display: false,
          min: 0,
          max: 26
        }
      },
      plugins: {
        legend: {
          display: false,
          labels: { display: false }
        },
        tooltips: { display: false }
      }
    }

    const data = {
      labels: wave.datasets.dates,
      datasets: [
        {
          data: wave.datasets.avgPositiveRates,
          pointRadius: 0
        }
      ]
    }

    const config = {
      type: 'line',
      data: data,
      options: options
    }

    return new Chart($chart, config)
  }

  /*
   * Public API
   */
  return {
    render: render
  }
})()


/*
 * Main block: these are the things that happen on designated event.
**/
$(document).on(OcWavesModel.dataReady, (event, model) => {
  OcWavesTable.render(model)
})
