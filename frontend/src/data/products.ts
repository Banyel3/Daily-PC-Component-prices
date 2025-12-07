export interface Product {
  id: string;
  name: string;
  price: number;
  currency: string;
  image: string;
  category: string;
  store: string;
  brand: string;
  url: string;
  lastUpdated: string;
  priceChange: number; // percentage change, negative means price drop
}

export const products: Product[] = [
  {
    id: '1',
    name: 'NVIDIA GeForce RTX 4090',
    price: 1599.99,
    currency: 'USD',
    image: 'https://placehold.co/300x200?text=RTX+4090',
    category: 'GPU',
    store: 'Amazon',
    brand: 'NVIDIA',
    url: 'https://amazon.com',
    lastUpdated: '2025-12-07T10:00:00Z',
    priceChange: -5.2,
  },
  {
    id: '2',
    name: 'AMD Ryzen 9 7950X',
    price: 599.00,
    currency: 'USD',
    image: 'https://placehold.co/300x200?text=Ryzen+9+7950X',
    category: 'CPU',
    store: 'Newegg',
    brand: 'AMD',
    url: 'https://newegg.com',
    lastUpdated: '2025-12-07T09:30:00Z',
    priceChange: 0,
  },
  {
    id: '3',
    name: 'Samsung 990 PRO 2TB',
    price: 169.99,
    currency: 'USD',
    image: 'https://placehold.co/300x200?text=Samsung+990+PRO',
    category: 'Storage',
    store: 'Best Buy',
    brand: 'Samsung',
    url: 'https://bestbuy.com',
    lastUpdated: '2025-12-07T11:15:00Z',
    priceChange: -12.5,
  },
  {
    id: '4',
    name: 'Corsair Vengeance DDR5 32GB',
    price: 129.99,
    currency: 'USD',
    image: 'https://placehold.co/300x200?text=DDR5+32GB',
    category: 'RAM',
    store: 'Amazon',
    brand: 'Corsair',
    url: 'https://amazon.com',
    lastUpdated: '2025-12-06T14:20:00Z',
    priceChange: 2.1,
  },
  {
    id: '5',
    name: 'ASUS ROG Strix Z790-E',
    price: 499.99,
    currency: 'USD',
    image: 'https://placehold.co/300x200?text=Z790-E',
    category: 'Motherboard',
    store: 'Micro Center',
    brand: 'ASUS',
    url: 'https://microcenter.com',
    lastUpdated: '2025-12-07T08:45:00Z',
    priceChange: 0,
  },
  {
    id: '6',
    name: 'Lian Li O11 Dynamic Evo',
    price: 169.99,
    currency: 'USD',
    image: 'https://placehold.co/300x200?text=O11+Dynamic',
    category: 'Case',
    store: 'Newegg',
    brand: 'Lian Li',
    url: 'https://newegg.com',
    lastUpdated: '2025-12-07T10:30:00Z',
    priceChange: -8.4,
  },
];
