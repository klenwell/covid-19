/*
 * OcTrendsModel
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
 */
const OcTrendsModel = (function() {
  /*
   * Constants
   */

  /*
   * Class Props
   */
  const DateTime = luxon.DateTime
  let allRows = []
  let trendRows = []
  let weekDates = []
  let datedRecords = {}

  /*
   * Public Methods
   */
  const loadCsvResults = function(csvRows) {
    console.debug('loadCsvResults?', csvRows)
    allRows = csvRows
    trendRows = filterTrendRows(csvRows)
    trendRows = computeTrends(trendRows)
    datedRecords = mapRowsToDates(trendRows)
    weekDates = [
      trendRows[0].date,
      trendRows[7].date,
      trendRows[14].date,
      trendRows[21].date,
      trendRows[28].date,
    ]
  }

  const toJson = function() {
    return {
      week: [
        datedRecords[weekDates[0]],
        datedRecords[weekDates[1]],
        datedRecords[weekDates[2]],
        datedRecords[weekDates[3]],
        datedRecords[weekDates[4]]
      ]
    }
  }

  /*
   * Private Methods
   */
   const filterTrendRows = function(rows) {
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
         dateTime: DateTime.fromFormat(row['Date'], 'yyyy-MM-dd'),
         positiveRate: parseFloat(row['Test Pos Rate 7d Avg']),
         adminTests: row["Tests Admin 7d Avg"],
         positiveTests: row['Pos Tests 7d Avg'],
         wastewater: row['Wastewater 7d (kv / L)'],
         hospitalCases: row['Hospital Cases'],
         deaths: row['New Deaths']
       })

       if ( filteredRows.length >= maxRows ) {
         break
       }
     }

     return filteredRows
   }

   let computeTrends = function(rows) {
     let updatedRows = []
     let idx = 0

     for (const row of rows) {
       const prevWeekIdx = idx + 7
       const prevWeekRow = rows[prevWeekIdx]
       idx++

       if ( prevWeekRow === undefined ) {
         updatedRows.push(row)
         continue
       }

       updatedRows.push({
         ...row,
         date: row['Date'],
         positiveRateDelta: computePctChange(prevWeekRow.positiveRate, row.positiveRate),
         adminTestsDelta: computePctChange(prevWeekRow.adminTests, row.adminTests),
         positiveTestsDelta: computePctChange(prevWeekRow.positiveTests, row.positiveTests),
         wastewaterDelta: computePctChange(prevWeekRow.wastewater, row.wastewater),
         hospitalCasesDelta: computePctChange(prevWeekRow.hospitalCases, row.hospitalCases),
         deathsDelta: computePctChange(prevWeekRow.deaths, row.deaths)
       })
     }

     return updatedRows
   }

   const mapRowsToDates = function(rows) {
     mappedRows = {}

     for (const row of rows) {
       mappedRows[row.date] = row
     }

     return mappedRows
   }

   let computePctChange = function(oldValue, newValue) {
     if ( !oldValue || !newValue ) {
       return undefined
     }
     return ((newValue - oldValue) / oldValue) * 100
   }

  /*
   * Public API
   */
  return {
    loadCsvResults: loadCsvResults,
    toJson: toJson
  }
})()
