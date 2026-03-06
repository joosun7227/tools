export interface ProductUnit {
  prodCd: string;
  unit: string;
  price: number;
  spec: string;
}

export interface Product {
  id: number;
  name: string;
  country: string;
  brand: string;
  category: string;
  storage: string;
  imageFile: string | null;
  units: ProductUnit[];
}

export interface CartItem {
  id: string;         // prodCd (unique per unit)
  productId: number;
  name: string;
  prodCd: string;
  unit: string;
  price: number;
  spec: string;
  qty: number;
}

export interface OrderInfo {
  custCode: string;
  custName: string;
  managerName: string;
  phone: string;
  orderDate: string;
  note: string;
}

export interface Meta {
  categories: string[];
  countries: string[];
  storages: string[];
}
