import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { EcommerceLayout } from "./layouts/EcommerceLayout";
import { Home } from "./pages/Home";
import { Products } from "./pages/Products";
import { Stores } from "./pages/Stores";
import { Deals } from "./pages/Deals";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<EcommerceLayout />}>
          <Route index element={<Home />} />
          <Route path="products" element={<Products />} />
          <Route path="deals" element={<Deals />} />
          <Route path="stores" element={<Stores />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
