import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card } from '@/components/ui/card'

interface AnalyticsStats {
  totalClicks: number
  totalConversions: number
  totalRevenue: number
  conversionRate: number
  clickTrend: Array<{ date: string; clicks: number }>
  revenueTrend: Array<{ date: string; revenue: number }>
  topCampaigns: Array<{
    id: string
    name: string
    clicks: number
    conversions: number
    revenue: number
  }>
}

export default function Analytics() {
  const [timeRange, setTimeRange] = useState('30d')

  const { data: stats, isLoading } = useQuery<AnalyticsStats>({
    queryKey: ['analytics', timeRange],
    queryFn: async () => {
      const response = await api.get(`/analytics/stats?range=${timeRange}`)
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent"></div>
          <p className="mt-4 text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Analytics</h1>
          <p className="text-muted-foreground">
            Track your performance and insights
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setTimeRange('7d')}
            className={`rounded-md px-3 py-2 text-sm ${
              timeRange === '7d'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground'
            }`}
          >
            7 Days
          </button>
          <button
            onClick={() => setTimeRange('30d')}
            className={`rounded-md px-3 py-2 text-sm ${
              timeRange === '30d'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground'
            }`}
          >
            30 Days
          </button>
          <button
            onClick={() => setTimeRange('90d')}
            className={`rounded-md px-3 py-2 text-sm ${
              timeRange === '90d'
                ? 'bg-primary text-primary-foreground'
                : 'bg-secondary text-secondary-foreground'
            }`}
          >
            90 Days
          </button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">
              Total Clicks
            </p>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold">
                {stats?.totalClicks.toLocaleString() || 0}
              </p>
              <span className="text-sm text-green-600">+12%</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">
              Conversions
            </p>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold">
                {stats?.totalConversions.toLocaleString() || 0}
              </p>
              <span className="text-sm text-green-600">+8%</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">
              Total Revenue
            </p>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold">
                ${stats?.totalRevenue.toLocaleString() || 0}
              </p>
              <span className="text-sm text-green-600">+15%</span>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">
              Conversion Rate
            </p>
            <div className="flex items-baseline gap-2">
              <p className="text-3xl font-bold">
                {stats?.conversionRate.toFixed(1) || 0}%
              </p>
              <span className="text-sm text-green-600">+2.1%</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="p-6">
          <h3 className="mb-4 font-semibold">Click Trend</h3>
          <div className="h-64">
            <SimpleLineChart
              data={stats?.clickTrend || []}
              dataKey="clicks"
              color="#3b82f6"
            />
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="mb-4 font-semibold">Revenue Trend</h3>
          <div className="h-64">
            <SimpleLineChart
              data={stats?.revenueTrend || []}
              dataKey="revenue"
              color="#10b981"
            />
          </div>
        </Card>
      </div>

      {/* Top Campaigns */}
      <Card className="p-6">
        <h3 className="mb-4 font-semibold">Top Performing Campaigns</h3>
        <div className="space-y-4">
          {stats?.topCampaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="flex items-center justify-between border-b pb-3 last:border-b-0"
            >
              <div className="space-y-1">
                <p className="font-medium">{campaign.name}</p>
                <p className="text-sm text-muted-foreground">
                  {campaign.clicks} clicks • {campaign.conversions} conversions
                </p>
              </div>
              <div className="text-right">
                <p className="font-semibold text-green-600">
                  ${campaign.revenue.toLocaleString()}
                </p>
                <p className="text-sm text-muted-foreground">
                  {((campaign.conversions / campaign.clicks) * 100).toFixed(1)}%
                  CR
                </p>
              </div>
            </div>
          ))}
          {(!stats?.topCampaigns || stats.topCampaigns.length === 0) && (
            <p className="text-center text-muted-foreground">
              No campaigns data available
            </p>
          )}
        </div>
      </Card>
    </div>
  )
}

// Simple line chart component (basic implementation)
function SimpleLineChart({ data, dataKey, color }: {
  data: Array<{ date: string; [key: string]: any }>
  dataKey: string
  color: string
}) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">
        No data available
      </div>
    )
  }

  const maxValue = Math.max(...data.map((d) => d[dataKey]))
  const height = 256 // 64px * 4 = h-64

  return (
    <div className="relative h-full w-full">
      <svg width="100%" height="100%" className="overflow-visible">
        {/* Y-axis labels */}
        <text x="0" y="20" className="text-xs fill-muted-foreground">
          {maxValue}
        </text>
        <text x="0" y={height / 2} className="text-xs fill-muted-foreground">
          {Math.round(maxValue / 2)}
        </text>
        <text x="0" y={height - 10} className="text-xs fill-muted-foreground">
          0
        </text>

        {/* Line path */}
        <polyline
          fill="none"
          stroke={color}
          strokeWidth="2"
          points={data
            .map((point, index) => {
              const x = 50 + (index / (data.length - 1)) * (100 - 50) + '%'
              const y = height - (point[dataKey] / maxValue) * (height - 20)
              return `${x},${y}`
            })
            .join(' ')}
        />

        {/* Data points */}
        {data.map((point, index) => {
          const x =
            50 +
            (index / (data.length - 1)) * (window.innerWidth * 0.45 - 50)
          const y = height - (point[dataKey] / maxValue) * (height - 20)
          return (
            <circle
              key={index}
              cx={x}
              cy={y}
              r="4"
              fill={color}
              className="opacity-80"
            />
          )
        })}
      </svg>

      {/* X-axis labels */}
      <div className="mt-2 flex justify-between text-xs text-muted-foreground">
        <span>{data[0]?.date}</span>
        <span>{data[Math.floor(data.length / 2)]?.date}</span>
        <span>{data[data.length - 1]?.date}</span>
      </div>
    </div>
  )
}
