# Data Analytics Dashboard - Frontend

React frontend for the Data Analytics Dashboard with interactive charts and data visualization.

## Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite 7.3** - Build tool
- **Tailwind CSS 4** - Styling
- **Recharts 3.8** - Data visualization
- **Axios** - HTTP client

## Features

- ✅ Interactive line charts (revenue trends)
- ✅ Bar charts (category sales)
- ✅ Data tables (top products)
- ✅ Date range filtering
- ✅ CSV export functionality
- ✅ Responsive design
- ✅ Type-safe API client
- ✅ Lazy-loaded dashboard sections and vendor chunk splitting

## Quick Start

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

Frontend runs on: http://localhost:5173

## Environment Variables

```env
VITE_API_URL=http://localhost:8000
```

If the backend is running on a different local port, set `VITE_API_URL` to match it before starting Vite.

## Build for Production

```bash
# Build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── charts/           # Lazy-loaded chart components (Recharts)
│   │   ├── RevenueTrendChart.tsx
│   │   └── CategoryChart.tsx
│   └── ui/               # UI components
│       ├── StatCard.tsx
│       ├── TopProductsTable.tsx
│       └── DateRangePicker.tsx
├── lib/
│   ├── api.ts            # API client
│   ├── errors.ts         # Error normalization helpers
│   └── logger.ts         # Dev-only logger
├── types/
│   └── index.ts          # TypeScript types
├── App.tsx               # Main application
├── main.tsx              # Entry point
└── index.css             # Global styles
```

## Performance Notes

- `DateRangePicker`, `RevenueTrendChart`, `CategoryChart`, and `TopProductsTable` are lazy-loaded with `Suspense` fallbacks.
- Vite manual chunking separates React, charting, and icon vendors to keep the initial app payload smaller.
- The app prefetches dashboard chunks during browser idle time after the summary data is loaded.

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Lint code

## License

MIT License
