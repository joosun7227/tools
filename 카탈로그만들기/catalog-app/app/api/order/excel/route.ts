import { NextRequest, NextResponse } from "next/server";
import * as XLSX from "xlsx";

export async function POST(req: NextRequest) {
  const { orderInfo, items } = await req.json();

  const wb = XLSX.utils.book_new();

  // 주문 헤더 시트
  const headerData = [
    ["그라미스 주문서"],
    [],
    ["거래처코드", orderInfo.custCode],
    ["거래처명", orderInfo.custName],
    ["담당자", orderInfo.managerName],
    ["연락처", orderInfo.phone],
    ["주문일", orderInfo.orderDate],
    ["비고", orderInfo.note],
    [],
    ["번호", "품목코드", "품목명", "바코드", "규격", "소비자가", "주문수량", "금액"],
  ];

  items.forEach((item: {prodCd: string; name: string; barcode: string; spec: string; price: number; qty: number}, idx: number) => {
    headerData.push([
      String(idx + 1),
      item.prodCd,
      item.name,
      item.barcode,
      item.spec,
      String(item.price),
      String(item.qty),
      String(item.price * item.qty),
    ]);
  });

  const total = items.reduce((s: number, i: {price: number; qty: number}) => s + i.price * i.qty, 0);
  headerData.push([], ["", "", "", "", "", "", "합계", String(total)]);

  const ws = XLSX.utils.aoa_to_sheet(headerData);

  // 컬럼 너비 설정
  ws["!cols"] = [
    { wch: 5 }, { wch: 12 }, { wch: 35 }, { wch: 16 },
    { wch: 16 }, { wch: 10 }, { wch: 8 }, { wch: 12 },
  ];

  XLSX.utils.book_append_sheet(wb, ws, "주문서");

  const buf = XLSX.write(wb, { type: "buffer", bookType: "xlsx" });

  const filename = `그라미스_주문서_${orderInfo.orderDate.replace(/-/g, "")}.xlsx`;

  return new NextResponse(buf, {
    headers: {
      "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "Content-Disposition": `attachment; filename*=UTF-8''${encodeURIComponent(filename)}`,
    },
  });
}
