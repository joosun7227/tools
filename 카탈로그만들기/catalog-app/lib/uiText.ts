import type { Lang } from "@/lib/types";

const UI: Record<string, Record<Lang | "en", string>> = {
  all:          { ko: "전체",       th: "ทั้งหมด",           vi: "Tất cả",        en: "All" },
  newItems:     { ko: "🆕 신규 품목", th: "🆕 สินค้าใหม่",      vi: "🆕 Hàng mới",   en: "🆕 New Items" },
  allCategory:  { ko: "전체 카테고리", th: "ทุกหมวดหมู่",       vi: "Tất cả danh mục", en: "All Categories" },
  allCountry:   { ko: "전체 국가",   th: "ทุกประเทศ",          vi: "Tất cả quốc gia", en: "All Countries" },
  allStorage:   { ko: "전체 보관",   th: "การเก็บทั้งหมด",     vi: "Tất cả bảo quản", en: "All Storage" },
  reset:        { ko: "초기화 ×",   th: "รีเซ็ต ×",           vi: "Đặt lại ×",     en: "Reset ×" },
  noResult:     { ko: "검색 결과가 없습니다.", th: "ไม่พบผลลัพธ์", vi: "Không tìm thấy kết quả.", en: "No results found." },
  searchPlaceholder: { ko: "상품명, 브랜드 검색...", th: "ค้นหาสินค้า, แบรนด์...", vi: "Tìm sản phẩm, thương hiệu...", en: "Search products, brands..." },
  cart:         { ko: "장바구니",   th: "ตะกร้าสินค้า",       vi: "Giỏ hàng",      en: "Cart" },
  cartEmpty:    { ko: "담긴 상품이 없습니다.", th: "ตะกร้าว่างเปล่า", vi: "Giỏ hàng trống.", en: "Cart is empty." },
  clearAll:     { ko: "전체삭제",   th: "ล้างทั้งหมด",         vi: "Xóa tất cả",    en: "Clear all" },
  clearConfirm: { ko: "장바구니를 전체 비우시겠습니까?", th: "ล้างตะกร้าทั้งหมดหรือไม่?", vi: "Xóa toàn bộ giỏ hàng?", en: "Clear all items from cart?" },
  order:        { ko: "주문하기",   th: "สั่งซื้อ",            vi: "Đặt hàng",      en: "Order" },
  prev:         { ko: "← 이전",    th: "← ก่อนหน้า",          vi: "← Trước",       en: "← Prev" },
  next:         { ko: "다음 →",    th: "ถัดไป →",             vi: "Tiếp →",        en: "Next →" },
  latestCount:  { ko: "최신",      th: "ล่าสุด",               vi: "Mới nhất",      en: "Latest" },
  orderTitle:   { ko: "주문서 작성", th: "กรอกใบสั่งซื้อ",     vi: "Tạo đơn hàng",  en: "Create Order" },
  back:         { ko: "← 뒤로",    th: "← กลับ",              vi: "← Quay lại",    en: "← Back" },
  custInfo:     { ko: "거래처 정보", th: "ข้อมูลลูกค้า",        vi: "Thông tin khách", en: "Customer Info" },
  custCode:     { ko: "거래처코드 *", th: "รหัสลูกค้า *",       vi: "Mã khách hàng *", en: "Customer Code *" },
  manager:      { ko: "담당자",     th: "ผู้รับผิดชอบ",         vi: "Người phụ trách", en: "Manager" },
  phone:        { ko: "연락처",     th: "เบอร์โทรศัพท์",       vi: "Số điện thoại",  en: "Phone" },
  orderDate:    { ko: "주문일",     th: "วันที่สั่งซื้อ",       vi: "Ngày đặt hàng",  en: "Order Date" },
  note:         { ko: "비고",       th: "หมายเหตุ",            vi: "Ghi chú",        en: "Note" },
  orderItems:   { ko: "주문 상품",  th: "สินค้าที่สั่ง",         vi: "Sản phẩm đặt",   en: "Order Items" },
  clearCart:    { ko: "전체 비우기", th: "ล้างทั้งหมด",         vi: "Xóa tất cả",    en: "Clear all" },
  cartEmpty2:   { ko: "장바구니가 비어있습니다.", th: "ตะกร้าว่างเปล่า", vi: "Giỏ hàng trống.", en: "Cart is empty." },
  goToCatalog:  { ko: "카탈로그로 돌아가기", th: "กลับสู่แคตตาล็อก", vi: "Quay lại danh mục", en: "Back to Catalog" },
  excelDownload: { ko: "엑셀 주문서 다운로드", th: "ดาวน์โหลดใบสั่งซื้อ Excel", vi: "Tải đơn hàng Excel", en: "Download Excel Order" },
  excelLoading:  { ko: "엑셀 생성 중...", th: "กำลังสร้าง Excel...", vi: "Đang tạo Excel...", en: "Generating Excel..." },
  ecountSending: { ko: "전송 중...", th: "กำลังส่ง...", vi: "Đang gửi...", en: "Sending..." },
  enterCustCode: { ko: "거래처코드 입력 후 Ecount 자동입력 가능", th: "กรอกรหัสลูกค้าเพื่อส่ง Ecount", vi: "Nhập mã khách hàng để gửi Ecount", en: "Enter customer code to submit to Ecount" },
  ecountSuccess: { ko: "Ecount 주문 입력 완료!", th: "บันทึกคำสั่งซื้อ Ecount สำเร็จ!", vi: "Đã nhập đơn hàng Ecount thành công!", en: "Ecount order submitted successfully!" },
  ecountFail:    { ko: "Ecount 전송 실패", th: "ส่ง Ecount ไม่สำเร็จ", vi: "Gửi Ecount thất bại", en: "Ecount submission failed" },
};

export function t(key: keyof typeof UI, lang: Lang | "en"): string {
  return UI[key]?.[lang] ?? UI[key]?.["ko"] ?? key;
}
