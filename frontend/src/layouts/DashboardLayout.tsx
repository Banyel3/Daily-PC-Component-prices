import { Outlet, NavLink } from "react-router-dom";
import { LayoutDashboard, Store, Package } from "lucide-react";
import clsx from "clsx";

const SidebarItem = ({
  to,
  icon: Icon,
  label,
}: {
  to: string;
  icon: any;
  label: string;
}) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      clsx(
        "flex items-center gap-3 px-4 py-3 rounded-xl transition-colors",
        isActive
          ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
          : "text-gray-500 hover:bg-gray-100 hover:text-gray-900"
      )
    }
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </NavLink>
);

export const DashboardLayout = () => {
  return (
    <div className="flex h-screen bg-gray-50 font-sans">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-100 flex flex-col p-6">
        <div className="flex items-center gap-3 px-2 mb-10">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Store className="text-white" size={20} />
          </div>
          <span className="text-xl font-bold text-gray-900">
            PC Component Prices
          </span>
        </div>

        <div className="space-y-2 flex-1">
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 px-4">
            Menu
          </div>
          <SidebarItem to="/" icon={LayoutDashboard} label="Dashboard" />
          <SidebarItem to="/products" icon={Package} label="Products" />
          <SidebarItem to="/stores" icon={Store} label="Stores" />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-20 bg-white border-b border-gray-100 flex items-center justify-end px-8">
          <div className="flex items-center gap-6">
            {/* Search removed as requested */}
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};
