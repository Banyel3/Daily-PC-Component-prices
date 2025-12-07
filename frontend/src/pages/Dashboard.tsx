import {
  TrendingUp,
  Package,
  ShoppingCart,
  ArrowDown,
  Loader2,
} from "lucide-react";
import { useStats, useTopDeals } from "../hooks";
import { Link } from "react-router-dom";

const StatCard = ({
  title,
  value,
  subValue,
  icon: Icon,
  color,
  trend,
}: {
  title: string;
  value: string | number;
  subValue: string;
  icon: React.ElementType;
  color: string;
  trend?: number;
}) => (
  <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
    <div className="flex items-start justify-between mb-4">
      <div className={`p-3 rounded-xl ${color}`}>
        <Icon size={24} className="text-white" />
      </div>
      {trend !== undefined && (
        <span
          className={`text-xs font-medium px-2 py-1 rounded-full ${
            trend > 0 ? "text-green-500 bg-green-50" : "text-red-500 bg-red-50"
          }`}
        >
          {trend > 0 ? "+" : ""}
          {trend}%
        </span>
      )}
    </div>
    <h3 className="text-gray-500 text-sm font-medium mb-1">{title}</h3>
    <div className="flex items-baseline gap-2">
      <span className="text-2xl font-bold text-gray-900">{value}</span>
      <span className="text-sm text-gray-400">{subValue}</span>
    </div>
  </div>
);

const LoadingSpinner = () => (
  <div className="flex items-center justify-center py-12">
    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
  </div>
);

const EmptyState = ({ message }: { message: string }) => (
  <div className="flex flex-col items-center justify-center py-12 text-gray-500">
    <Package size={48} className="mb-4 opacity-50" />
    <p>{message}</p>
  </div>
);

export const Dashboard = () => {
  const { stats, loading: statsLoading, error: statsError } = useStats();
  const { deals, loading: dealsLoading } = useTopDeals(5);

  if (statsLoading) {
    return <LoadingSpinner />;
  }

  if (statsError) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">Failed to load dashboard data</p>
        <p className="text-gray-500 text-sm mt-2">{statsError}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Dashboard Overview
          </h1>
          <p className="text-gray-500 mt-1">Daily price tracking updates.</p>
        </div>
        <div className="text-sm text-gray-500">
          Last Updated:{" "}
          {stats?.date
            ? new Date(stats.date).toLocaleDateString()
            : new Date().toLocaleDateString()}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Products Tracked"
          value={stats?.total_products || 0}
          subValue="Active Items"
          icon={Package}
          color="bg-blue-500"
        />
        <StatCard
          title="Stores Monitored"
          value={stats?.unique_stores || 0}
          subValue="Sources"
          icon={ShoppingCart}
          color="bg-purple-500"
        />
        <StatCard
          title="Price Drops"
          value={stats?.price_drops || 0}
          subValue="Today"
          icon={TrendingUp}
          color="bg-orange-500"
        />
        <StatCard
          title="Biggest Drop"
          value={`${stats?.biggest_drop || 0}%`}
          subValue="Discount"
          icon={ArrowDown}
          color="bg-green-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Price Drops */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-gray-900">Top Deals Today</h2>
            <Link
              to="/products"
              className="text-blue-600 text-sm font-medium hover:underline"
            >
              View All
            </Link>
          </div>

          {dealsLoading ? (
            <LoadingSpinner />
          ) : deals.length === 0 ? (
            <EmptyState message="No price drops today. Check back after the daily scrape!" />
          ) : (
            <div className="space-y-4">
              {deals.map((product) => (
                <div
                  key={product.id}
                  className="flex items-center gap-4 p-4 hover:bg-gray-50 rounded-xl transition-colors cursor-pointer"
                >
                  <img
                    src={product.image || "/placeholder.svg"}
                    alt={product.name}
                    className="w-16 h-16 rounded-lg object-cover bg-gray-100"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = "/placeholder.svg";
                    }}
                  />
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 line-clamp-1">
                      {product.name}
                    </h3>
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <span>{product.store}</span>
                      <span>•</span>
                      <span>{product.category}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-gray-900">
                      ${product.price.toFixed(2)}
                    </div>
                    <div className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full inline-block mt-1">
                      {product.priceChange}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Category Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-6">Categories</h2>
          {stats?.categories_count === 0 ? (
            <EmptyState message="No categories yet" />
          ) : (
            <div className="space-y-4">
              <div className="text-center py-8">
                <p className="text-3xl font-bold text-gray-900">
                  {stats?.categories_count || 0}
                </p>
                <p className="text-gray-500 text-sm">Product Categories</p>
              </div>
              <div className="pt-4 border-t border-gray-100">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">Avg. Price Drop</span>
                  <span className="font-medium text-green-600">
                    {stats?.avg_price_drop || 0}%
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
