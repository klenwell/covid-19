import './index.css';
import React from 'react'
import Header from './components/Header'
import SimpleTable from './components/SimpleTable'


const METRICS_URL = 'https://raw.githubusercontent.com/klenwell/covid-19/master/docs/data/json/oc/metrics.json'


function App() {

  const [metricsData, setmetricsData] = React.useState({})
  const [metricsDataFetched, setMetricsDataReady] = React.useState(false)

  React.useEffect(() => {
    fetch(METRICS_URL)
      .then(response => response.json())
      .then(data => {
        console.log(data)
        setmetricsData(data)
        setMetricsDataReady(true)
      })
  }, [])

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
