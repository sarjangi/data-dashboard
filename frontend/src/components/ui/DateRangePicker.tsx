import { useState } from 'react';
import type { DateRangeFilter } from '@/types';
import { Calendar } from 'lucide-react';

export interface DateRangePickerProps {
  filters: DateRangeFilter;
  setFilters: (filters: DateRangeFilter) => void;
}

export function DateRangePicker({ filters, setFilters }: DateRangePickerProps) {
  const [startDate, setStartDate] = useState(filters.start_date || '');
  const [endDate, setEndDate] = useState(filters.end_date || '');

  function handleApply() {
    setFilters({
      ...filters,
      start_date: startDate || undefined,
      end_date: endDate || undefined,
    });
  }

  function handleClear() {
    setStartDate('');
    setEndDate('');
    setFilters({});
  }

  return (
    <div className="flex items-center gap-4 flex-wrap">
      <div className="flex items-center gap-2">
        <Calendar className="h-5 w-5 text-gray-500" />
        <label className="text-sm font-medium text-gray-700">From:</label>
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700">To:</label>
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <button onClick={handleApply} className="btn-primary">
        Apply
      </button>

      {(startDate || endDate) && (
        <button onClick={handleClear} className="btn-secondary">
          Clear
        </button>
      )}
    </div>
  );
}
