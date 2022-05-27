import React from 'react'


export default function SimpleTable(props) {
  const metricsData = props.metricsData

  function headRow(headers) {
    console.log(headers)
    const headCells = headers.map((header, i) => {
      let cellKey = `head-${i}`
      return (
        <th className={header} key={cellKey}>{header}</th>
      )
    })

    return (
      <tr>
        {headCells}
      </tr>
    )
  }

  function bodyRow(metricKey, metric) {
    console.log('bodyRow', metric)
    const cells = Object.entries(metric).map(([key, value], i) => {
      let cellKey = `${metricKey}-${i}`
      return (
        <td className={key} key={cellKey}>{value}</td>
      )
    })

    return (
      <tr key={metricKey}>
        {cells}
      </tr>
    )
  }

  return (
    <table className="table">
      <thead>
        {headRow(Object.keys(metricsData.testPositiveRate))}
      </thead>
      <tbody>
        {bodyRow('testPositiveRate', metricsData.testPositiveRate)}
        {bodyRow('dailyNewCases', metricsData.dailyNewCases)}
      </tbody>
    </table>
  );
}
