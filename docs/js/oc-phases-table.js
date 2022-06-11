/*
 * OC Phases Table Component
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
**/
const OcPhasesTable = (function() {
  /*
   * Constants
   */
  const SELECTOR = 'section#oc-covid-phases table'

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
    model.phases.forEach((phase, num) => {
      let $tr = appendRow(phase, num + 1)
      let $canvas = appendChartCell($tr, phase)
      let $chart = enableChart($canvas, phase)
    })
  }

  const appendRow = function(phase, num) {
    const $tr = $('<tr />')
    $tr.addClass(phase.trend)

    appendCell($tr, 'index', num)
    appendCell($tr, 'trend', phase.trend)
    appendCell($tr, 'start-date', phase.startedOn)
    appendCell($tr, 'end-date', phase.endedOn)
    appendCell($tr, 'days', phase.days)
    appendPositveRateCell($tr, phase)
    appendPopSlopeCell($tr, phase.popSlope)
    appendNotesCell($tr, phase)

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

  const appendPositveRateCell = function($tr, phase) {
    const startRate = phase.startPositiveRate.toFixed(1)
    const endRate = phase.endPositiveRate.toFixed(1)
    const valueHtml = `<b>${startRate}</b>% &#10145; <b>${endRate}</b>%`

    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(valueHtml)

    $div.append($valueSpan)
    appendCell($tr, 'rate', $div)
  }

  const appendPopSlopeCell = function($tr, popSlope) {
    // https://stackoverflow.com/a/32154217/1093087
    const nf = new Intl.NumberFormat('en-US');
    const valueText = `<b>${nf.format(popSlope.toFixed(1))}</b>/day`


    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(valueText)

    $div.append($valueSpan)
    appendCell($tr, 'slope', $div)
  }

  const appendNotesCell = function($tr, wave) {
    const $div = $('<div />')
    // TODO
    appendCell($tr, 'notes', $div)
  }

  const appendChartCell = function($tr, phase) {
    const canvasId = `phase-mini-chart-${phase.startedOn}`
    const height = 60

    // Set widths proportional to length in days
    const maxWidth = 120
    const refDuration = 90 // days
    const canvasWidth = Math.round(phase.days / refDuration * maxWidth)

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

  const enableChart = function($chart, phase) {
    //console.debug('enableChart', $chart, phase)
    const colorMap = {
      rising: '#ff0000',
      flat: '#e08600',
      falling: '#aecbfa'
    }
    const chartColor = colorMap[phase.trend]

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
      labels: phase.datasets.dates,
      datasets: [
        {
          data: phase.datasets.avgPositiveRates,
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
$(document).on(OcPhasesModel.dataReady, (event, model) => {
  OcPhasesTable.render(model)
})
