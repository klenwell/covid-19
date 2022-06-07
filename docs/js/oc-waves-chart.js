/*
 * OC Waves Chart Component
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
**/
class OcWavesChart {
  constructor(model) {
    this.model = model
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
  get canvas() {
    const selector = 'canvas#waves-chart'
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
    return {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          type: 'time',
          parser: 'yyyy-MM-dd'
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

    this.model.waves.forEach((wave, num) => {
      const waveColor = '#ff0000'
      const lullColor = '#e08600'
      const chartColor = wave.type === 'wave' ? waveColor : lullColor

      // Create an array of x,y maps: { x: '2017-01-06', y: 3.6 }
      let data = wave.datasets.dates.map((dated, i) => {
        let posRate = wave.datasets.avgPositiveRates[i]
        return { x: dated, y: posRate }
      })

      let dataset = {
        label: num + 1,
        borderColor: chartColor,
        backgroundColor: `${chartColor}75`,
        fill: true,
        data: data
      }

      datasets.push(dataset)
      console.log(dataset)
    })

    return datasets
  }

  /*
   * Methods
  **/
  render() {
    console.log('render chart config', this.config)
    return new Chart(this.canvas, this.config)
  }

}

/*
 * Main block: these are the things that happen on page load.
 */
 $( document ).on(OC_WAVES_MODEL_LOAD_EVENT, (event, model) => {
   console.log('event received', event, model)
   const chart = new OcWavesChart(model)
   chart.render()
 })
