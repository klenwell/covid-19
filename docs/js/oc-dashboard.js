/*
 * OC Dashboard Javascript
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
 */
const ocDashboard = (function() {
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
    const jsonData = transformCsvResults(results)
    reloadDashboard(jsonData)
  }

  const transformCsvResults = function(results) {
    $(TRENDS_TABLE_SEL).find('caption').text(`Data extracted.`)
    console.debug("transformCsvResults:", results)
    // OcTrendsModel.loadCsvResults(results)
    // return OcTrendsModel.toJson()
    return {}
  }

  const reloadDashboard = function(jsonData) {
    $(TRENDS_TABLE_SEL).find('caption').text(`Data transformed.`)
    console.debug("reloadDashboard:", jsonData)
    $(TRENDS_TABLE_SEL).find('td').text('TBA')
    $(TRENDS_TABLE_SEL).find('caption').text(`Dashboard reloaded.`)
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
  console.log('document ready')
  ocDashboard.etl()
})
