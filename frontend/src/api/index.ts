// API configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || "/api";

// Product interface matching the API response
export interface Product {
  id: string;
  name: string;
  price: number;
  currency: string;
  image: string | null;
  category: string;
  store: string;
  brand: string | null;
  url: string;
  lastUpdated: string;
  priceChange: number;
}

export interface Store {
  id: string;
  name: string;
  url: string;
  logo: string | null;
  description: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Stats {
  date: string;
  total_products: number;
  unique_stores: number;
  price_drops: number;
  biggest_drop: number;
  categories_count: number;
  avg_price_drop: number;
}

export interface ProductFilters {
  category?: string;
  store?: string;
  brand?: string;
  minPrice?: number;
  maxPrice?: number;
  search?: string;
}

// Build query string from filters
function buildQueryString(filters: ProductFilters): string {
  const params = new URLSearchParams();
  if (filters.category) params.append("category", filters.category);
  if (filters.store) params.append("store", filters.store);
  if (filters.brand) params.append("brand", filters.brand);
  if (filters.minPrice !== undefined)
    params.append("min_price", filters.minPrice.toString());
  if (filters.maxPrice !== undefined)
    params.append("max_price", filters.maxPrice.toString());
  if (filters.search) params.append("q", filters.search);
  return params.toString();
}

// API functions
export const api = {
  // Products
  async getProducts(filters: ProductFilters = {}): Promise<Product[]> {
    const queryString = buildQueryString(filters);
    const url = `${API_BASE_URL}/products${
      queryString ? `?${queryString}` : ""
    }`;
    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to fetch products");
    return response.json();
  },

  async getProduct(id: string): Promise<Product> {
    const response = await fetch(`${API_BASE_URL}/products/${id}`);
    if (!response.ok) throw new Error("Failed to fetch product");
    return response.json();
  },

  async getProductHistory(id: string, days: number = 30): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/products/${id}/history?days=${days}`
    );
    if (!response.ok) throw new Error("Failed to fetch product history");
    return response.json();
  },

  async getCategories(): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/products/categories`);
    if (!response.ok) throw new Error("Failed to fetch categories");
    return response.json();
  },

  async getBrands(): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/products/brands`);
    if (!response.ok) throw new Error("Failed to fetch brands");
    return response.json();
  },

  // Stores
  async getStores(): Promise<Store[]> {
    const response = await fetch(`${API_BASE_URL}/stores`);
    if (!response.ok) throw new Error("Failed to fetch stores");
    return response.json();
  },

  async getStore(id: string): Promise<Store> {
    const response = await fetch(`${API_BASE_URL}/stores/${id}`);
    if (!response.ok) throw new Error("Failed to fetch store");
    return response.json();
  },

  // Stats
  async getStats(): Promise<Stats> {
    const response = await fetch(`${API_BASE_URL}/stats`);
    if (!response.ok) throw new Error("Failed to fetch stats");
    return response.json();
  },

  async getTopDeals(limit: number = 10): Promise<Product[]> {
    const response = await fetch(
      `${API_BASE_URL}/stats/top-deals?limit=${limit}`
    );
    if (!response.ok) throw new Error("Failed to fetch top deals");
    return response.json();
  },

  async getStatsByCategory(): Promise<any[]> {
    const response = await fetch(`${API_BASE_URL}/stats/by-category`);
    if (!response.ok) throw new Error("Failed to fetch stats by category");
    return response.json();
  },
};

export default api;
