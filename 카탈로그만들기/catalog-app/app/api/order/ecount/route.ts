import { NextRequest, NextResponse } from "next/server";

// Edge Runtime: preferredRegion이 동작하려면 필요
export const runtime = "edge";
// Ecount 서버가 한국에 있으므로 서울 리전에서 실행 (GeoDNS 우회)
export const preferredRegion = "icn1";

// ─── 계정 설정 (trim: vercel env add 시 줄바꿈 방지) ─────────
const e = (v: string | undefined, fallback = "") => (v ?? fallback).trim();
const ACCOUNTS = {
  "1": {
    label:        e(process.env.ECOUNT_LABEL,        "예주나라"),
    COM_CODE:     e(process.env.ECOUNT_COM_CODE,     "665496"),
    API_CERT_KEY: e(process.env.ECOUNT_API_CERT_KEY),
    ZONE:         e(process.env.ECOUNT_ZONE,         "AA"),
    USER_ID:      e(process.env.ECOUNT_USER_ID),
    EMP_CD:       e(process.env.ECOUNT_EMP_CD),
    WH_CD:        e(process.env.ECOUNT_WH_CD,        "100"),
    BASE_URL:     e(process.env.ECOUNT_BASE_URL),
  },
  "2": {
    label:        e(process.env.ECOUNT_2_LABEL,        "5팀"),
    COM_CODE:     e(process.env.ECOUNT_2_COM_CODE,     "670393"),
    API_CERT_KEY: e(process.env.ECOUNT_2_API_CERT_KEY),
    ZONE:         e(process.env.ECOUNT_2_ZONE,         "AA"),
    USER_ID:      e(process.env.ECOUNT_2_USER_ID),
    EMP_CD:       e(process.env.ECOUNT_2_EMP_CD),
    WH_CD:        e(process.env.ECOUNT_2_WH_CD,        "400"),
    BASE_URL:     e(process.env.ECOUNT_2_BASE_URL),
  },
} as const;

type AccountKey = keyof typeof ACCOUNTS;
type LoginResult = { sessionId: string; baseUrl: string } | { error: string; raw?: unknown };

async function login(acc: typeof ACCOUNTS[AccountKey]): Promise<LoginResult> {
  const { COM_CODE, USER_ID, API_CERT_KEY, ZONE } = acc;
  const baseUrl = acc.BASE_URL || ("https://oapi" + ZONE + ".ecount.com");
  const loginUrl = baseUrl + "/OAPI/V2/OAPILogin";
  console.log("[Ecount Login]", acc.label, loginUrl);

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

  let data: unknown;
  try { data = await res.json(); }
  catch {
    const text = await res.text().catch(() => "(body read failed)");
    return { error: `[로그인 실패] JSON 파싱 오류 (HTTP ${res.status}) | ${text.slice(0, 200)}` };
  }
  console.log("[Ecount Login result]", JSON.stringify(data).slice(0, 400));

  const d = data as Record<string, unknown>;
  const datas = (d?.Data as Record<string, unknown>)?.Datas as Record<string, unknown> | undefined;
  if (String(d?.Status) === "200" && datas?.SESSION_ID) {
    // HOST_URL이 있으면 그걸 우선 사용 (테스트/실서버 환경에 따라 다른 호스트로 안내)
    const hostUrl = datas?.HOST_URL ? `https://${datas.HOST_URL}` : baseUrl;
    return { sessionId: String(datas.SESSION_ID), baseUrl: hostUrl };
  }

  const rawErrCode = (d?.Error as Record<string, unknown>)?.Code ?? (d?.Data as Record<string, unknown>)?.Code;
  const errCode = rawErrCode != null ? Number(rawErrCode) : null;
  const errMsg  = String((d?.Error as Record<string, unknown>)?.Message ?? (d?.Data as Record<string, unknown>)?.Message ?? "");
  const codeDesc: Record<number, string> = {
    20: "로그인 정보 오류 (COM_CODE/USER_ID 확인)", 99: "USER_ID 없음",
    201: "API_CERT_KEY 유효하지 않음", 204: "테스트/실서버 인증키 불일치",
    21: "임시접속차단", 24: "IP 차단", 25: "IP 차단(회사)", 81: "미수차단", 98: "비밀번호 오류",
  };
  const desc = (errCode !== null && !isNaN(errCode)) ? (codeDesc[errCode] ?? `오류코드 ${errCode}`) : `응답 이상 (HTTP ${res.status})`;
  return { error: `[${acc.label} 로그인 실패] ${desc}${errMsg ? ` | ${errMsg}` : ""}`, raw: data };
}

export async function POST(req: NextRequest) {
  const { orderInfo, items, accountKey } = await req.json();

  const key: AccountKey = accountKey === "2" ? "2" : "1";
  const acc = ACCOUNTS[key];

  if (!acc.API_CERT_KEY || !acc.USER_ID) {
    return NextResponse.json({ success: false, error: `[${acc.label}] 환경변수 ECOUNT_${key === "2" ? "2_" : ""}API_CERT_KEY / USER_ID 가 설정되지 않았습니다.` }, { status: 400 });
  }
  if (!orderInfo.custCode) {
    return NextResponse.json({ success: false, error: "거래처코드가 필요합니다." }, { status: 400 });
  }

  const loginResult = await login(acc);
  if ("error" in loginResult) {
    return NextResponse.json({ success: false, error: loginResult.error, raw: loginResult.raw }, { status: 502 });
  }
  const { sessionId, baseUrl } = loginResult;

  const ioDate        = orderInfo.orderDate.replace(/-/g, "");
  const empCd         = orderInfo.managerName || acc.EMP_CD;
  const REMARK        = orderInfo.phone ?? "";
  const ADD_LTXT_01_T = orderInfo.note  ?? "";

  const SaleOrderList = items.map((item: { prodCd: string; unit: string; price: number; qty: number }) => ({
    BulkDatas: {
      IO_DATE: ioDate,
      CUST:    orderInfo.custCode,
      EMP_CD:  empCd,
      WH_CD:   acc.WH_CD,
      PROD_CD: item.prodCd,
      QTY:     String(item.qty),
      USER_PRICE_VAT: "",
      REMARK,
      ADD_LTXT_01_T,
    },
  }));

  const res = await fetch(baseUrl + "/OAPI/V2/SaleOrder/SaveSaleOrder?SESSION_ID=" + sessionId, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ SaleOrderList }),
  });

  const result = await res.json();
  console.log("[Ecount SaveSaleOrder]", JSON.stringify(result).slice(0, 500));

  const successCnt = result?.Data?.SuccessCnt ?? 0;
  const failCnt    = result?.Data?.FailCnt    ?? 0;

  if (String(result?.Status) === "200" && successCnt > 0 && failCnt === 0) {
    return NextResponse.json({ success: true, message: `${acc.label} 수주 입력 완료` });
  }

  const details = result?.Data?.ResultDetails as Array<{ Errors: Array<{ Message: string }> }> | undefined;
  const detailMsg = details?.flatMap(d => d.Errors.map(e => e.Message)).filter(Boolean).join(" / ");
  const errMsg = detailMsg || result?.Error?.Message || result?.Errors?.[0]?.Message || JSON.stringify(result).slice(0, 300);
  return NextResponse.json({ success: false, error: errMsg, raw: result }, { status: 502 });
}
