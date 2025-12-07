import { TrendingUp, Package, ShoppingCart, ArrowDown } from 'lucide-react';
import { products } from '../data/products';

const StatCard = ({ title, value, subValue, icon: Icon, color, trend }: any) => (
  <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
    <div className="flex items-start justify-between mb-4">
      <div className={`p-3 rounded-xl ${color}`}>
        <Icon size={24} className="text-white" />
      </div>
      {trend !== undefined && (
        <span className={`text-xs font-medium px-2 py-1 rounded-full ${trend > 0 ? 'text-green-500 bg-green-50' : 'text-red-500 bg-red-50'}`}>
          {trend > 0 ? '+' : ''}{trend}%
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

export const Dashboard = () => {
  const totalProducts = products.length;
  const uniqueStores = new Set(products.map(p => p.store)).size;
  const priceDrops = products.filter(p => p.priceChange < 0).length;
  const biggestDrop = Math.min(...products.map(p => p.priceChange));

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard Overview</h1>
          <p className="text-gray-500 mt-1">Daily price tracking updates.</p>
        </div>
        <div className="text-sm text-gray-500">
          Last Scrape: {new Date().toLocaleDateString()}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Products Tracked"
          value={totalProducts}
          subValue="Active Items"
          icon={Package}
          color="bg-blue-500"
          trend={2.5}
        />
        <StatCard
          title="Stores Monitored"
          value={uniqueStores}
          subValue="Sources"
          icon={ShoppingCart}
          color="bg-purple-500"
        />
        <StatCard
          title="Price Drops"
          value={priceDrops}
          subValue="Last 24h"
          icon={TrendingUp}
          color="bg-orange-500"
          trend={12}
        />
        <StatCard
          title="Biggest Drop"
          value={`${Math.abs(biggestDrop)}%`}
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
            <button className="text-blue-600 text-sm font-medium hover:underline">View All</button>
          </div>
          <div className="space-y-4">
            {products
              .filter(p => p.priceChange < 0)
              .sort((a, b) => a.priceChange - b.priceChange)
              .slice(0, 5)
              .map((product) => (
              <div key={product.id} className="flex items-center gap-4 p-4 hover:bg-gray-50 rounded-xl transition-colors cursor-pointer">
                <img
                  src={product.image}
                  alt={product.name}
                  className="w-16 h-16 rounded-lg object-cover bg-gray-100"
                />
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{product.name}</h3>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <span>{product.store}</span>
                    <span>•</span>
                    <span>Updated {new Date(product.lastUpdated).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-gray-900">${product.price}</div>
                  <div className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full inline-block mt-1">
                    {product.priceChange}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Category Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
          <h2 className="text-lg font-bold text-gray-900 mb-6">Categories</h2>
          <div className="space-y-4">
            {['GPU', 'CPU', 'RAM', 'Storage', 'Motherboard'].map((cat, i) => (
              <div key={cat} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 rounded-full ${['bg-blue-500', 'bg-purple-500', 'bg-orange-500', 'bg-green-500', 'bg-red-500'][i]}`}></div>
                  <span className="text-sm font-medium text-gray-700">{cat}</span>
                </div>
                <span className="text-sm text-gray-500">{products.filter(p => p.category === cat).length}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
