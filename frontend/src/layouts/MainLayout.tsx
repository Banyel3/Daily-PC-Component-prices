import { Outlet, NavLink, Link } from "react-router-dom";
import { Search, TrendingDown, Menu, X, Cpu } from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

const NavItem = ({
  to,
  children,
}: {
  to: string;
  children: React.ReactNode;
}) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      clsx(
        "px-4 py-2 rounded-lg font-medium transition-colors",
        isActive
          ? "text-blue-600 bg-blue-50"
          : "text-gray-600 hover:text-blue-600 hover:bg-gray-50"
      )
    }
  >
    {children}
  </NavLink>
);

const MobileNavItem = ({
  to,
  children,
  onClick,
}: {
  to: string;
  children: React.ReactNode;
  onClick: () => void;
}) => (
  <NavLink
    to={to}
    onClick={onClick}
    className={({ isActive }) =>
      clsx(
        "block px-4 py-3 rounded-lg font-medium transition-colors",
        isActive
          ? "text-blue-600 bg-blue-50"
          : "text-gray-600 hover:text-blue-600 hover:bg-gray-50"
      )
    }
  >
    {children}
  </NavLink>
);

export const MainLayout = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Top Banner */}
      <div className="bg-blue-600 text-white text-center py-2 text-sm">
        <span className="flex items-center justify-center gap-2">
          <TrendingDown size={16} />
          Track daily PC component prices across major retailers
        </span>
      </div>

      {/* Main Navigation */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl flex items-center justify-center shadow-lg shadow-blue-600/20">
                <Cpu className="text-white" size={22} />
              </div>
              <div className="hidden sm:block">
                <span className="text-xl font-bold text-gray-900">
                  PriceTracker
                </span>
                <span className="text-xs text-gray-500 block -mt-1">
                  PC Components
                </span>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              <NavItem to="/">Home</NavItem>
              <NavItem to="/products">Products</NavItem>
              <NavItem to="/deals">Deals</NavItem>
              <NavItem to="/stores">Stores</NavItem>
            </nav>

            {/* Right Side Actions */}
            <div className="flex items-center gap-4">
              {/* Search (Desktop) */}
              <div className="hidden lg:flex items-center">
                <div className="relative">
                  <Search
                    className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                    size={18}
                  />
                  <input
                    type="text"
                    placeholder="Search products..."
                    className="pl-10 pr-4 py-2 w-64 bg-gray-100 border-0 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
                  />
                </div>
              </div>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-gray-100 py-4 px-4">
            {/* Mobile Search */}
            <div className="relative mb-4">
              <Search
                className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                size={18}
              />
              <input
                type="text"
                placeholder="Search products..."
                className="w-full pl-10 pr-4 py-3 bg-gray-100 border-0 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <nav className="space-y-1">
              <MobileNavItem to="/" onClick={() => setMobileMenuOpen(false)}>
                Home
              </MobileNavItem>
              <MobileNavItem
                to="/products"
                onClick={() => setMobileMenuOpen(false)}
              >
                Products
              </MobileNavItem>
              <MobileNavItem
                to="/deals"
                onClick={() => setMobileMenuOpen(false)}
              >
                Deals
              </MobileNavItem>
              <MobileNavItem
                to="/stores"
                onClick={() => setMobileMenuOpen(false)}
              >
                Stores
              </MobileNavItem>
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Brand */}
            <div className="md:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                  <Cpu className="text-white" size={22} />
                </div>
                <span className="text-xl font-bold text-white">
                  PriceTracker
                </span>
              </div>
              <p className="text-sm leading-relaxed">
                Track PC component prices across major retailers. Get notified
                when prices drop and never miss a deal on GPUs, CPUs, RAM, and
                more.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-white font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-sm">
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
                    Retailers
                  </Link>
                </li>
              </ul>
            </div>

            {/* Categories */}
            <div>
              <h3 className="text-white font-semibold mb-4">Categories</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link
                    to="/products?category=GPU"
                    className="hover:text-white transition-colors"
                  >
                    Graphics Cards
                  </Link>
                </li>
                <li>
                  <Link
                    to="/products?category=CPU"
                    className="hover:text-white transition-colors"
                  >
                    Processors
                  </Link>
                </li>
                <li>
                  <Link
                    to="/products?category=RAM"
                    className="hover:text-white transition-colors"
                  >
                    Memory
                  </Link>
                </li>
                <li>
                  <Link
                    to="/products?category=Storage"
                    className="hover:text-white transition-colors"
                  >
                    Storage
                  </Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 text-sm text-center">
            <p>
              © {new Date().getFullYear()} PriceTracker. Prices updated daily at
              11:59 PM UTC.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};
