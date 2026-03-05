export interface Product {
  id: number;
  prodCd: string;
  name: string;
  barcode: string;
  country: string;
  brand: string;
  category: string;
  spec: string;
  storage: string;
  price: number;
  imageFile: string | null;
}

export interface CartItem extends Product {
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
