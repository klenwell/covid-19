/*
 * OC Trends Table Component
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
 */
const OcTrendsTable = (function() {
  /*
   * Constants
   */
  const TRENDS_TABLE_SEL = 'section#week-to-week-trends table'

  /*
   * Public Methods
  **/
  const render = function(model) {
     reloadTable(model)
   }

   const resetTable = function() {
     const extractUrl = OcTrendsModelConfig.extractUrl
     $(TRENDS_TABLE_SEL).find('caption').text(`Loading data from ${extractUrl}`)
   }

  /*
   * Private Methods
  **/
  const reloadTable = function(model) {
    '1234'.split('').forEach(weekNum => reloadRow(weekNum, model))
    $(TRENDS_TABLE_SEL).find('caption').text('')
  }

  const reloadRow = function(weekNum, model) {
    const rowSel = `${TRENDS_TABLE_SEL} tr.week-${weekNum}`
    const valSel = 'span.value'
    const delSel = 'span.delta'

    const idx = parseInt(weekNum) - 1
    const week = model.weeks[idx]

    // Helper functions
    const asNum = (value, fixed) => !isNaN(value) ? value.toFixed(fixed !== undefined ? fixed : 1) : 'n/a'
    const asPct = (value) => !isNaN(value) ? `${value.toFixed(1)}%` : 'n/a'
    const asSignedPct = (value) => {
      if ( isNaN(value) ) {
        return 'n/a'
      }
      const sign = value > 0 ? '+' : '';
      return `${sign}${value.toFixed(1)}%`
    }
    const pctWrap = (value) => `(${asSignedPct(value)})`

    // Update cells
    $(`${rowSel} td.test-positive-rate ${valSel}`).text(asPct(week.testPositiveRate.value))
    $(`${rowSel} td.test-positive-rate ${delSel}`).text(pctWrap(week.testPositiveRate.delta))
    $(`${rowSel} td.admin-tests ${valSel}`).text(asNum(week.adminTests.average7d))
    $(`${rowSel} td.admin-tests ${delSel}`).text(pctWrap(week.adminTests.delta))
    $(`${rowSel} td.positive-tests ${valSel}`).text(asNum(week.positiveTests.average7d, 1))
    $(`${rowSel} td.positive-tests ${delSel}`).text(pctWrap(week.positiveTests.delta))
    $(`${rowSel} td.wastewater ${valSel}`).text(asNum(week.wastewater.average7d, 0))
    $(`${rowSel} td.wastewater ${delSel}`).text(pctWrap(week.wastewater.delta))
    $(`${rowSel} td.hospital-cases ${valSel}`).text(asNum(week.hospitalCases.average7d, 1))
    $(`${rowSel} td.hospital-cases ${delSel}`).text(pctWrap(week.hospitalCases.delta))
    $(`${rowSel} td.deaths ${valSel}`).text(asNum(week.deaths.total, 0))
    $(`${rowSel} td.deaths ${delSel}`).text(pctWrap(week.deaths.delta))
    $(`${rowSel} td.start-date`).text(week.startDate)
    $(`${rowSel} td.end-date`).text(week.endDate)

    // Set cell styles
    updateRowStyling(rowSel, week)
  }

  const updateRowStyling = function(rowSel, week) {
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

    setClass(week.testPositiveRate.value, 'td.test-positive-rate')
    setClass(week.adminTests.delta, 'td.admin-tests')
    setClass(week.positiveTests.delta, 'td.positive-tests')
    setClass(week.wastewater.delta, 'td.wastewater')
    setClass(week.hospitalCases.delta, 'td.hospital-cases')
    setClass(week.deaths.delta, 'td.deaths')
  }

  /*
   * Public API
   */
  return {
    render: render,
    resetTable: resetTable
  }
})()


/*
 * Main block: these are the things that happen on designated event.
**/
$(document).on(OcTrendsModel.dataReady, (event, model) => {
  OcTrendsTable.render(model)
})

$(document).ready(function() {
  OcTrendsTable.resetTable()
})
