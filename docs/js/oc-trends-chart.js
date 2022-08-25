/*
 * OC Trends Chart Component
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
class OcTrendsChart {
  constructor(model) {
    this.model = model
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
  get canvas() {
    const selector = 'canvas#trends-chart'
    return $(selector)
  }

  // Refer: https://stackoverflow.com/a/48143738/1093087
  get config() {
    console.log('scales', this.scales)
    console.log('options', this.options)
    return {
      type: 'line',
      data: this.data,
      options: this.options
    }
  }

  get options() {
    const scales = this.scales
    const annotations = this.annotations
    const tooltip = this.tooltip

    return {
      responsive: true,
      maintainAspectRatio: false,
      scales: scales,
      plugins: {
        legend: { display: true },
        //annotation: { annotations: annotations },
        //tooltip: tooltip
      }
    }
  }

  get scales() {
    const xScale = {
      type: 'time',
      parser: 'yyyy-MM-dd',
      grid: { display: false },
      ticks: {
        stepSize: 2,
        callback: (value, index, ticks) => index % 2 === 0 ? value : ''
      }
    }

    let scales = this.yAxes
    scales['x'] = xScale
    return scales
  }

  get annotations() {
    let annotations = {}
    return {}
  }

  get tooltip() {
    const tooltipTitleFormatter = (contexts) => {
      const dateF = 'MMMM d, yyyy'
      const context = contexts[0]
      const label = context.dataset.label
      const date = this.dateTime.fromSeconds(context.parsed.x / 1000).toFormat(dateF)
      const day = context.dataIndex + 1
      const title = `${date}: day ${day} of phase ${label}`
      //console.log('tooltipTitleFormatter', title, context)
      return title
    }

    return {
      callbacks: {
        title: tooltipTitleFormatter,
        label: ctx => `Positive Rate: ${ctx.formattedValue}%`
      }
    }
  }

  get data() {
    return {
      labels: this.model.dates,
      datasets: this.datasets
    }
  }

  get datasets() {
    return [
      this.configureDataset('wastewater', this.model.wastewaterSeries, '#3377ff'),
      this.configureDataset('positive-rate', this.model.positiveRateSeries, '#ff9933'),
      this.configureDataset('cases', this.model.caseSeries, '#527a7a'),
      this.configureDataset('hospital-cases', this.model.hospitalCaseSeries, '#e60000'),
      this.configureDataset('icu-cases', this.model.icuCaseSeries, '#800080'),
      this.configureDataset('deaths', this.model.deathSeries, '#000000'),
    ]
  }

  get yAxes() {
    return {
      'wastewater': this.configureYScale('wastewater', 'left', '#3377ff', 'virus/ml'),
      'positive-rate': this.configureYScale('positive-rate', 'left', '#ff9933', '%'),
      'cases': this.configureYScale('cases', 'left', '#527a7a'),
      'hospital-cases': this.configureYScale('hospital-cases', 'right', '#e60000'),
      'icu-cases': this.configureYScale('icu-cases', 'right', '#800080'),
      'deaths': this.configureYScale('deaths', 'right', '#000000')
    }
  }

  /*
   * Methods
  **/
  render() {
    return new Chart(this.canvas, this.config)
  }

  configureDataset(id, data, color) {
    const opacity = 10
    const backgroundColor = `${color}${opacity}`

    return {
      label: id,
      yAxisID: id,
      borderColor: color,
      backgroundColor: backgroundColor,
      data: data,
      fill: 'origin',
      borderWidth: 2,
      pointStyle: 'circle',
      pointRadius: 0,
      pointHoverRadius: 8,
      grid: { display: false },
    }
  }

  configureYScale(id, position, color, tickLabel) {
    const max = this.model.maxValues[id]
    const tickCount = 5
    const stepSize = (max * 1.05) / tickCount
    const smoothStepSize = Math.ceil(stepSize)
    const smoothMax = smoothStepSize * tickCount

    let tickCallback = (value, index, _) => (index == 0) ? 'per day' : value

    if ( tickLabel == '%' ) {
      tickCallback = (value, index, _) => `${value}%`
    }
    else if ( tickLabel == 'virus/ml' ) {
      tickCallback = (value, index, _) => (index == 0) ? tickLabel : value
    }

    return {
      axis: 'y',
      type: 'linear',
      position: position,
      min: 0,
      max: smoothMax,
      ticks: {
        count: tickCount,
        stepSize: smoothStepSize,
        color: color,
        callback: tickCallback
      }
    }
  }
}


/*
 * Main block: these are the things that happen on designated event.
**/
$(document).on(OcTimeSeriesModel.dataReady, (event, model) => {
  const chart = new OcTrendsChart(model)
  chart.render()
})
