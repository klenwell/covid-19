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
    console.debug('loadCsvResults', csvRows)
    allRows = csvRows
    trendRows = filterTrendRows(csvRows)
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
     console.debug(rows)

     for (const row of rows) {
       let isValid = !!row['Date'] && !!row['Test Pos Rate 7d Avg']

       if ( !isValid ) {
         continue
       }

       filteredRows.push({
         ...row,
         date: row['Date'],
         dateTime: DateTime.fromFormat(row['Date'], 'yyyy-MM-dd'),
         positiveRate: row['Test Pos Rate 7d Avg'],
         adminTests: row["Tests Admin'd"],
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

   const mapRowsToDates = function(rows) {
     mappedRows = {}

     for (const row of rows) {
       mappedRows[row.date] = row
     }

     return mappedRows
   }

  /*
   * Public API
   */
  return {
    loadCsvResults: loadCsvResults,
    toJson: toJson
  }
})()
