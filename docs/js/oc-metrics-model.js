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
    return {
      updatedOn: metric.updatedOn,
      latest: metric.latest,
      level: this.computeLevel(metric.percentile),
      trend: this.computeTrend(metric),
      delta7dValue: metric.d7Value,
      delta7dDelta: metric.d7DeltaPct,
      delta14dValue: metric.d14Value,
      delta14dDelta: metric.d14DeltaPct
    }
  }

  get positiveRate() {
    const metric = this.data.testPositiveRate
    return {
      updatedOn: metric.updatedOn,
      latest: metric.latest,
      level: this.computeLevel(metric.percentile),
      trend: this.computeTrend(metric),
      delta7dValue: metric.d7Value,
      delta7dDelta: metric.d7DeltaPct,
      delta14dValue: metric.d14Value,
      delta14dDelta: metric.d14DeltaPct
    }
  }

  get wastewater() {
    const metric = this.data.wastewater
    return {
      updatedOn: metric.updatedOn,
      latest: metric.latest,
      level: this.computeLevel(metric.percentile),
      trend: this.computeTrend(metric),
      delta7dValue: metric.d7Value,
      delta7dDelta: metric.d7DeltaPct,
      delta14dValue: metric.d14Value,
      delta14dDelta: metric.d14DeltaPct
    }
  }

  /*
   * Methods
  **/
  computeLevel(percentile) {
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

  computeTrend(metric) {
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
