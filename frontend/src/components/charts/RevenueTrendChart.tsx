import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import type { ValueType } from 'recharts/types/component/DefaultTooltipContent';
import type { DateRangeFilter, RevenueTrendItem } from '@/types';
import { analyticsApi } from '@/lib/api';
import { getErrorMessage } from '@/lib/errors';
import { logger } from '@/lib/logger';

interface RevenueTrendChartProps {
  filters?: DateRangeFilter;
}

// Transformed data with numbers for chart display
interface RevenueTrendChartData {
  period: string;
  revenue: number;
  order_count: number;
  avg_order_value: number;
}

function formatCurrencyValue(value: ValueType | undefined): string {
  const numericValue = Array.isArray(value) ? Number(value[0] ?? 0) : Number(value ?? 0);
  return `$${numericValue.toLocaleString()}`;
}

export function RevenueTrendChart({ filters }: RevenueTrendChartProps) {
  const [data, setData] = useState<RevenueTrendChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [periodType, setPeriodType] = useState<'daily' | 'weekly' | 'monthly' | 'yearly'>('monthly');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [filters, periodType]);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);
      const result = await analyticsApi.getRevenueTrend({ ...filters, period_type: periodType });
      // Convert string values to numbers for Recharts
      const transformedData = result.data.map((item: RevenueTrendItem) => ({
        ...item,
        revenue: Number(item.revenue),
        avg_order_value: Number(item.avg_order_value),
      }));
      setData(transformedData);
    } catch (err) {
      const message = getErrorMessage(err, 'Failed to load revenue trend');
      logger.error('Revenue trend load failed', err);
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  if (loading && data.length === 0) {
    return (
      <div className="card">
        <p className="text-gray-600">Loading revenue trend...</p>
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
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900">Revenue Trend</h2>
        <select
          value={periodType}
          onChange={(e) => setPeriodType(e.target.value as 'daily' | 'weekly' | 'monthly' | 'yearly')}
          className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
        </select>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="period"
            stroke="#6b7280"
            fontSize={12}
            tickFormatter={(value) => {
              const date = new Date(value);
              return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }}
          />
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
          <Line
            type="monotone"
            dataKey="revenue"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 6 }}
            name="Revenue"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
