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
    window.OcTrendsModel = OcTrendsModel
    return OcTrendsModel.toJson()
  }

  const reloadDashboard = function(jsonData) {
    $(TRENDS_TABLE_SEL).find('caption').text(`Data transformed.`)
    '12345'.split('').forEach(num => reloadRow(num, jsonData))
    $(TRENDS_TABLE_SEL).find('caption').text(`Dashboard reloaded.`)
  }

  const reloadRow = function(week, jsonData) {
    const idx = parseInt(week) - 1
    const rowSel = `${TRENDS_TABLE_SEL} tr.week-${week}`
    const wasteWater = jsonData.week[idx].wastewater

    const nullOrValue = function(value) {
      return value !== null ? value : 'n/a'
    }

    $(`${rowSel} td.test-positive-rate`).text(jsonData.week[idx].positiveRate)
    $(`${rowSel} td.wastewater`).text(nullOrValue(wasteWater))
    $(`${rowSel} td.end-date`).text(jsonData.week[idx].date)
  }

  const resetDashboard = function() {
    $(TRENDS_TABLE_SEL).find('td').html('&middot;')
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
