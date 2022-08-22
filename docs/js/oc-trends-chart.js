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
    const yScale = {
      yAxes: [{
        id: 'wastewater',
        type: 'linear',
        position: 'left',
        ticks: {
          min: 0,
          max: this.model.maxValues.wastewater,
          //stepSize: 20,
          fontColor: 'brown'
        }
      }, {
        id: 'positive-rate',
        type: 'linear',
        position: 'left',
        ticks: {
          min: 0,
          max: this.model.maxValues['positive-rate'],
          //stepSize: 20,
          fontColor: 'orange'
        }
      }]
    }

    return {
      yAxes: yScale
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
    console.log('positiveRateSeries', this.model.positiveRateSeries)
    return [{
      label: 'wastewater',
      yAxisID: 'wastewater',
      borderColor: 'brown',
      backgroundColor: 'white',
      data: this.model.wastewaterSeries,
      fill: false,
      borderWidth: 1,
      pointStyle: 'circle',
      pointRadius: 0,
      pointHoverRadius: 8,
    }, {
      label: 'positive rate',
      yAxisID: 'positive-rate',
      borderColor: 'orange',
      backgroundColor: 'white',
      data: this.model.positiveRateSeries,
      fill: false,
      borderWidth: 1,
      pointStyle: 'circle',
      pointRadius: 0,
      pointHoverRadius: 8,
    }]
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
