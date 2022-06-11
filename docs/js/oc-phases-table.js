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
  const $tableBody = $(SELECTOR).find('tbody')

  /*
   * Public Methods
   */
  const render = function(model) {
    $(SELECTOR).find('caption').html('')
    populate(model)
  }

  /*
   * Private Methods
   */
  const populate = function(model) {
    //console.log("populate table:", model)
    model.phases.forEach((phase, num) => {
      let $tr = indexedRow(phase, num + 1)
      let $canvas = appendChartCell($tr, phase)
      $tableBody.append($tr)
      enableChart($canvas, phase)
    })
  }

  const indexedRow = function(phase, num) {
    const $tr = $('<tr />').addClass(phase.trend)

    $tr.append(indexCell(num))
    $tr.append(classCell('trend', phase.trend))
    $tr.append(classCell('start-date', phase.startedOn))
    $tr.append(classCell('end-date', phase.endedOn))
    $tr.append(classCell('days', phase.days))
    $tr.append(positiveRateCell(phase))
    $tr.append(popSlopeCell(phase.popSlope))
    $tr.append(notesCell(phase))

    return $tr
  }

  const classCell = function(className, html) {
    const $td = $('<td />')
    $td.addClass(className)
    $td.html(html)
    return $td
  }

  const indexCell = function(num) {
    const $td = $('<td />').addClass('index')
    const $span = $('<span />').addClass('circled').html(num)
    $td.append($span)
    return $td
  }

  const positiveRateCell = function(phase) {
    const startRate = phase.startPositiveRate.toFixed(1)
    const endRate = phase.endPositiveRate.toFixed(1)
    const valueHtml = `<b>${startRate}</b>% &#10145; <b>${endRate}</b>%`

    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(valueHtml)

    $div.append($valueSpan)
    return classCell('rate', $div)
  }

  const popSlopeCell = function(popSlope) {
    // https://stackoverflow.com/a/32154217/1093087
    const nf = new Intl.NumberFormat('en-US');
    const valueText = `<b>${nf.format(popSlope.toFixed(1))}</b>/day`

    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(valueText)

    $div.append($valueSpan)
    return classCell('slope', $div)
  }

  const notesCell = function(wave) {
    const $div = $('<div />')
    // TODO
    return classCell('notes', $div)
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

    $tr.append(classCell('chart', $chartWrapper))
    return $canvas
  }

  const enableChart = function($canvas, phase) {
    //console.debug('enableChart', $chart, phase)
    const colorMap = {
      rising: '#cb3c2c',
      flat: '#f1c78a',
      falling: '#1967d2'
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

    return new Chart($canvas, config)
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
