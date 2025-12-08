import { Link } from "react-router-dom";
import {
  TrendingDown,
  ExternalLink,
  Loader2,
  Package,
  ArrowDown,
} from "lucide-react";
import { useTopDeals } from "../hooks";

export const Deals = () => {
  const { deals, loading, error } = useTopDeals(20);

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-red-100 rounded-lg">
            <TrendingDown className="text-red-600" size={24} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Today's Deals</h1>
        </div>
        <p className="text-gray-500">
          Products with the biggest price drops today. Prices are updated daily
          at 11:59 PM.
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="animate-spin text-blue-600 mb-4" size={40} />
          <p className="text-gray-500">Loading today's deals...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && deals.length === 0 && (
        <div className="text-center py-20">
          <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Package className="text-gray-400" size={40} />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No Deals Found
          </h3>
          <p className="text-gray-500 mb-6">
            There are no price drops to show today. Check back tomorrow!
          </p>
          <Link
            to="/products"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors"
          >
            Browse All Products
          </Link>
        </div>
      )}

      {/* Deals Grid */}
      {!loading && !error && deals.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {deals.map((deal) => (
            <div
              key={deal.id}
              className="bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-lg hover:border-gray-200 transition-all group"
            >
              {/* Deal Badge */}
              <div className="relative">
                <div className="absolute top-3 left-3 z-10">
                  <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-500 text-white text-sm font-semibold rounded-full">
                    <ArrowDown size={14} />
                    {Math.abs(deal.priceChange).toFixed(1)}% OFF
                  </span>
                </div>

                {/* Image */}
                <div className="aspect-square bg-gray-100 flex items-center justify-center p-4">
                  {deal.image ? (
                    <img
                      src={deal.image}
                      alt={deal.name}
                      className="max-h-full max-w-full object-contain group-hover:scale-105 transition-transform"
                    />
                  ) : (
                    <Package className="text-gray-300" size={64} />
                  )}
                </div>
              </div>

              {/* Content */}
              <div className="p-4">
                {/* Store & Category */}
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded">
                    {deal.store}
                  </span>
                  <span className="text-xs text-gray-400">{deal.category}</span>
                </div>

                {/* Name */}
                <h3 className="font-medium text-gray-900 line-clamp-2 mb-3 min-h-[48px]">
                  {deal.name}
                </h3>

                {/* Price */}
                <div className="flex items-baseline gap-2 mb-4">
                  <span className="text-2xl font-bold text-gray-900">
                    ${deal.price.toFixed(2)}
                  </span>
                  <span className="text-sm text-gray-400 line-through">
                    ${(deal.price / (1 + deal.priceChange / 100)).toFixed(2)}
                  </span>
                </div>

                {/* Action */}
                <a
                  href={deal.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors"
                >
                  View Deal
                  <ExternalLink size={16} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
