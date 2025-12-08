import { useState, useEffect, useMemo } from "react";
import {
  Search,
  Filter,
  Store,
  ExternalLink,
  ArrowDown,
  ArrowUp,
  Loader2,
  Package,
} from "lucide-react";
import { useProducts, useCategories } from "../hooks";
import { useStores } from "../hooks/useStores";
import clsx from "clsx";

const FilterSection = ({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) => (
  <div className="mb-6">
    <h3 className="text-sm font-semibold text-gray-900 mb-3">{title}</h3>
    <div className="space-y-2">{children}</div>
  </div>
);

const Checkbox = ({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: () => void;
}) => (
  <label className="flex items-center gap-2 cursor-pointer group">
    <div
      className={clsx(
        "w-4 h-4 rounded border flex items-center justify-center transition-colors",
        checked
          ? "bg-blue-600 border-blue-600"
          : "border-gray-300 group-hover:border-blue-500"
      )}
    >
      {checked && (
        <svg
          className="w-3 h-3 text-white"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={3}
            d="M5 13l4 4L19 7"
          />
        </svg>
      )}
    </div>
    <span className="text-sm text-gray-600 group-hover:text-gray-900">
      {label}
    </span>
    <input
      type="checkbox"
      className="hidden"
      checked={checked}
      onChange={onChange}
    />
  </label>
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

export const Products = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedStores, setSelectedStores] = useState<string[]>([]);
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 5000]);

  // Check URL params for category filter
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const category = params.get("category");
    if (category) {
      setSelectedCategories([category]);
    }
  }, []);

  // Fetch data from API
  const { products, loading, error } = useProducts({
    search: searchQuery || undefined,
    category:
      selectedCategories.length === 1 ? selectedCategories[0] : undefined,
    store: selectedStores.length === 1 ? selectedStores[0] : undefined,
    minPrice: priceRange[0] > 0 ? priceRange[0] : undefined,
    maxPrice: priceRange[1] < 5000 ? priceRange[1] : undefined,
  });

  const { categories } = useCategories();
  const { stores } = useStores();

  // Get unique store names for filtering
  const storeNames = useMemo(() => stores.map((s) => s.name), [stores]);

  const toggleFilter = (
    list: string[],
    setList: (l: string[]) => void,
    item: string
  ) => {
    if (list.includes(item)) {
      setList(list.filter((i) => i !== item));
    } else {
      setList([...list, item]);
    }
  };

  // Client-side filtering for multiple selections (API only supports single values)
  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      const matchesCategory =
        selectedCategories.length <= 1 ||
        selectedCategories.includes(product.category);
      const matchesStore =
        selectedStores.length <= 1 || selectedStores.includes(product.store);
      return matchesCategory && matchesStore;
    });
  }, [products, selectedCategories, selectedStores]);

  return (
    <div className="max-w-7xl mx-auto px-4 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">All Products</h1>
        <p className="text-gray-500">
          Browse and compare prices across all tracked PC components
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Filters Sidebar */}
        <div className="w-full lg:w-64 shrink-0">
          <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm lg:sticky lg:top-24">
            <div className="flex items-center gap-2 mb-6 text-gray-900">
              <Filter size={20} />
              <h2 className="font-bold">Filters</h2>
            </div>

            <FilterSection title="Categories">
              {categories.length === 0 ? (
                <p className="text-sm text-gray-400">No categories available</p>
              ) : (
                categories.map((category) => (
                  <Checkbox
                    key={category}
                    label={category}
                    checked={selectedCategories.includes(category)}
                    onChange={() =>
                      toggleFilter(
                        selectedCategories,
                        setSelectedCategories,
                        category
                      )
                    }
                  />
                ))
              )}
            </FilterSection>

            <FilterSection title="Stores">
              {storeNames.length === 0 ? (
                <p className="text-sm text-gray-400">No stores available</p>
              ) : (
                storeNames.map((store) => (
                  <Checkbox
                    key={store}
                    label={store}
                    checked={selectedStores.includes(store)}
                    onChange={() =>
                      toggleFilter(selectedStores, setSelectedStores, store)
                    }
                  />
                ))
              )}
            </FilterSection>

            <FilterSection title="Price Range">
              <div className="px-2">
                <input
                  type="range"
                  min="0"
                  max="5000"
                  step="50"
                  value={priceRange[1]}
                  onChange={(e) =>
                    setPriceRange([priceRange[0], parseInt(e.target.value)])
                  }
                  className="w-full accent-blue-600"
                />
                <div className="flex justify-between text-sm text-gray-500 mt-2">
                  <span>${priceRange[0]}</span>
                  <span>${priceRange[1]}</span>
                </div>
              </div>
            </FilterSection>
          </div>
        </div>

        {/* Product Grid */}
        <div className="flex-1">
          <div className="mb-6 flex items-center justify-between">
            <div className="relative flex-1 max-w-md">
              <Search
                className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                size={20}
              />
              <input
                type="text"
                placeholder="Search today's products..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none shadow-sm"
              />
            </div>
            <div className="flex items-center gap-2 text-gray-500 text-sm">
              <span className="font-medium text-gray-900">
                {filteredProducts.length}
              </span>{" "}
              results found
            </div>
          </div>

          {loading ? (
            <LoadingSpinner />
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-500">Failed to load products</p>
              <p className="text-gray-500 text-sm mt-2">{error}</p>
            </div>
          ) : filteredProducts.length === 0 ? (
            <EmptyState message="No products found. Try adjusting your filters or check back after the daily scrape." />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {filteredProducts.map((product) => (
                <div
                  key={product.id}
                  className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow group"
                >
                  <div className="relative aspect-[4/3] bg-gray-100 overflow-hidden">
                    <img
                      src={product.image || "/placeholder.svg"}
                      alt={product.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = "/placeholder.svg";
                      }}
                    />
                    <div className="absolute top-3 right-3">
                      {product.priceChange !== 0 && (
                        <span
                          className={clsx(
                            "px-2 py-1 rounded-lg text-xs font-medium flex items-center gap-1",
                            product.priceChange < 0
                              ? "bg-green-100 text-green-700"
                              : "bg-red-100 text-red-700"
                          )}
                        >
                          {product.priceChange < 0 ? (
                            <ArrowDown size={12} />
                          ) : (
                            <ArrowUp size={12} />
                          )}
                          {Math.abs(product.priceChange)}%
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="p-5">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded-md">
                        {product.category}
                      </span>
                      <span className="text-xs text-gray-500 flex items-center gap-1">
                        <Store size={12} />
                        {product.store}
                      </span>
                    </div>
                    <h3
                      className="font-bold text-gray-900 mb-2 line-clamp-2 h-12"
                      title={product.name}
                    >
                      {product.name}
                    </h3>
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex flex-col">
                        <span className="text-xs text-gray-400">
                          Updated{" "}
                          {new Date(product.lastUpdated).toLocaleDateString()}
                        </span>
                        <span className="text-xl font-bold text-gray-900">
                          ${product.price.toFixed(2)}
                        </span>
                      </div>
                      <a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2"
                      >
                        View Deal
                        <ExternalLink size={14} />
                      </a>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
