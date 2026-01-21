/**
 * ChartDisplay Component
 *
 * Renders data visualizations using Recharts.
 * Supports bar, line, pie, and scatter charts.
 */
import { useMemo } from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts'
import type { ChartData } from '../types'
import './ChartDisplay.css'

interface ChartDisplayProps {
  data: ChartData
  type: string
}

// Color palette for charts
const COLORS = [
  '#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316',
  '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6'
]

export default function ChartDisplay({ data, type }: ChartDisplayProps) {
  // Transform data for Recharts format
  const chartData = useMemo(() => {
    if (!data?.labels || !data?.values) return []

    return data.labels.map((label, index) => ({
      name: label,
      value: data.values[index],
      index
    }))
  }, [data])

  // Transform data for multiple series (line/bar charts)
  const multiSeriesData = useMemo(() => {
    if (!data?.additional_series) return null

    return data.labels.map((label, index) => {
      const item: any = { name: label }
      data.additional_series?.forEach(series => {
        item[series.name] = series.data[index]
      })
      return item
    })
  }, [data])

  if (!chartData.length) {
    return (
      <div className="chart-display empty">
        <p>No chart data available</p>
      </div>
    )
  }

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return multiSeriesData ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={multiSeriesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              {data.additional_series?.map((series, index) => (
                <Bar
                  key={series.name}
                  dataKey={series.name}
                  fill={COLORS[index % COLORS.length]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }}
              />
              <Bar
                dataKey="value"
                fill={COLORS[0]}
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )

      case 'line':
        return multiSeriesData ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={multiSeriesData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              {data.additional_series?.map((series, index) => (
                <Line
                  key={series.name}
                  type="monotone"
                  dataKey={series.name}
                  stroke={COLORS[index % COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke={COLORS[0]}
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={120}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        )

      case 'scatter':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px'
                }}
              />
              <Scatter fill={COLORS[0]} />
            </ScatterChart>
          </ResponsiveContainer>
        )

      default:
        return (
          <div className="chart-display empty">
            <p>Unsupported chart type: {type}</p>
          </div>
        )
    }
  }

  return (
    <div className="chart-display">
      <div className="chart-header">
        <h3>Visualization</h3>
        <span className="chart-type-badge">{type}</span>
      </div>
      <div className="chart-content">
        {renderChart()}
      </div>
    </div>
  )
}
