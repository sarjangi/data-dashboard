import { lazy, Suspense, useEffect, useState } from 'react';
import { BarChart3, TrendingUp, Package, Globe, Download } from 'lucide-react';
import { analyticsApi, exportApi } from './lib/api';
import { getErrorMessage } from './lib/errors';
import { logger } from './lib/logger';
import type { SummaryStats, DateRangeFilter } from './types';
import { StatCard } from './components/ui/StatCard';
import type { DateRangePickerProps } from './components/ui/DateRangePicker';

type IdleWindow = Window & {
  requestIdleCallback?: (callback: () => void) => number;
  cancelIdleCallback?: (handle: number) => void;
};

const DateRangePicker = lazy(async () => {
  const module = await import('./components/ui/DateRangePicker');
  return { default: module.DateRangePicker };
});

const RevenueTrendChart = lazy(async () => {
  const module = await import('./components/charts/RevenueTrendChart');
  return { default: module.RevenueTrendChart };
});

const CategoryChart = lazy(async () => {
  const module = await import('./components/charts/CategoryChart');
  return { default: module.CategoryChart };
});

const TopProductsTable = lazy(async () => {
  const module = await import('./components/ui/TopProductsTable');
  return { default: module.TopProductsTable };
});

function prefetchDashboardChunks(): Promise<unknown[]> {
  return Promise.all([
    import('./components/charts/RevenueTrendChart'),
    import('./components/charts/CategoryChart'),
    import('./components/ui/TopProductsTable'),
    import('./components/ui/DateRangePicker'),
  ]);
}

function SectionFallback({ message, className = 'card' }: { message: string; className?: string }) {
  return (
    <div className={className}>
      <p className="text-gray-600">{message}</p>
    </div>
  );
}

function App() {
  const [summary, setSummary] = useState<SummaryStats | null>(null);
  const [filters, setFilters] = useState<DateRangeFilter>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, [filters]);

  useEffect(() => {
    if (!summary) {
      return undefined;
    }

    const currentWindow = window as IdleWindow;
    const runPrefetch = () => {
      void prefetchDashboardChunks();
    };

    if (currentWindow.requestIdleCallback) {
      const handle = currentWindow.requestIdleCallback(runPrefetch);
      return () => {
        currentWindow.cancelIdleCallback?.(handle);
      };
    }

    const timeoutId = window.setTimeout(runPrefetch, 0);
    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [summary]);

  async function loadDashboardData() {
    try {
      setLoading(true);
      setError(null);
      const data = await analyticsApi.getSummary(filters);
      setSummary(data);
    } catch (err) {
      const message = getErrorMessage(err, 'Failed to load dashboard data');
      setError(message);
      logger.error('Dashboard summary load failed', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleExportCSV() {
    try {
      setExportError(null);
      const blob = await exportApi.exportCSV(filters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sales-export-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      const message = getErrorMessage(err, 'Failed to export data');
      logger.error('CSV export failed', err);
      setExportError(message);
    }
  }

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error && !summary) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={loadDashboardData} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                <BarChart3 className="h-8 w-8 text-blue-600" />
                Data Analytics Dashboard
              </h1>
              <p className="text-gray-600 mt-1">Business Intelligence & Insights</p>
            </div>
            <button onClick={handleExportCSV} className="btn-primary flex items-center gap-2">
              <Download className="h-4 w-4" />
              Export CSV
            </button>
          </div>

          {/* Date Range Filter */}
          <div className="mt-4">
            <Suspense fallback={<SectionFallback className="min-h-11" message="Loading filters..." />}>
              <DateRangePicker
                filters={filters}
                setFilters={setFilters as DateRangePickerProps['setFilters']}
              />
            </Suspense>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {exportError ? (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {exportError}
          </div>
        ) : null}

        {summary && (
          <>
            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                title="Total Revenue"
                value={`$${Number(summary.total_revenue).toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}`}
                icon={<TrendingUp className="h-6 w-6 text-green-600" />}
                trend="+12.5%"
              />
              <StatCard
                title="Total Orders"
                value={summary.total_orders.toLocaleString()}
                icon={<Package className="h-6 w-6 text-blue-600" />}
              />
              <StatCard
                title="Products Sold"
                value={summary.total_products_sold.toLocaleString()}
                icon={<Package className="h-6 w-6 text-purple-600" />}
              />
              <StatCard
                title="Avg Order Value"
                value={`$${Number(summary.average_order_value).toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}`}
                icon={<Globe className="h-6 w-6 text-orange-600" />}
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <Suspense fallback={<SectionFallback message="Loading revenue trend..." />}>
                <RevenueTrendChart filters={filters} />
              </Suspense>
              <Suspense fallback={<SectionFallback message="Loading category data..." />}>
                <CategoryChart filters={filters} />
              </Suspense>
            </div>

            {/* Top Products */}
            <Suspense fallback={<SectionFallback message="Loading top products..." />}>
              <TopProductsTable filters={filters} />
            </Suspense>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
