import { Outlet, NavLink, Link } from "react-router-dom";
import { Search, Menu, X, TrendingDown, Cpu, ChevronDown } from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

const categories = [
  "GPU",
  "CPU",
  "RAM",
  "Storage",
  "Motherboard",
  "Case",
  "PSU",
  "Cooling",
];

export const EcommerceLayout = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white py-2 px-4 text-center text-sm">
        <span className="flex items-center justify-center gap-2">
          <TrendingDown size={16} />
          Track daily PC component prices and never miss a deal!
        </span>
      </div>

      {/* Main Navbar */}
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto">
          {/* Top Nav */}
          <div className="flex items-center justify-between px-4 py-4 lg:px-8">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-600/20">
                <Cpu className="text-white" size={24} />
              </div>
              <div className="hidden sm:block">
                <span className="text-xl font-bold text-gray-900">
                  PriceWatch
                </span>
                <p className="text-xs text-gray-500">PC Component Tracker</p>
              </div>
            </Link>

            {/* Search Bar - Desktop */}
            <div className="hidden md:flex flex-1 max-w-xl mx-8">
              <div className="relative w-full">
                <Search
                  className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
                  size={20}
                />
                <input
                  type="text"
                  placeholder="Search for GPUs, CPUs, RAM, and more..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 bg-gray-100 rounded-xl border-0 focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
              <Link
                to="/deals"
                className="hidden lg:flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors font-medium"
              >
                <TrendingDown size={18} />
                Hot Deals
              </Link>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>

          {/* Category Nav - Desktop */}
          <nav className="hidden lg:flex items-center gap-1 px-8 py-2 border-t border-gray-100">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                clsx(
                  "px-4 py-2 rounded-lg font-medium transition-colors",
                  isActive
                    ? "bg-blue-50 text-blue-600"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )
              }
            >
              Home
            </NavLink>
            <NavLink
              to="/products"
              className={({ isActive }) =>
                clsx(
                  "px-4 py-2 rounded-lg font-medium transition-colors",
                  isActive
                    ? "bg-blue-50 text-blue-600"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )
              }
            >
              All Products
            </NavLink>

            {/* Categories Dropdown */}
            <div className="relative group">
              <button className="flex items-center gap-1 px-4 py-2 rounded-lg font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors">
                Categories
                <ChevronDown size={16} />
              </button>
              <div className="absolute top-full left-0 mt-1 bg-white rounded-xl shadow-xl border border-gray-100 py-2 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                {categories.map((category) => (
                  <Link
                    key={category}
                    to={`/products?category=${category}`}
                    className="block px-4 py-2 text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                  >
                    {category}
                  </Link>
                ))}
              </div>
            </div>

            <NavLink
              to="/deals"
              className={({ isActive }) =>
                clsx(
                  "px-4 py-2 rounded-lg font-medium transition-colors",
                  isActive
                    ? "bg-red-50 text-red-600"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )
              }
            >
              <span className="flex items-center gap-1">
                <TrendingDown size={16} />
                Deals
              </span>
            </NavLink>

            <NavLink
              to="/stores"
              className={({ isActive }) =>
                clsx(
                  "px-4 py-2 rounded-lg font-medium transition-colors",
                  isActive
                    ? "bg-blue-50 text-blue-600"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                )
              }
            >
              Stores
            </NavLink>
          </nav>

          {/* Mobile Search */}
          <div className="lg:hidden px-4 pb-4">
            <div className="relative">
              <Search
                className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
                size={20}
              />
              <input
                type="text"
                placeholder="Search products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 bg-gray-100 rounded-xl border-0 focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
              />
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-white border-t border-gray-100 px-4 py-4">
            <nav className="space-y-2">
              <NavLink
                to="/"
                end
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  clsx(
                    "block px-4 py-3 rounded-lg font-medium",
                    isActive ? "bg-blue-50 text-blue-600" : "text-gray-600"
                  )
                }
              >
                Home
              </NavLink>
              <NavLink
                to="/products"
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  clsx(
                    "block px-4 py-3 rounded-lg font-medium",
                    isActive ? "bg-blue-50 text-blue-600" : "text-gray-600"
                  )
                }
              >
                All Products
              </NavLink>
              <NavLink
                to="/deals"
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  clsx(
                    "block px-4 py-3 rounded-lg font-medium",
                    isActive ? "bg-red-50 text-red-600" : "text-gray-600"
                  )
                }
              >
                🔥 Deals
              </NavLink>
              <NavLink
                to="/stores"
                onClick={() => setMobileMenuOpen(false)}
                className={({ isActive }) =>
                  clsx(
                    "block px-4 py-3 rounded-lg font-medium",
                    isActive ? "bg-blue-50 text-blue-600" : "text-gray-600"
                  )
                }
              >
                Stores
              </NavLink>

              <div className="border-t border-gray-100 pt-4 mt-4">
                <p className="px-4 text-xs font-semibold text-gray-400 uppercase mb-2">
                  Categories
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {categories.map((category) => (
                    <Link
                      key={category}
                      to={`/products?category=${category}`}
                      onClick={() => setMobileMenuOpen(false)}
                      className="px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg text-sm"
                    >
                      {category}
                    </Link>
                  ))}
                </div>
              </div>
            </nav>
          </div>
        )}
      </header>

      {/* Page Content */}
      <main>
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 mt-16">
        <div className="max-w-7xl mx-auto px-4 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Brand */}
            <div className="md:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                  <Cpu className="text-white" size={24} />
                </div>
                <span className="text-xl font-bold text-white">PriceWatch</span>
              </div>
              <p className="text-sm max-w-md">
                Track PC component prices across multiple retailers. Get
                notified when prices drop and find the best deals on GPUs, CPUs,
                RAM, and more.
              </p>
            </div>

            {/* Links */}
            <div>
              <h4 className="font-semibold text-white mb-4">Categories</h4>
              <ul className="space-y-2 text-sm">
                {categories.slice(0, 5).map((cat) => (
                  <li key={cat}>
                    <Link
                      to={`/products?category=${cat}`}
                      className="hover:text-white transition-colors"
                    >
                      {cat}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-white mb-4">Quick Links</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link to="/" className="hover:text-white transition-colors">
                    Home
                  </Link>
                </li>
                <li>
                  <Link
                    to="/products"
                    className="hover:text-white transition-colors"
                  >
                    All Products
                  </Link>
                </li>
                <li>
                  <Link
                    to="/deals"
                    className="hover:text-white transition-colors"
                  >
                    Today's Deals
                  </Link>
                </li>
                <li>
                  <Link
                    to="/stores"
                    className="hover:text-white transition-colors"
                  >
                    Stores
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm">
            <p>
              © {new Date().getFullYear()} PriceWatch. Prices are updated daily
              at 11:59 PM.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};
