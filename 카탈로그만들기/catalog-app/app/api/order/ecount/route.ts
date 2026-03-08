import { NextRequest, NextResponse } from "next/server";

const COM_CODE     = process.env.ECOUNT_COM_CODE     ?? "665496";
const API_CERT_KEY = process.env.ECOUNT_API_CERT_KEY ?? "";
const ZONE         = process.env.ECOUNT_ZONE         ?? "AA";
const USER_ID      = process.env.ECOUNT_USER_ID      ?? "";  // 로그인 ID (API 인증키 발급 ID)
const EMP_CD       = process.env.ECOUNT_EMP_CD       ?? "";  // 담당자 코드 (주문서에 기록)
const WH_CD        = process.env.ECOUNT_WH_CD        ?? "100";

const BASE_URL = "https://oapi" + ZONE + ".ecount.com";

type LoginResult = { sessionId: string } | { error: string; raw?: unknown };

async function login(): Promise<LoginResult> {
  const loginUrl = BASE_URL + "/OAPI/V2/OAPILogin";
  console.log("[Ecount Login URL]", loginUrl);
  let res: Response;
  try {
    res = await fetch(loginUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ COM_CODE, USER_ID, API_CERT_KEY, LAN_TYPE: "ko-KR", ZONE }),
    });
  } catch (e) {
    return { error: `[로그인 실패] 네트워크 오류: ${String(e)}` };
  }
  console.log("[Ecount Login HTTP]", res.status, res.statusText);
  let data: unknown;
  try {
    data = await res.json();
  } catch {
    const text = await res.text().catch(() => "(body read failed)");
    return { error: `[로그인 실패] JSON 파싱 오류 (HTTP ${res.status}) | ${text.slice(0, 200)}` };
  }
  console.log("[Ecount Login]", JSON.stringify(data).slice(0, 400));

  const d = data as Record<string, unknown>;
  if (String(d?.Status) === "200" && (d?.Data as Record<string, unknown>)?.Datas && ((d?.Data as Record<string, unknown>)?.Datas as Record<string, unknown>)?.SESSION_ID) {
    return { sessionId: String(((d?.Data as Record<string, unknown>)?.Datas as Record<string, unknown>)?.SESSION_ID) };
  }

  // 이카운트 오류 코드별 메시지 (Data.Code 또는 Error.Code)
  const rawErrCode = (d?.Error as Record<string, unknown>)?.Code ?? ((d?.Data as Record<string, unknown>)?.Code);
  const errCode = rawErrCode != null ? Number(rawErrCode) : null;
  const errMsg  = String((d?.Error as Record<string, unknown>)?.Message ?? (d?.Data as Record<string, unknown>)?.Message ?? "");
  const codeDesc: Record<number, string> = {
    20:  "로그인 정보 오류 (COM_CODE/USER_ID 확인)",
    99:  "해당 USER_ID가 존재하지 않음",
    201: "API_CERT_KEY가 유효하지 않음",
    204: "테스트용/실서버용 인증키 불일치",
    21:  "임시접속차단 - 마스터에게 문의",
    24:  "IP 차단 - 마스터에게 문의",
    25:  "IP 차단(회사) - 마스터에게 문의",
    81:  "미수차단으로 API 이용 불가",
    98:  "비밀번호 5회 이상 오류 - 마스터에게 문의",
  };
  const desc = (errCode !== null && !isNaN(errCode)) ? (codeDesc[errCode] ?? `오류코드 ${errCode}`) : `응답 이상 (HTTP ${res.status})`;
  return { error: `[로그인 실패] ${desc}${errMsg ? ` | ${errMsg}` : ""}`, raw: data };
}

export async function POST(req: NextRequest) {
  const { orderInfo, items } = await req.json();

  if (!orderInfo.custCode) {
    return NextResponse.json({ success: false, error: "거래처코드가 필요합니다." }, { status: 400 });
  }

  console.log("[Ecount ENV] COM_CODE:", COM_CODE, "ZONE:", ZONE, "EMP_CD:", EMP_CD, "WH_CD:", WH_CD);

  const loginResult = await login();
  if ("error" in loginResult) {
    return NextResponse.json({ success: false, error: loginResult.error, raw: loginResult.raw }, { status: 502 });
  }
  const { sessionId } = loginResult;

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
    BASE_URL + "/OAPI/V2/Sale/SaveSale?SESSION_ID=" + sessionId,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ SaleList }),
    }
  );

  const result = await res.json();
  console.log("[Ecount SaveSale]", JSON.stringify(result).slice(0, 500));

  const successCnt = result?.Data?.SuccessCnt ?? 0;
  const failCnt    = result?.Data?.FailCnt    ?? 0;

  if (String(result?.Status) === "200" && successCnt > 0 && failCnt === 0) {
    return NextResponse.json({ success: true, message: "Ecount 판매 입력 완료" });
  } else {
    const details = result?.Data?.ResultDetails as Array<{ Errors: Array<{ Message: string }> }> | undefined;
    const detailMsg = details?.flatMap(d => d.Errors.map(e => e.Message)).filter(Boolean).join(" / ");
    const errMsg =
      detailMsg ||
      result?.Error?.Message ||
      result?.Errors?.[0]?.Message ||
      JSON.stringify(result).slice(0, 300);
    return NextResponse.json({ success: false, error: errMsg, raw: result }, { status: 502 });
  }
}
