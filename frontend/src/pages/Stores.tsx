import { ExternalLink, ShoppingBag, Loader2, Package } from "lucide-react";
import { useStores } from "../hooks/useStores";

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

export const Stores = () => {
  const { stores, loading, error } = useStores();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">Failed to load stores</p>
        <p className="text-gray-500 text-sm mt-2">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Supported Stores</h1>
        <p className="text-gray-500 mt-1">
          We currently track prices from these major retailers.
        </p>
      </div>

      {stores.length === 0 ? (
        <EmptyState message="No stores configured yet. Add stores via the API to start tracking prices." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {stores.map((store) => (
            <div
              key={store.id}
              className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="h-16 flex items-center mb-6">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-50 rounded-xl text-blue-600">
                    <ShoppingBag size={24} />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900">
                    {store.name}
                  </h3>
                </div>
              </div>

              <p className="text-gray-500 mb-6 h-12 line-clamp-2">
                {store.description || "No description available"}
              </p>

              <div className="flex items-center justify-between pt-4 border-t border-gray-50">
                <span
                  className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    store.status === "active"
                      ? "bg-green-100 text-green-800"
                      : store.status === "error"
                      ? "bg-red-100 text-red-800"
                      : "bg-gray-100 text-gray-800"
                  }`}
                >
                  {store.status.charAt(0).toUpperCase() + store.status.slice(1)}
                </span>
                <a
                  href={store.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline"
                >
                  Visit Website
                  <ExternalLink size={14} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
