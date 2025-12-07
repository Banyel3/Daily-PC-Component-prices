import { ExternalLink, ShoppingBag } from 'lucide-react';

const supportedStores = [
  {
    id: 'amazon',
    name: 'Amazon',
    url: 'https://amazon.com',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg',
    description: 'Global e-commerce giant with a vast selection of PC components.',
    status: 'Active',
  },
  {
    id: 'newegg',
    name: 'Newegg',
    url: 'https://newegg.com',
    logo: 'https://c1.neweggimages.com/WebResource/Themes/Nest/logos/Newegg_full_color_logo_RGB.SVG',
    description: 'Leading tech-focused e-retailer in North America.',
    status: 'Active',
  },
  {
    id: 'bestbuy',
    name: 'Best Buy',
    url: 'https://bestbuy.com',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/f/f5/Best_Buy_Logo.svg',
    description: 'Consumer electronics retailer with both online and physical stores.',
    status: 'Active',
  },
  {
    id: 'microcenter',
    name: 'Micro Center',
    url: 'https://microcenter.com',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/f/f5/Micro_Center_Logo.png', // Placeholder or actual if available
    description: 'Computer department store known for in-store deals and bundles.',
    status: 'Active',
  },
];

export const Stores = () => {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Supported Stores</h1>
        <p className="text-gray-500 mt-1">We currently track prices from these major retailers.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {supportedStores.map((store) => (
          <div key={store.id} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="h-16 flex items-center mb-6">
               {/* Fallback to text if logo fails or for simplicity in this demo */}
               <div className="flex items-center gap-3">
                 <div className="p-3 bg-blue-50 rounded-xl text-blue-600">
                   <ShoppingBag size={24} />
                 </div>
                 <h3 className="text-xl font-bold text-gray-900">{store.name}</h3>
               </div>
            </div>
            
            <p className="text-gray-500 mb-6 h-12">{store.description}</p>
            
            <div className="flex items-center justify-between pt-4 border-t border-gray-50">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                {store.status}
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
    </div>
  );
};
