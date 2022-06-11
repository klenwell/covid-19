/*
 * OC Phases Chart Component
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
**/
class OcPhasesChart {
  constructor(model) {
    this.model = model
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
  get canvas() {
    const selector = 'canvas#phases-chart'
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

    const yTickFormatter = (value, index, ticks) => {
      return value % 5 === 0 ? `${value}%` : ''
    }

    const phaseAnnotations = this.annotations

    return {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: 'time',
          parser: 'yyyy-MM-dd',
          grid: { display: false },
          ticks: {
            stepSize: 2,
            callback: (value, index, ticks) => index % 2 === 0 ? value : ''
          }
        },
        y: {
          max: 28,
          min: 0,
          title: {
            display: true,
            text: 'Test Positive Rate'
          },
          ticks: {
            stepSize: 5,
            callback: (value, index, ticks) => value % 5 === 0 ? `${value}%` : ''
          }
        }
      },
      plugins: {
        legend: {
          display: false,
          position: 'left',
          labels: { usePointStyle: true }
        },
        tooltip: {
          callbacks: {
            title: tooltipTitleFormatter,
            label: ctx => `Positive Rate: ${ctx.formattedValue}%`
          }
        },
        annotation: {
          annotations: phaseAnnotations
        }
      }
    }
  }

  get annotations() {
    let annotations = {}

    this.model.phases.forEach((phase, num) => {
      let index = num + 1
      let annotationKey = `line${index}`
      let valueIndex = parseInt(Math.round(phase.datasets.dates.length / 2)) - 1
      let value = phase.datasets.dates[valueIndex]

      // Add spaces to single digits allow space for border radius to expand to circle.
      let labelContent = index < 10 ? ` ${index} ` : index

      let phaseAnnotation = {
        type: 'line',
        scaleID: 'x',
        value: value,
        borderColor: '#ccc',
        borderWidth: 0,
        label: {
          enabled: true,
          position: "85%",
          content: labelContent,
          backgroundColor: this.mapTrendToColor(phase.trend),
          borderRadius: 12
        }
      }

      annotations[annotationKey] = phaseAnnotation
    })

    return annotations
  }

  get data() {
    return {
      datasets: this.datasets
    }
  }

  get datasets() {
    let datasets = []
    const opacity = 75

    this.model.phases.forEach((phase, num) => {
      const chartColor = this.mapTrendToColor(phase.trend)

      // Create an array of x,y maps: { x: '2017-01-06', y: 3.6 }
      let data = phase.datasets.dates.map((dated, i) => {
        let posRate = phase.datasets.avgPositiveRates[i]
        return { x: dated, y: posRate }
      })

      // Refer: https://www.chartjs.org/docs/next/samples/scales/time-line.html
      let dataset = {
        label: num + 1,
        borderColor: chartColor,
        backgroundColor: `${chartColor}${opacity}`,
        fill: true,
        borderWidth: 1,
        pointStyle: 'circle',
        pointRadius: 0,
        pointHoverRadius: 8,
        data: data
      }

      datasets.push(dataset)
    })

    return datasets
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

}


/*
 * Main block: these are the things that happen on designated event.
**/
$(document).on(OcPhasesModel.dataReady, (event, model) => {
  const chart = new OcPhasesChart(model)
  chart.render()
})
