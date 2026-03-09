import { readFileSync } from "fs";
import path from "path";
import CatalogClient from "@/components/CatalogClient";
import type { Product, Meta, Translations } from "@/lib/types";

export const dynamic = "force-dynamic";

export default function CatalogPage() {
  const dataPath = path.join(process.cwd(), "data", "products.json");
  const metaPath = path.join(process.cwd(), "data", "meta.json");
  const translationsPath = path.join(process.cwd(), "data", "translations.json");
  const products: Product[] = JSON.parse(readFileSync(dataPath, "utf-8"));
  const meta: Meta = JSON.parse(readFileSync(metaPath, "utf-8"));
  const translations: Translations = JSON.parse(readFileSync(translationsPath, "utf-8"));
  return <CatalogClient products={products} meta={meta} translations={translations} />;
}
