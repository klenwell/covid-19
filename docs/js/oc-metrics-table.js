/*
 * OC Metrics Table View Model
 *
 * Uses jQuery module pattern: https://wiki.klenwell.com/view/JQuery
 */
const OcMetricTable = (function() {
  /*
   * Constants
   */
  const SELECTOR = 'section#oc-covid-metrics table'

  /*
   * Public Methods
   */
  const render = function(model) {
    populate(model)
  }

  // Based on https://stackoverflow.com/a/12138756/1093087
  const syncUrlToTab = function() {
    const homeHash = '#metrics'
    const hash = window.location.hash;
    const hashSel = `ul.nav-pills button[data-bs-target="${hash}"]`

    // https://stackoverflow.com/a/5298684/1093087
    const removeHash = () => {
      const loc = window.location
      history.pushState("", document.title, loc.pathname + loc.search)
      console.log('removeHash', loc.pathname + loc.search)
    }

    // Onload: open tab if hash found
    if (hash) {
      console.log('redirect to tab', hash)
      hash && $(hashSel).tab('show')
    }

    // On pill click, update URL hash
    $('.nav-pills button').click(function (e) {
      const pillHash = $(this).data('bsTarget')
      $(this).tab('show')

      if ( pillHash == homeHash ) {
        removeHash()
      }
      else {
        window.location.hash = pillHash
      }

      const scrollmem = $('body').scrollTop() || $('html').scrollTop()
      $('html,body').scrollTop(scrollmem)
    })
  }

  /*
   * Private Methods
   */
  const populate = function(model) {
    $(`${SELECTOR} tbody tr`).each((_, el) => {
      const $tr = $(el)
      const rowGetter = $tr.data('metric')
      const metric = model[rowGetter]

      // Update HTML
      $tr.find('td.updated-on span.value').html(metric.html.updatedOn)
      $tr.find('td.latest span.value').html(metric.html.latest)
      $tr.find('td.level span.value').html(metric.html.level)
      $tr.find('td.level span.note').html(metric.html.levelNote)
      $tr.find('td.trend span.value').html(metric.html.trend)
      $tr.find('td.delta-7d span.value').html(metric.html.delta7dValue)
      $tr.find('td.delta-7d span.note').html(metric.html.delta7dNote)
      $tr.find('td.delta-14d span.value').html(metric.html.delta14dValue)
      $tr.find('td.delta-14d span.note').html(metric.html.delta14dNote)

      // Update td classes (styling)
      $tr.find('td.level').addClass(metric.tdClass.level)
      $tr.find('td.trend').addClass(metric.tdClass.trend)
      $tr.find('td.delta-7d').addClass(metric.tdClass.trend)
      $tr.find('td.delta-14d').addClass(metric.tdClass.trend)
    })
  }

  /*
   * Public API
   */
  return {
    render: render,
    syncUrlToTab: syncUrlToTab
  }
})()

/*
 * Main block: these are the things that happen on designatved events.
**/
$(document).ready(() => {
  OcMetricTable.syncUrlToTab()
})

$(document).on(OcMetricsModel.dataReady, (event, model) => {
  OcMetricTable.render(model)
})
