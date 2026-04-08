import { useState, useEffect } from 'react';
import type { DateRangeFilter, ProductStats } from '@/types';
import { analyticsApi } from '@/lib/api';
import { getErrorMessage } from '@/lib/errors';
import { logger } from '@/lib/logger';

interface TopProductsTableProps {
  filters?: DateRangeFilter;
}

export function TopProductsTable({ filters }: TopProductsTableProps) {
  const [products, setProducts] = useState<ProductStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProducts();
  }, [filters]);

  async function loadProducts() {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsApi.getTopProducts(10, filters);
      setProducts(data.data);
    } catch (err) {
      const message = getErrorMessage(err, 'Failed to load top products');
      logger.error('Top products load failed', err);
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  if (loading && products.length === 0) {
    return (
      <div className="card">
        <p className="text-gray-600">Loading top products...</p>
      </div>
    );
  }

  if (error && products.length === 0) {
    return (
      <div className="card">
        <p className="text-sm text-red-700">{error}</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Top Products</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Product
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Revenue
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Quantity
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Orders
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Avg Price
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {products.map((product) => (
              <tr key={product.product_id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-sm font-medium text-gray-900">
                  {product.product_name}
                </td>
                <td className="px-4 py-3 text-sm text-right text-gray-900">
                  ${Number(product.total_revenue).toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </td>
                <td className="px-4 py-3 text-sm text-right text-gray-700">
                  {product.total_quantity.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-sm text-right text-gray-700">
                  {product.order_count.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-sm text-right text-gray-700">
                  ${Number(product.avg_price).toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
