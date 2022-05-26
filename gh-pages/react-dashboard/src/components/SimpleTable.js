import React from 'react'


export default function SimpleTable(props) {
  const metricsData = props.metricsData

  function headRow(headers) {
    console.log(headers)
    const headCells = headers.map(header => {
      return (
        <th className="{header}">{header}</th>
      )
    })

    return (
      <tr>
        {headCells}
      </tr>
    )
  }

  function bodyRow(metric) {
    console.log('bodyRow', metric)
    const cells = Object.entries(metric).map(([key, value]) => {
      console.log(key, value)
      return (
        <td className="{key}">{value}</td>
      )
    })

    return (
      <tr>
        {cells}
      </tr>
    )
  }

  return (
    <table>
      <thead>
        {headRow(Object.keys(metricsData.testPositiveRate))}
      </thead>
      <tbody>
        {bodyRow(metricsData.testPositiveRate)}
        {bodyRow(metricsData.dailyNewCases)}
      </tbody>
    </table>
  );
}
