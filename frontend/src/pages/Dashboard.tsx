import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { DollarSign, MousePointerClick, ShoppingCart, TrendingUp } from 'lucide-react'
import { formatCurrency, formatNumber, formatPercentage } from '../lib/utils'
import type { DashboardMetrics } from '../services/types'

export default function Dashboard() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      const response = await api.get<DashboardMetrics>('/analytics/dashboard')
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-muted-foreground">Loading...</div>
      </div>
    )
  }

  const stats = [
    {
      title: 'Total Revenue',
      value: formatCurrency(Number(metrics?.total_revenue || 0)),
      icon: DollarSign,
      description: 'Total earnings',
    },
    {
      title: 'Conversions',
      value: formatNumber(metrics?.total_conversions || 0),
      icon: ShoppingCart,
      description: 'Total sales',
    },
    {
      title: 'Clicks',
      value: formatNumber(metrics?.total_clicks || 0),
      icon: MousePointerClick,
      description: 'Total clicks',
    },
    {
      title: 'Conversion Rate',
      value: formatPercentage(metrics?.conversion_rate || 0),
      icon: TrendingUp,
      description: 'Click to sale ratio',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here's your overview.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Active Campaigns</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{metrics?.active_campaigns || 0}</div>
            <p className="text-sm text-muted-foreground">Campaigns currently running</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Average Commission</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {formatCurrency(Number(metrics?.average_commission || 0))}
            </div>
            <p className="text-sm text-muted-foreground">Per conversion</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
