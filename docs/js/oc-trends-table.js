/*
 * OC Trends Table Component
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
class OcTrendsTable {
  constructor(model) {
    const selector = 'section#oc-covid-trends table'

    this.model = model
    this.dateTime = luxon.DateTime
    this.table = $(selector)
    this.tableBody = this.table.find('tbody')
  }

  /*
   * Getters
  **/
  get weekLabels() {
    return [
      'Last Week*',
      '2 Weeks Ago',
      '3 Weeks Ago',
      '4 Weeks Ago'
    ]
  }

  /*
   * Methods
  **/
  resetTable() {
    const extractUrl = OcTrendsModelConfig.extractUrl
    this.table.find('caption').text(`Loading data from ${extractUrl}`)
  }

  render() {
    this.table.find('caption').html('')

    this.weekLabels.forEach((label, idx) => {
      let week = this.model.weeks[idx]
      let $tr = this.weekRow(label, week, idx + 1)
      this.tableBody.append($tr)
    })
  }

  weekRow(label, week, weekNum) {
    const className = `week-${weekNum}`
    const $tr = $('<tr />').addClass(className)

    $tr.append(this.labelCell(label))
    $tr.append(this.rateCell(week.testPositiveRate))
    $tr.append(this.avg7dCell('admin-tests', week.adminTests))
    $tr.append(this.avg7dCell('positive-tests', week.positiveTests))
    $tr.append(this.avg7dCell('wastewater', week.wastewater))
    $tr.append(this.avg7dCell('hospital-cases', week.hospitalCases))
    $tr.append(this.deathCell(week.deaths))
    $tr.append(this.dateCell(week.endDate))
    $tr.append(this.dateCell(week.startDate))

    return $tr
  }

  valueDeltaCell(className, value, delta) {
    const trendClass = this.mapDeltaToTrend(delta)
    const $td = $('<td />').addClass(className).addClass(trendClass)
    const deltaHtml = `(${this.fmtSignedPct(delta)})`
    const $valueSpan = $('<span />').addClass('value').html(value)
    const $deltaSpan = $('<span />').addClass('delta').html(deltaHtml)
    $td.append($valueSpan).append($deltaSpan)
    return $td
  }

  avg7dCell(className, metric, precision) {
    const value = this.fmtNum(metric.average7d, precision)
    return this.valueDeltaCell(className, value, metric.delta)
  }

  labelCell(label) {
    return $('<th />').attr('scope', 'row').html(label)
  }

  dateCell(date) {
    const $td = $('<td />').addClass('date')
    $td.html(date)
    return $td
  }

  rateCell(rate) {
    const value = this.fmtPct(rate.value)
    return this.valueDeltaCell('test-positive-rate', value, rate.delta)
  }

  deathCell(deaths) {
    return this.valueDeltaCell('deaths', deaths.total, deaths.delta)
  }

  fmtNum(value, precision) {
    const locale = 'en-US'
    const fixed = precision !== undefined ? precision : 1
    const config = {
      maximumFractionDigits: fixed,
      minimumFractionDigits: fixed
    }
    const nonVal = 'n/a'
    return this.isNum(value) ? value.toLocaleString(locale, config) : nonVal
  }

  fmtPct(value) {
    if ( ! this.isNum(value) ) {
      return 'n/a'
    }
    return `${this.fmtNum(value, 1)}%`
  }

  fmtSignedPct(value) {
    if ( ! this.isNum(value) ) {
      return 'n/a'
    }
    const sign = value > 0 ? '+' : '';
    return `${sign}${this.fmtNum(value, 1)}%`
  }

  mapDeltaToTrend(delta) {
    if (isNaN(delta)) {
      return 'nan'
    }
    else if (delta > 0) {
      return 'rising'
    }
    else if (delta < 0) {
      return 'falling'
    }
    else {
      return 'flat'
    }
  }

  isNum(value) {
    // Why? See https://stackoverflow.com/q/115548/1093087
    if ( value === null ) {
      return false
    }

    return !isNaN(value)
  }
}


/*
 * Main block: these are the things that happen on designated event.
**/
$(document).on(OcTrendsModel.dataReady, (event, model) => {
  const table = new OcTrendsTable(model)
  table.render()
})

$(document).ready(function() {
  const table = new OcTrendsTable(null)
  table.resetTable()
})
