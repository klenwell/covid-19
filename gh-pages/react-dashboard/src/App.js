import './index.css';
import React from 'react'
import Header from './components/Header'
import SimpleTable from './components/SimpleTable'


const DEV_METRICS_URL = 'react-dev/data/json/oc/metrics.json'
const METRICS_URL = 'data/json/oc/metrics.json'


function App() {

  const [metricsData, setmetricsData] = React.useState({})
  const [metricsDataFetched, setMetricsDataReady] = React.useState(false)

  React.useEffect(() => {
    fetchMetricsData()
  }, [])

  function fetchMetricsData() {
    const isDev = process.env.NODE_ENV == 'development'
    const metricsUrl = isDev ? DEV_METRICS_URL : METRICS_URL
    console.log(`fetching metrics data from ${metricsUrl}`)

    fetch(metricsUrl)
      .then(response => response.json())
      .then(data => {
        console.log(data)
        setmetricsData(data)
        setMetricsDataReady(true)
      })
  }

  function simpleTable() {
    console.log('simpleTable', metricsDataFetched)
    if ( ! metricsDataFetched ) {
      return '<div>loading...</div>'
    }

    return (
      <SimpleTable
        metricsData={metricsData}
      />
    )
  }

  return (
    <div className="container">
      <Header />
      <main>
        {simpleTable()}
      </main>
    </div>
  )
}

export default App;
