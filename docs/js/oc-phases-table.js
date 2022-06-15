/*
 * OC Phases Table Component
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
class OcPhasesTable {
  constructor(model) {
    const selector = 'section#oc-covid-phases table'

    this.model = model
    this.dateTime = luxon.DateTime
    this.formatNumber = new Intl.NumberFormat('en-US').format;
    this.table = $(selector)
    this.tableBody = this.table.find('tbody')
  }

  /*
   * Getters
  **/

  /*
   * Methods
  **/
  render() {
    this.table.find('caption').html('')

    this.model.phases.forEach((phase, num) => {
      let $tr = this.indexedRow(phase, num + 1)
      this.tableBody.append($tr)
    })
  }

  indexedRow(phase, index) {
    const $tr = $('<tr />').addClass(phase.trend)
    const $chartCanvas = this.chartCanvas(phase)

    $tr.append(this.indexCell(index))
    $tr.append(this.classCell('trend', phase.trend))
    $tr.append(this.classCell('start-date', phase.startedOn))
    $tr.append(this.classCell('end-date', phase.endedOn))
    $tr.append(this.classCell('days', phase.days))
    $tr.append(this.positiveRateCell(phase))
    $tr.append(this.popSlopeCell(phase.popSlope))
    $tr.append(this.notesCell(index))
    $tr.append(this.chartCell($chartCanvas))

    this.enableChart($chartCanvas, phase)
    return $tr
  }

  classCell(className, html) {
    const $td = $('<td />')
    $td.addClass(className)
    $td.html(html)
    return $td
  }

  indexCell(indexNum) {
    const $td = $('<td />').addClass('index')
    const $span = $('<span />').addClass('circled').html(indexNum)
    $td.append($span)
    return $td
  }

  positiveRateCell(phase) {
    const startRate = phase.startPositiveRate.toFixed(1)
    const endRate = phase.endPositiveRate.toFixed(1)
    const valueHtml = `<b>${startRate}</b>% &#10145; <b>${endRate}</b>%`

    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(valueHtml)

    $div.append($valueSpan)
    return this.classCell('rate', $div)
  }

  popSlopeCell(popSlope) {
    // https://stackoverflow.com/a/32154217/1093087
    const slope = this.formatNumber(popSlope.toFixed(1))
    const valueText = `<b>${slope}</b>/day`

    const $div = $('<div />')
    const $valueSpan = $('<span />').addClass('value').html(valueText)

    $div.append($valueSpan)
    return this.classCell('slope', $div)
  }

  notesCell(index) {
    const note = this.model.phaseNotes[index]
    return this.classCell('notes', note)
  }

  chartCell($canvas) {
    // To center things
    const $chartWrapper = $('<div />')
      .addClass('chart-wrapper')
      .append($canvas)

    return this.classCell('chart', $chartWrapper)
  }

  chartCanvas(phase) {
    const canvasId = `phase-mini-chart-${phase.startedOn}`
    const height = 60

    // Set widths proportional to length in days
    const maxWidth = 120
    const refDuration = 90 // days
    const canvasWidth = Math.round(phase.days / refDuration * maxWidth)

    const $canvas = $('<canvas />')
      .attr('id', canvasId)
      .attr('width', canvasWidth)
      .attr('height', height)

    return $canvas
  }

  enableChart($canvas, phase) {
    const chartColor = this.mapTrendToColor(phase.trend)
    const scales = {
      x: { display: false },
      y: {
        display: false,
        min: 0,
        max: 26
      }
    }
    const plugins = {
      legend: {
        display: false,
        labels: { display: false }
      },
      tooltips: { display: false }
    }

    // Refer: https://www.ethangunderson.com/writing/sparklines-in-chart.js/
    const options = {
      events: [],
      responsive: false,
      borderColor: chartColor,
      backgroundColor: `${chartColor}75`,
      fill: true,
      borderWidth: 1,
      scales: scales,
      plugins: plugins
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

  mapTrendToColor(trend) {
    const colorMap = {
      rising: '#cb3c2c',
      flat: '#f1c78a',
      falling: '#1967d2'
    }
    return colorMap[trend]
  }
}


/*
 * Event block: these are the things that happen on designated event.
**/
$(document).on(OcPhasesModel.dataReady, (event, model) => {
  const table = new OcPhasesTable(model)
  table.render()
})
