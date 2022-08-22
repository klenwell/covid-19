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
        legend: { display: false },
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

    return {
      x: xScale,
      y: this.yAxes
    }
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
    console.log('caseSeries', this.model.caseSeries)
    return [
      this.configureDataset('wastewater', this.model.wastewaterSeries, 'brown'),
      this.configureDataset('positive-rate', this.model.positiveRateSeries, 'red'),
      this.configureDataset('cases', this.model.caseSeries, 'orange'),
      this.configureDataset('hospital-cases', this.model.hospitalCaseSeries, 'purple'),
    ]
  }

  configureDataset(id, data, borderColor) {
    return {
      label: id,
      yAxisID: id,
      borderColor: borderColor,
      backgroundColor: 'white',
      data: data,
      fill: false,
      borderWidth: 1,
      pointStyle: 'circle',
      pointRadius: 0,
      pointHoverRadius: 8,
    }
  }

  get yAxes() {
    return {
      'wastewater': this.configureYScale('wastewater', 'left', 'brown'),
      'positive-rate': this.configureYScale('positive-rate', 'left', 'red'),
      'cases': this.configureYScale('cases', 'right', 'orange'),
      'hospital-cases': this.configureYScale('hospital-cases', 'right', 'purple')
    }
  }

  configureYScale(id, position, color) {
    const max = this.model.maxValues[id]
    const stepSize = max / 5
    const smoothStepSize = Math.ceil(stepSize)
    const smoothMax = smoothStepSize * 5
    console.log(id, smoothStepSize, smoothMax, position)

    return {
      axis: 'y',
      type: 'linear',
      grace: 0,
      position: position,
      min: 0,
      max: smoothMax,
      ticks: {
        stepSize: smoothStepSize,
        color: color
      }
    }
  }

  /*
   * Methods
  **/
  render() {
    return new Chart(this.canvas, this.config)
  }

  mapTrendToColor(trend) {
    const colorMap = {
      rising: '#cb3c2c',
      flat: '#f1c78a',
      falling: '#1967d2'
    }
    return colorMap[trend]
  }

  lineAnnotationForYear(year) {
    const labelColor = "#e08600"
    const lineColor = "#CCCCCC"
    const value = `${year}-01-01`

    return {
      type: 'line',
      scaleID: 'x',
      value: value,
      borderColor: lineColor,
      borderWidth: 3,
      drawTime: 'beforeDatasetsDraw',
      label: {
        enabled: true,
        position: "2%",
        content: year,
        backgroundColor: labelColor,
        borderRadius: 12
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
