import { useState, useEffect } from "react";
import api from "../api";
import type { Stats, Product } from "../api";

interface UseStatsResult {
  stats: Stats | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useStats(): UseStatsResult {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch stats");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return { stats, loading, error, refetch: fetchStats };
}

interface UseTopDealsResult {
  deals: Product[];
  loading: boolean;
  error: string | null;
}

export function useTopDeals(limit: number = 10): UseTopDealsResult {
  const [deals, setDeals] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getTopDeals(limit)
      .then(setDeals)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "Failed to fetch deals")
      )
      .finally(() => setLoading(false));
  }, [limit]);

  return { deals, loading, error };
}
