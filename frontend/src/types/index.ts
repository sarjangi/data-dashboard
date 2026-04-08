/**
 * TypeScript types for the Data Analytics Dashboard
 */

export interface SummaryStats {
  total_revenue: string | number;
  total_orders: number;
  total_products_sold: number;
  average_order_value: string | number;
  top_category: string | null;
  top_region: string | null;
}

export interface RevenueTrendItem {
  period: string;
  revenue: string | number;
  order_count: number;
  avg_order_value: string | number;
}

export interface RevenueTrendResponse {
  data: RevenueTrendItem[];
  period_type: string;
}

export interface ProductStats {
  product_id: number;
  product_name: string;
  total_revenue: string | number;
  total_quantity: number;
  order_count: number;
  avg_price: string | number;
}

export interface TopProductsResponse {
  data: ProductStats[];
  limit: number;
}

export interface CategoryStats {
  category: string;
  revenue: string | number;
  order_count: number;
  product_count: number;
  avg_order_value: string | number;
  percentage_of_total?: string | number;
}

export interface SalesByCategoryResponse {
  data: CategoryStats[];
}

export interface RegionalStats {
  region: string;
  revenue: string | number;
  order_count: number;
  avg_order_value: string | number;
  top_product?: string;
  top_category?: string;
}

export interface RegionalPerformanceResponse {
  data: RegionalStats[];
}

export interface DateRangeFilter {
  start_date?: string;
  end_date?: string;
  period_type?: 'daily' | 'weekly' | 'monthly' | 'yearly';
}
