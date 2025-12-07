import { useState, useEffect } from "react";
import api from "../api";
import type { Store } from "../api";

interface UseStoresResult {
  stores: Store[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useStores(): UseStoresResult {
  const [stores, setStores] = useState<Store[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStores = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStores();
      setStores(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch stores");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStores();
  }, []);

  return { stores, loading, error, refetch: fetchStores };
}
