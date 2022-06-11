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
      const label = context.dataset.label.split(' ')
      const date = this.dateTime.fromSeconds(context.parsed.x / 1000).toFormat(dateF)
      const day = context.dataIndex + 1
      const title = `${date}: day ${day} of ${label[1]}`
      //console.log('tooltipTitleFormatter', title, context)
      return title
    }

    const yTickFormatter = (value, index, ticks) => {
      return value % 5 === 0 ? `${value}%` : ''
    }

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
        }
      }
    }
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
      const colorMap = {
        rising: '#cb3c2c',
        flat: '#f1c78a',
        falling: '#1967d2'
      }
      const chartColor = colorMap[phase.trend]

      // Create an array of x,y maps: { x: '2017-01-06', y: 3.6 }
      let data = phase.datasets.dates.map((dated, i) => {
        let posRate = phase.datasets.avgPositiveRates[i]
        return { x: dated, y: posRate }
      })

      // Refer: https://www.chartjs.org/docs/next/samples/scales/time-line.html
      let dataset = {
        label: `(${num + 1}) ${phase.trend}`,
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

}


/*
 * Main block: these are the things that happen on designated event.
**/
$(document).on(OcPhasesModel.dataReady, (event, model) => {
  const chart = new OcPhasesChart(model)
  chart.render()
})
