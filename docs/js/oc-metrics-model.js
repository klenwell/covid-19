/*
 * OcMetricsModel
 *
 * This is really as much a decorator or view helper as a data model.
 *
 * TODO: Move helper methods to metrics table component: oc-metrics-table.js
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const OcMetricsModelConfig = {
  readyEvent: 'OcMetricsModel:data:ready',
  extractUrl: 'data/json/oc/metrics.json'
}


class OcMetricsModel {
  constructor(config) {
    this.config = config
    this.data = {}
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
  // For use by component as on event string to confirm data loaded:
  // $(document).on(OcMetricsModel.dataReady, (event, model) => {})
  static get dataReady() {
    return OcMetricsModelConfig.readyEvent
  }

  get cases() {
    const metric = this.data.dailyNewCases
    const postfix = '/day'
    return this.mapMetric(metric, postfix)
  }

  get positiveRate() {
    const metric = this.data.testPositiveRate
    const postfix = '%'
    return this.mapMetric(metric, postfix)
  }

  get wastewater() {
    const metric = this.data.wastewater
    const postfix = '/day'
    return this.mapMetric(metric, postfix)
  }

  get hospitalCases() {
    const metric = this.data.hospitalCases
    const postfix = '/day'
    return this.mapMetric(metric, postfix)
  }

  get icuCases() {
    const metric = this.data.icuCases
    const postfix = '/day'
    return this.mapMetric(metric, postfix)
  }

  get deaths() {
    const metric = this.data.deaths
    const postfix = '/day'
    return this.mapMetric(metric, postfix)
  }

  /*
   * Public Methods
  **/
  fetchData() {
    fetch(this.config.extractUrl)
      .then(response => response.json())
      .then(data => this.onFetchComplete(data))
  }

  /*
   * Private Methods
  **/
  onFetchComplete(jsonData) {
    this.data = jsonData
    this.triggerReadyEvent()
  }

  triggerReadyEvent() {
    console.log(this.config.readyEvent, this)
    $(document).trigger(this.config.readyEvent, [this])
  }

  mapMetric(metric, postfix) {
    const level = this.mapLevel(metric.percentile)
    const percentileOrd = this.mapOrd(metric.percentile)
    const trend = this.mapTrend(metric)

    const html = {
      updatedOn: metric.updatedOn,
      latest: `${metric.latest}<span class="postfix">${postfix}</span>`,
      level: level,
      levelNote: `${metric.percentile.toFixed(0)}<span class="postfix">${percentileOrd} percentile</span>`,
      trend: trend,
      delta7dValue: this.asSignedPct(metric.d7DeltaPct),
      delta7dNote: this.asFromNote(metric.d7Value, postfix),
      delta14dValue: this.asSignedPct(metric.d14DeltaPct),
      delta14dNote: this.asFromNote(metric.d14Value, postfix)
    }

    const tdClass = {
      level: level.replace(/\s/g , "-"),
      trend: trend,
    }

    return {
      data: metric,
      html: html,
      tdClass: tdClass
    }
  }

  asSignedPct(value) {
    if ( !value ) {
      return 'n/a'
    }
    const sign = value > 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}%`
  }

  asFromNote(value, postfix) {
    return `from ${value}<span class="postfix">${postfix}</span>`
  }

  mapLevel(percentile) {
    if (percentile <= 25) {
      return 'low'
    }
    else if (percentile > 25 && percentile <= 50) {
      return 'moderate'
    }
    else if (percentile > 50 && percentile <= 75) {
      return 'high'
    }
    else {
      return 'very high'
    }
  }

  mapTrend(metric) {
    if ( metric.d7DeltaPct > 10 && metric.d14DeltaPct < -10 ) {
      return 'erratic'
    }
    else if ( metric.d7DeltaPct < -10 && metric.d14DeltaPct > 10 ) {
      return 'erratic'
    }
    else if ( metric.d7DeltaPct >= 2.5 ) {
      return 'rising'
    }
    else if ( metric.d7DeltaPct <= -2.5 ) {
      return 'falling'
    }
    else {
      return 'flat'
    }
  }

  mapOrd(num) {
    // https://stackoverflow.com/a/39466341/1093087
    const n = Math.round(num)
    return [,'st','nd','rd'][n/10%10^1&&n%10]||'th'
  }
}


/*
 * Main block: these are the things that happen on page load.
**/
$(document).ready(function() {
  const model = new OcMetricsModel(OcMetricsModelConfig)
  model.fetchData()
})
