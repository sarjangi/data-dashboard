import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from 'recharts';
import type { ValueType } from 'recharts/types/component/DefaultTooltipContent';
import type { DateRangeFilter, CategoryStats } from '@/types';
import { analyticsApi } from '@/lib/api';
import { getErrorMessage } from '@/lib/errors';
import { logger } from '@/lib/logger';

interface CategoryChartProps {
  filters?: DateRangeFilter;
}

// Transformed data with numbers for chart display
interface CategoryChartData {
  category: string;
  revenue: number;
  order_count: number;
  product_count: number;
  avg_order_value: number;
  percentage_of_total: number;
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function formatCurrencyValue(value: ValueType | undefined): string {
  const numericValue = Array.isArray(value) ? Number(value[0] ?? 0) : Number(value ?? 0);
  return `$${numericValue.toLocaleString()}`;
}

export function CategoryChart({ filters }: CategoryChartProps) {
  const [data, setData] = useState<CategoryChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [filters]);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);
      const result = await analyticsApi.getSalesByCategory(filters);
      // Convert string values to numbers for Recharts
      const transformedData = result.data.map((item: CategoryStats) => ({
        ...item,
        revenue: Number(item.revenue),
        avg_order_value: Number(item.avg_order_value),
        percentage_of_total: item.percentage_of_total ? Number(item.percentage_of_total) : 0,
      }));
      setData(transformedData);
    } catch (err) {
      const message = getErrorMessage(err, 'Failed to load category data');
      logger.error('Category chart load failed', err);
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  if (loading && data.length === 0) {
    return (
      <div className="card">
        <p className="text-gray-600">Loading category data...</p>
      </div>
    );
  }

  if (error && data.length === 0) {
    return (
      <div className="card">
        <p className="text-sm text-red-700">{error}</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Sales by Category</h2>

      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="category" stroke="#6b7280" fontSize={12} />
          <YAxis
            stroke="#6b7280"
            fontSize={12}
            tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
            formatter={(value) => [formatCurrencyValue(value), 'Revenue']}
          />
          <Legend />
          <Bar dataKey="revenue" name="Revenue" radius={[8, 8, 0, 0]}>
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Category Details */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        {data.slice(0, 4).map((category, index) => (
          <div key={category.category} className="flex items-center gap-2">
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: COLORS[index % COLORS.length] }}
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{category.category}</p>
              <p className="text-xs text-gray-600">
                {category.percentage_of_total.toFixed(1)}% of total
              </p>
            </div>
            <p className="text-sm font-semibold text-gray-900">
              ${category.revenue.toLocaleString(undefined, {
                maximumFractionDigits: 0,
              })}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
