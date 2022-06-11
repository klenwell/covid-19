/*
 * OC Dashboard Javascript
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
 */
const OcDashboard = (function() {
  /*
   * Constants
   */
  const TRENDS_TABLE_SEL = 'section#week-to-week-trends table'

  /*
   * Public Methods
  **/
  const render = function(model) {
     reloadDashboard(model)
   }

   const resetDashboard = function() {
     const csvUrl = OcTrendsModelConfig.csvUrl
     $(TRENDS_TABLE_SEL).find('caption').text(`Loading data from ${csvUrl}`)
   }

  /*
   * Private Methods
  **/
  const reloadDashboard = function(model) {
    '1234'.split('').forEach(weekNum => reloadRow(weekNum, model))
    $(TRENDS_TABLE_SEL).find('caption').text('')
  }

  const reloadRow = function(weekNum, model) {
    const rowSel = `${TRENDS_TABLE_SEL} tr.week-${weekNum}`
    const valSel = 'span.value'
    const delSel = 'span.delta'

    const idx = parseInt(weekNum) - 1
    const rowData = model.weeks[idx]
    const startDate = rowData.dateTime.minus({days: 6}).toFormat('yyyy-MM-dd')

    // Helper functions
    const asNum = (value, fixed) => !!value ? value.toFixed(fixed !== undefined ? fixed : 1) : 'n/a'
    const asPct = (value) => !!value ? `${value.toFixed(1)}%` : 'n/a'
    const asSignedPct = (value) => {
      if ( !value ) {
        return 'n/a'
      }
      const sign = value > 0 ? '+' : '';
      return `${sign}${value.toFixed(1)}%`
    }
    const pctWrap = (value) => `(${asSignedPct(value)})`

    // Compute death delta
    let prevWeekDeaths = model.weeks[idx + 1].totalDeaths
    rowData.deathsDelta = OcTrendsModel.computePctChange(prevWeekDeaths, rowData.totalDeaths)

    // Update cells
    $(`${rowSel} td.test-positive-rate ${valSel}`).text(asPct(rowData.positiveRate))
    $(`${rowSel} td.test-positive-rate ${delSel}`).text(pctWrap(rowData.positiveRateDelta))
    $(`${rowSel} td.admin-tests ${valSel}`).text(asNum(rowData.adminTests))
    $(`${rowSel} td.admin-tests ${delSel}`).text(pctWrap(rowData.adminTestsDelta))
    $(`${rowSel} td.positive-tests ${valSel}`).text(asNum(rowData.positiveTests, 1))
    $(`${rowSel} td.positive-tests ${delSel}`).text(pctWrap(rowData.positiveTestsDelta))
    $(`${rowSel} td.wastewater ${valSel}`).text(asNum(rowData.wastewater, 1))
    $(`${rowSel} td.wastewater ${delSel}`).text(pctWrap(rowData.wastewaterDelta))
    $(`${rowSel} td.hospital-cases ${valSel}`).text(asNum(rowData.hospitalCases, 1))
    $(`${rowSel} td.hospital-cases ${delSel}`).text(pctWrap(rowData.hospitalCasesDelta))
    $(`${rowSel} td.deaths ${valSel}`).text(asNum(rowData.totalDeaths, 0))
    $(`${rowSel} td.deaths ${delSel}`).text(pctWrap(rowData.deathsDelta))
    $(`${rowSel} td.start-date`).text(startDate)
    $(`${rowSel} td.end-date`).text(rowData.date)

    // Set cell styles
    updateRowStyling(rowSel, rowData)
  }

  const updateRowStyling = function(rowSel, rowData) {
    const setClass = (delta, tdSel) => {
      let className = ''
      if (delta > 0) {
        className = 'rising'
      }
      else if (delta < 0) {
        className = 'falling'
      }

      $(`${rowSel} ${tdSel}`).addClass(className)
    }

    setClass(rowData.positiveRateDelta, 'td.test-positive-rate')
    setClass(rowData.adminTestsDelta, 'td.admin-tests')
    setClass(rowData.positiveTestsDelta, 'td.positive-tests')
    setClass(rowData.wastewaterDelta, 'td.wastewater')
    setClass(rowData.hospitalCasesDelta, 'td.hospital-cases')
    setClass(rowData.deathsDelta, 'td.deaths')
  }

  /*
   * Public API
   */
  return {
    render: render,
    resetDashboard: resetDashboard
  }
})()


/*
 * Main block: these are the things that happen on designated event.
**/
$(document).on(OcTrendsModel.dataReady, (event, model) => {
  OcDashboard.render(model)
})

$(document).ready(function() {
  OcDashboard.resetDashboard()
})
