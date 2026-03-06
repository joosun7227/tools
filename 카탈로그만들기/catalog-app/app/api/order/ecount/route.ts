import { NextRequest, NextResponse } from "next/server";

const COM_CODE = process.env.ECOUNT_COM_CODE!;
const API_CERT_KEY = process.env.ECOUNT_API_CERT_KEY!;
const ZONE = process.env.ECOUNT_ZONE!;
const EMP_CD = process.env.ECOUNT_EMP_CD!;
const WH_CD = process.env.ECOUNT_WH_CD!;

async function login(): Promise<string | null> {
  const res = await fetch(`https://oapi${ZONE}.ecount.com/OAPI/V2/OAPILogin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ COM_CODE, USER_ID: EMP_CD, API_CERT_KEY, LAN_TYPE: "ko-KR", ZONE }),
  });
  const data = await res.json();
  if (data?.Status === "200" && data?.Data?.Datas?.SESSION_ID) {
    return data.Data.Datas.SESSION_ID;
  }
  return null;
}

export async function POST(req: NextRequest) {
  const { orderInfo, items } = await req.json();

  if (!orderInfo.custCode) {
    return NextResponse.json({ success: false, error: "거래처코드가 필요합니다." }, { status: 400 });
  }

  const sessionId = await login();
  if (!sessionId) {
    return NextResponse.json({ success: false, error: "Ecount 로그인 실패" }, { status: 502 });
  }

  const ioDate = orderInfo.orderDate.replace(/-/g, "");

  const SaleList = items.map((item: { prodCd: string; unit: string; price: number; qty: number }) => ({
    BulkDatas: {
      IO_DATE: ioDate,
      CUST: orderInfo.custCode,
      EMP_CD,
      WH_CD,
      PROD_CD: item.prodCd,
      QTY: String(item.qty),
      USER_PRICE_VAT: String(item.price),
    },
  }));

  const res = await fetch(
    `https://oapi${ZONE}.ecount.com/OAPI/V2/Sale/SaveSale?SESSION_ID=${sessionId}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ SaleList }),
    }
  );

  const result = await res.json();

  if (result?.Status === "200") {
    return NextResponse.json({ success: true, message: "Ecount 판매 입력 완료" });
  } else {
    const errMsg = result?.Error?.Message || "알 수 없는 오류";
    return NextResponse.json({ success: false, error: errMsg }, { status: 502 });
  }
}
