/*
 * OcMetricsModel
 *
 * This is really more a decorator or helper module than a data model.
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
 */

 class OcMetricsModel {
  constructor(jsonData) {
    this.data = jsonData
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
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
   * Methods
  **/
  mapMetric(metric, postfix) {
    const level = this.mapLevel(metric.percentile)
    const trend = this.mapTrend(metric)

    const html = {
      updatedOn: metric.updatedOn,
      latest: `${metric.latest}<span class="postfix">${postfix}</span>`,
      level: level,
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
    if (metric.d7DeltaPct >= 2.5) {
      return 'rising'
    }
    else if ( (metric.d7DeltaPct <= -2.5) ) {
      return 'falling'
    }
    else {
      return 'flat'
    }
  }
}
