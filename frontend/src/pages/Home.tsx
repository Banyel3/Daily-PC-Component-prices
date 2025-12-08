import { Link } from "react-router-dom";
import {
  TrendingDown,
  Package,
  ArrowRight,
  Zap,
  Shield,
  Clock,
  Loader2,
} from "lucide-react";
import { useStats, useTopDeals } from "../hooks";

const HeroSection = () => (
  <section className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28">
      <div className="max-w-3xl">
        <h1 className="text-4xl lg:text-6xl font-bold leading-tight mb-6">
          Find the Best Prices on
          <span className="text-blue-200"> PC Components</span>
        </h1>
        <p className="text-xl text-blue-100 mb-8 leading-relaxed">
          We track prices across major retailers daily, so you never miss a deal
          on GPUs, CPUs, RAM, storage, and more.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <Link
            to="/products"
            className="inline-flex items-center justify-center gap-2 bg-white text-blue-700 px-8 py-4 rounded-xl font-semibold hover:bg-blue-50 transition-colors shadow-lg"
          >
            Browse Products
            <ArrowRight size={20} />
          </Link>
          <Link
            to="/deals"
            className="inline-flex items-center justify-center gap-2 bg-blue-500/30 text-white px-8 py-4 rounded-xl font-semibold hover:bg-blue-500/40 transition-colors border border-blue-400/30"
          >
            <TrendingDown size={20} />
            Today's Deals
          </Link>
        </div>
      </div>
    </div>
  </section>
);

const FeatureCard = ({
  icon: Icon,
  title,
  description,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
}) => (
  <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
    <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
      <Icon className="text-blue-600" size={24} />
    </div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-gray-600 text-sm leading-relaxed">{description}</p>
  </div>
);

const StatBadge = ({
  value,
  label,
}: {
  value: string | number;
  label: string;
}) => (
  <div className="text-center">
    <div className="text-3xl lg:text-4xl font-bold text-gray-900">{value}</div>
    <div className="text-sm text-gray-500 mt-1">{label}</div>
  </div>
);

const ProductCard = ({
  product,
}: {
  product: {
    id: string;
    name: string;
    price: number;
    currency: string;
    image: string | null;
    category: string;
    store: string;
    priceChange: number;
    url: string;
  };
}) => (
  <Link
    to={`/products`}
    className="group bg-white rounded-2xl border border-gray-100 overflow-hidden hover:shadow-lg transition-all hover:-translate-y-1"
  >
    <div className="aspect-[4/3] bg-gray-100 relative overflow-hidden">
      {product.image ? (
        <img
          src={product.image}
          alt={product.name}
          className="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform"
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center">
          <Package className="w-16 h-16 text-gray-300" />
        </div>
      )}
      {product.priceChange < 0 && (
        <div className="absolute top-3 left-3 bg-green-500 text-white text-xs font-bold px-2 py-1 rounded-full">
          {product.priceChange.toFixed(1)}%
        </div>
      )}
    </div>
    <div className="p-4">
      <div className="text-xs text-gray-500 mb-1">
        {product.category} • {product.store}
      </div>
      <h3 className="font-medium text-gray-900 line-clamp-2 mb-2 group-hover:text-blue-600 transition-colors">
        {product.name}
      </h3>
      <div className="flex items-baseline gap-2">
        <span className="text-xl font-bold text-gray-900">
          ${product.price.toLocaleString()}
        </span>
        <span className="text-xs text-gray-400">{product.currency}</span>
      </div>
    </div>
  </Link>
);

export const Home = () => {
  const { stats, loading: statsLoading } = useStats();
  const { deals, loading: dealsLoading } = useTopDeals(4);

  return (
    <div>
      <HeroSection />

      {/* Stats Section */}
      <section className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <StatBadge
              value={statsLoading ? "—" : stats?.total_products || 0}
              label="Products Tracked"
            />
            <StatBadge
              value={statsLoading ? "—" : stats?.unique_stores || 0}
              label="Retailers"
            />
            <StatBadge
              value={statsLoading ? "—" : stats?.price_drops || 0}
              label="Price Drops Today"
            />
            <StatBadge
              value={statsLoading ? "—" : `${stats?.biggest_drop || 0}%`}
              label="Biggest Discount"
            />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Use PriceTracker?
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              We make it easy to find the best deals on PC components across all
              major retailers.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <FeatureCard
              icon={Clock}
              title="Daily Price Updates"
              description="Prices are automatically scraped every day at 11:59 PM UTC to ensure you have the latest information."
            />
            <FeatureCard
              icon={Zap}
              title="Instant Price Drops"
              description="See which products have dropped in price today and by how much, so you can act fast on deals."
            />
            <FeatureCard
              icon={Shield}
              title="Multiple Retailers"
              description="Compare prices across Newegg, Best Buy, Micro Center, Amazon, and more in one place."
            />
          </div>
        </div>
      </section>

      {/* Top Deals Section */}
      <section className="bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Today's Top Deals
              </h2>
              <p className="text-gray-500 mt-1">
                Products with the biggest price drops today
              </p>
            </div>
            <Link
              to="/deals"
              className="hidden sm:inline-flex items-center gap-2 text-blue-600 font-medium hover:underline"
            >
              View all deals
              <ArrowRight size={16} />
            </Link>
          </div>

          {dealsLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            </div>
          ) : deals.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-2xl">
              <TrendingDown className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">
                No price drops today. Check back after the daily update!
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {deals.map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          )}

          <div className="sm:hidden mt-6 text-center">
            <Link
              to="/deals"
              className="inline-flex items-center gap-2 text-blue-600 font-medium"
            >
              View all deals
              <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-600 to-indigo-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Start Tracking Prices Today
          </h2>
          <p className="text-blue-100 mb-8 max-w-2xl mx-auto">
            Browse our catalog of PC components and find the best prices across
            major retailers.
          </p>
          <Link
            to="/products"
            className="inline-flex items-center gap-2 bg-white text-blue-700 px-8 py-4 rounded-xl font-semibold hover:bg-blue-50 transition-colors shadow-lg"
          >
            Browse All Products
            <ArrowRight size={20} />
          </Link>
        </div>
      </section>
    </div>
  );
};
