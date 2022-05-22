/*
 * OC Dashboard Javascript
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
 */
const OcDashboard = (function() {
  /*
   * Constants
   */
  const SHEET_ID = '1M7BfyPuwHQiavFtH59sgI9lJ7HjBpjXdBB-5BWv15K4'
  const CSV_URL = `https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Data`
  const TRENDS_TABLE_SEL = 'section#week-to-week-trends table'

  /*
   * Public Methods
   */
  const etl = function() {
    resetDashboard()
    extractCsvData(CSV_URL)
  }

  /*
   * Private Methods
   */
  const extractCsvData = function(csvUrl) {
    const papaConfig = {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      download: true,
      complete: onFetchComplete,
      error: onFetchError
    }

    console.log(`Fetching data from ${csvUrl}`)
    Papa.parse(csvUrl, papaConfig)
  }

  const onFetchComplete = function(results) {
    console.log('onFetchComplete', results)
    const jsonData = transformCsvResults(results.data)
    reloadDashboard(jsonData)
  }

  const transformCsvResults = function(csvRows) {
    console.log("transformCsvResults:", csvRows)
    $(TRENDS_TABLE_SEL).find('caption').text(`Data extracted.`)
    OcTrendsModel.loadCsvResults(csvRows)
    return OcTrendsModel.toJson()
  }

  const reloadDashboard = function(jsonData) {
    console.log("loadResults:", jsonData)
    $(TRENDS_TABLE_SEL).find('caption').text(`Data transformed.`)
    '12345'.split('').forEach(weekNum => reloadRow(weekNum, jsonData))
    $(TRENDS_TABLE_SEL).find('caption').text(`Dashboard reloaded.`)
  }

  const reloadRow = function(weekNum, jsonData) {
    const rowSel = `${TRENDS_TABLE_SEL} tr.week-${weekNum}`
    const valSel = 'span.value'
    const delSel = 'span.delta'

    const idx = parseInt(weekNum) - 1
    const rowData = jsonData.week[idx]
    const startDate = rowData.dateTime.minus({days: 6}).toFormat('yyyy-MM-dd')

    // Helper functions
    const asNum = (value) => !!value ? value.toFixed(1) : 'n/a'
    const asPct = (value) => {
      if ( !value ) {
        return 'n/a'
      }
      const sign = value > 0 ? '+' : '';
      return `${sign}${value.toFixed(1)}%`
    }
    const pctWrap = (value) => `(${asPct(value)})`

    // Update cells
    $(`${rowSel} td.test-positive-rate ${valSel}`).text(asPct(rowData.positiveRate))
    $(`${rowSel} td.test-positive-rate ${delSel}`).text(pctWrap(rowData.positiveRateDelta))
    $(`${rowSel} td.admin-tests ${valSel}`).text(asNum(rowData.adminTests))
    $(`${rowSel} td.admin-tests ${delSel}`).text(pctWrap(rowData.adminTestsDelta))
    $(`${rowSel} td.positive-tests ${valSel}`).text(asNum(rowData.positiveTests))
    $(`${rowSel} td.positive-tests ${delSel}`).text(pctWrap(rowData.positiveTestsDelta))
    $(`${rowSel} td.wastewater ${valSel}`).text(asNum(rowData.wastewater))
    $(`${rowSel} td.wastewater ${delSel}`).text(pctWrap(rowData.wastewaterDelta))
    $(`${rowSel} td.start-date`).text(startDate)
    $(`${rowSel} td.end-date`).text(rowData.date)
  }

  const resetDashboard = function() {
    $(TRENDS_TABLE_SEL).find('caption').text(`Loading data from ${CSV_URL}`)
  }

  const onFetchError = function(err, file) {
    console.error("ERROR:", err, file)
    $(TRENDS_TABLE_SEL).find('caption').text('Sorry. There was an error fetching the data.')
  }

  /*
   * Public API
   */
  return {
    etl: etl
  }
})()

/*
 * Main block: these are the things that happen on every page load.
 */
$(document).ready(function() {
  OcDashboard.etl()
})
