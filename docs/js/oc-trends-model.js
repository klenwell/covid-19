/*
 * OcTrendsModel
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
// Need to use this IIFE module pattern to interpolate sheetID string.
// Usage: OcTrendsModelConfig.readyEvent
const OcTrendsModelConfig = (function() {
  const readyEvent = 'OcTrendsModel:data:ready'
  const sheetID = '1M7BfyPuwHQiavFtH59sgI9lJ7HjBpjXdBB-5BWv15K4'
  const csvUrl = `https://docs.google.com/spreadsheets/d/${sheetID}/gviz/tq?tqx=out:csv&sheet=Data`

  return {
    readyEvent: readyEvent,
    csvUrl: csvUrl
  }
})()


class OcTrendsModel {
  constructor(config) {
    this.config = config
    this.csvRows = []
    this.url = config.csvUrl
    this.csv = Papa
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
  // For use by component as on event string to confirm data loaded:
  // $(document).on(OcTrendsModel.dataReady, (event, model) => {})
  static get dataReady() {
    return OcTrendsModelConfig.readyEvent
  }

  get weeks() {
    return [
      this.datedRows[this.weekDates[0]],
      this.datedRows[this.weekDates[1]],
      this.datedRows[this.weekDates[2]],
      this.datedRows[this.weekDates[3]],
      this.datedRows[this.weekDates[4]]
    ]
  }

  get weekDates() {
    return [
      this.trendRows[0].date,
      this.trendRows[7].date,
      this.trendRows[14].date,
      this.trendRows[21].date,
      this.trendRows[28].date
    ]
  }

  get trendRows() {
    const trendRows = this.filterTrendRows(this.csvRows)
    return this.computeTrends(trendRows)
  }

  get datedRows() {
    let datedRows = {}

    for (const row of this.trendRows) {
      datedRows[row.date] = row
    }

    return datedRows
  }

  /*
   * Public Methods
  **/
  fetchData() {
    const papaConfig = {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      download: true,
      complete: (results) => this.onFetchComplete(results),
      error: (err, file) => this.onFetchError(err, file)
    }

    this.csv.parse(this.url, papaConfig)
  }

  static computePctChange(oldValue, newValue) {
    if ( !oldValue || !newValue ) {
      return undefined
    }
    return ((newValue - oldValue) / oldValue) * 100
  }

  /*
   * Private Methods
  **/
  onFetchComplete(results) {
    this.csvRows = results.data
    this.triggerReadyEvent()
  }

  onFetchError(err, file) {
    const message = `OcTrendsModel error: ${err} (file: ${file})`
    console.error(message)
  }

  triggerReadyEvent() {
    console.log(this.config.readyEvent, this)
    $(document).trigger(this.config.readyEvent, [this])
  }

  filterTrendRows(rows) {
    let filteredRows = []
    const maxRows = 35

    for (const row of rows) {
      let isValid = !!row['Date'] && !!row['Test Pos Rate 7d Avg']

      if ( !isValid ) {
        continue
      }

      filteredRows.push({
        ...row,
        date: row['Date'],
        dateTime: this.dateTime.fromFormat(row['Date'], 'yyyy-MM-dd'),
        positiveRate: parseFloat(row['Test Pos Rate 7d Avg']),
        adminTests: row["Tests Admin 7d Avg"],
        positiveTests: row['Pos Tests 7d Avg'],
        wastewater: row['Wastewater 7d (kv / L)'],
        hospitalCases: row['Hospital Avg 7d'],
        deaths: row['New Deaths']
      })

      if ( filteredRows.length >= maxRows ) {
        break
      }
    }

    return filteredRows
  }

  computeTrends(rows) {
    let updatedRows = []
    let idx = 0
    const pctChange = (oldVal, newVal) => OcTrendsModel.computePctChange(oldVal, newVal)

    for (const row of rows) {
      const prevWeekIdx = idx + 7
      const prevWeekRow = rows[prevWeekIdx]
      const totalDeaths = this.sumDeaths(rows, idx, prevWeekIdx-1)
      idx++

      if ( prevWeekRow === undefined ) {
        updatedRows.push(row)
        continue
      }

      updatedRows.push({
        ...row,
        date: row['Date'],
        positiveRateDelta: pctChange(prevWeekRow.positiveRate, row.positiveRate),
        adminTestsDelta: pctChange(prevWeekRow.adminTests, row.adminTests),
        positiveTestsDelta: pctChange(prevWeekRow.positiveTests, row.positiveTests),
        wastewaterDelta: pctChange(prevWeekRow.wastewater, row.wastewater),
        hospitalCasesDelta: pctChange(prevWeekRow.hospitalCases, row.hospitalCases),
        totalDeaths: totalDeaths
      })
    }

    return updatedRows
  }

  sumDeaths(rows, startIndex, endIndex) {
    let sum = 0
    if (endIndex < 5) { console.log('sumDeaths', rows, startIndex, endIndex) }

    rows.slice(startIndex, endIndex).forEach(row => {
      sum += row.deaths
    })

    if (endIndex < 5) { console.log('sum', sum) }
    return sum
  }
}


/*
 * Main block: these are the things that happen on page load.
**/
$(document).ready(function() {
  const model = new OcTrendsModel(OcTrendsModelConfig)
  model.fetchData()
})
