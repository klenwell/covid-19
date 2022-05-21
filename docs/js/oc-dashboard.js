/*
 * OC Dashboard Javascript
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
 */
const ocDashboard = (function() {
  /*
   * Constants
   */
  const WEEK_TO_WEEK_TABLE_SEL = 'section#week-to-week-trends table'

  /*
   * Public Methods
   */
  const etl = function() {
    extract()
    $(WEEK_TO_WEEK_TABLE_SEL).find('td').html('&middot;')
  }

  /*
   * Private Methods
   */
  const extract = function() {
    console.debug("TODO: extract")
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
  console.log('document ready', $)
  ocDashboard.etl()
})
