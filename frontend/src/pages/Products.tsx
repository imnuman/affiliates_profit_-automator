import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../services/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { Search } from 'lucide-react'
import type { Product } from '../services/types'
import { formatCurrency, formatNumber } from '../lib/utils'

export default function Products() {
  const [searchQuery, setSearchQuery] = useState('')

  const { data: products, isLoading } = useQuery({
    queryKey: ['products', searchQuery],
    queryFn: async () => {
      const response = await api.get<Product[]>('/products/search', {
        params: { query: searchQuery, limit: 20 },
      })
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Products</h1>
        <p className="text-muted-foreground">Find profitable ClickBank products to promote</p>
      </div>

      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search products..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Button>Search</Button>
      </div>

      {isLoading ? (
        <div className="flex h-96 items-center justify-center">
          <div className="text-muted-foreground">Loading products...</div>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {products?.map(product => (
            <Card key={product.id}>
              <CardHeader>
                <CardTitle className="line-clamp-2">{product.title}</CardTitle>
                <CardDescription>{product.vendor}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Gravity:</span>
                  <span className="font-medium">{formatNumber(Number(product.gravity || 0))}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Commission:</span>
                  <span className="font-medium">
                    {formatCurrency(Number(product.commission_amount || 0))}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Category:</span>
                  <span className="font-medium">{product.category || 'N/A'}</span>
                </div>
                <Button className="mt-4 w-full" size="sm">
                  Create Campaign
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!isLoading && products?.length === 0 && (
        <div className="flex h-96 items-center justify-center">
          <div className="text-center">
            <p className="text-muted-foreground">No products found</p>
            <p className="text-sm text-muted-foreground">Try adjusting your search criteria</p>
          </div>
        </div>
      )}
    </div>
  )
}
