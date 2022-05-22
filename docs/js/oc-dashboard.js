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

    console.log(`Fetrching data from ${csvUrl}`)
    Papa.parse(csvUrl, papaConfig)
  }

  const onFetchComplete = function(results) {
    console.log('onFetchComplete', results)
    const jsonData = transformCsvResults(results.data)
    reloadDashboard(jsonData)
  }

  const transformCsvResults = function(csvRows) {
    $(TRENDS_TABLE_SEL).find('caption').text(`Data extracted.`)
    console.debug("transformCsvResults:", csvRows)
    OcTrendsModel.loadCsvResults(csvRows)
    return OcTrendsModel.toJson()
  }

  const reloadDashboard = function(jsonData) {
    console.debug("loadResults:", jsonData)
    $(TRENDS_TABLE_SEL).find('caption').text(`Data transformed.`)
    '12345'.split('').forEach(num => reloadRow(num, jsonData))
    $(TRENDS_TABLE_SEL).find('caption').text(`Dashboard reloaded.`)
  }

  const reloadRow = function(week, jsonData) {
    const rowSel = `${TRENDS_TABLE_SEL} tr.week-${week}`
    const valSel = 'span.value'
    const delSel = 'span.delta'

    const idx = parseInt(week) - 1
    const rowData = jsonData.week[idx]

    const nullOrValue = function(value) {
      return value !== null ? value : 'n/a'
    }

    const asNum = (value) => !!value ? value.toFixed(1) : 'n/a'
    const asPct = (value) => !!value ? `${value.toFixed(1)}%` : 'n/a'

    $(`${rowSel} td.test-positive-rate ${valSel}`).text(asPct(rowData.positiveRate))
    $(`${rowSel} td.test-positive-rate ${delSel}`).text(asPct(rowData.positiveRateDelta))
    $(`${rowSel} td.admin-tests ${valSel}`).text(asNum(rowData.adminTests))
    $(`${rowSel} td.admin-tests ${delSel}`).text(asPct(rowData.adminTestsDelta))
    $(`${rowSel} td.positive-tests ${valSel}`).text(asNum(rowData.positiveTests))
    $(`${rowSel} td.positive-tests ${delSel}`).text(asPct(rowData.positiveTestsDelta))
    $(`${rowSel} td.wastewater ${valSel}`).text(asNum(rowData.wastewater))
    $(`${rowSel} td.wastewater ${delSel}`).text(asPct(rowData.wastewaterDelta))
    $(`${rowSel} td.end-date`).text(jsonData.week[idx].date)
  }

  const resetDashboard = function() {
    $(TRENDS_TABLE_SEL).find('caption').text(`Loading data from ${CSV_URL}`)
  }

  const onFetchError = function(err, file) {
    console.error("ERROR:", err, file)
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
