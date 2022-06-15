/*
 * OcPhasesModel
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const OcPhasesModelConfig = {
  readyEvent: 'OcPhasesModel:data:ready',
  extractUrl: 'data/json/oc/phases.json'
}


class OcPhasesModel {
  constructor(config) {
    this.config = config
    this.phases = []
    this.meta = {}
    this.url = config.extractUrl
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
  // For use by component as on event string to confirm data loaded:
  // $(document).on(OcWavesModel.dataReady, (event, model) => {})
  static get dataReady() {
    return OcPhasesModelConfig.readyEvent
  }

  get phaseNotes() {
    const urls = {
      'Alpha': 'https://en.wikipedia.org/wiki/SARS-CoV-2_Alpha_variant',
      'Delta': 'https://en.wikipedia.org/wiki/SARS-CoV-2_Delta_variant',
      'Omicron': 'https://en.wikipedia.org/wiki/SARS-CoV-2_Omicron_variant',
      'Omicron 2': 'https://en.wikipedia.org/wiki/SARS-CoV-2_Omicron_variant#Sublineages_and_BA.2_subvariant'
    }

    const link = (variant) => {
      const href = urls[variant]
      return `<a class="variant" target="_blank" href="${href}">${variant}</a>`
    }

    return {
      // index: note (html)
      1: 'First Wave',
      2: 'CA Stay-at-Home Order Drop',
      3: 'Summer Re-Opening Surge',
      4: 'CA Indoor Dining Shutdown Drop',
      5: 'Autumn Lull',
      6: `Holiday ${link('Alpha')} Surge`,
      7: 'Post-Alpha Drop',
      8: 'Spring "Hot Vax Summer" Lull',
      9: `Summer ${link('Delta')} Surge`,
      10: 'Post-Delta Drop',
      11: 'Autumn Lull',
      12: `Holiday ${link('Omicron')} Surge`,
      13: 'Post-Omicron Drop',
      14: 'Spring Lull',
      15: `Summer ${link('Omicron 2')} Surge<br />(Ongoing)`,
    }
  }

  get completePhases() {
    return this.phases.slice(0, -1)
  }

  get activePhase() {
    return this.phases.slice(-1)
  }

  get risingPhases() {
    return this.completePhases.filter((phase) => phase.trend === 'rising')
  }

  get fallingPhases() {
    return this.completePhases.filter((phase) => phase.trend === 'falling')
  }

  get flatPhases() {
    return this.completePhases.filter((phase) => phase.trend === 'flat')
  }

  get averageDurations() {
    const risingDurations = this.risingPhases.map((phase) => phase.days)
    const fallingDurations = this.fallingPhases.map((phase) => phase.days)
    const flatDurations = this.flatPhases.map((phase) => phase.days)

    const sum = (arr) => arr.reduce((acc, n) => acc + n, 0)
    const avg = (arr) => sum(arr) / arr.length

    return {
      rising: avg(risingDurations),
      falling: avg(fallingDurations),
      flat: avg(flatDurations)
    }
  }

  /*
   * Public Methods
  **/
  fetchData() {
    fetch(this.url)
      .then(response => response.json())
      .then(data => this.onFetchComplete(data))
  }

  /*
   * Private Methods
  **/
  onFetchComplete(jsonData) {
    this.phases = jsonData.phases
    this.meta = jsonData.meta
    this.triggerReadyEvent()
  }

  triggerReadyEvent() {
    console.log(this.config.readyEvent, this)
    $(document).trigger(this.config.readyEvent, [this])
  }
}


/*
 * Main block: these are the things that happen on page load.
**/
$(document).ready(function() {
  const model = new OcPhasesModel(OcPhasesModelConfig)
  model.fetchData()
})