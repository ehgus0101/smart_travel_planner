# app/collector.py
import argparse, json, os, sys, pathlib, datetime, time
from typing import Dict, Any, List, Tuple
import requests
from app.config import get_settings

OP = "areaBasedList1"

def try_request(url: str, params: Dict[str, Any], key: str, svc: str) -> requests.Response:
    """key는 'serviceKey' 또는 'ServiceKey'"""
    p = dict(params)
    if "%" in svc:
        full = f"{url}?{key}={svc}"
        return requests.get(full, params=p, timeout=25, allow_redirects=True)
    else:
        p[key] = svc
        return requests.get(url, params=p, timeout=25, allow_redirects=True)

def call_api(st, params: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """HTTPS 우선 → HTTP 폴백, 키 대/소문자 모두 시도. 성공 시 (data, 사용URL) 반환."""
    hosts = [st.BASE_URL, st.FALLBACK_URL]
    keys = ["serviceKey", "ServiceKey"]

    for base in hosts:
        url = f"{base}/{OP}"
        for key in keys:
            try:
                r = try_request(url, params, key, st.SERVICE_KEY)
                ctype = (r.headers.get("content-type") or "").lower()
                if "json" not in ctype:
                    # 에러 본문 저장 도움용
                    pathlib.Path("data/raw").mkdir(parents=True, exist_ok=True)
                    open("data/raw/last_non_json.txt", "w", encoding="utf-8").write(r.text)
                    continue
                data = r.json()
                code = (((data.get("response") or {}).get("header")) or {}).get("resultCode")
                if code == "0000":
                    return data, f"{url} [{key}]"
                else:
                    # 마지막 JSON 응답 보관
                    open("data/raw/last_json.json", "w", encoding="utf-8").write(
                        json.dumps(data, ensure_ascii=False, indent=2)
                    )
            except Exception as e:
                # 재시도 간단 딜레이
                time.sleep(0.5)
                continue
    raise SystemExit("모든 시도 실패: 유효한 JSON(resultCode=0000)을 받지 못했습니다.")

def extract_items(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    items = (((data.get("response") or {}).get("body") or {}).get("items") or {}).get("item") or []
    if isinstance(items, dict):
        items = [items]
    return items

def main():
    st = get_settings()
    if not st.SERVICE_KEY:
        print("Error: SERVICE_KEY가 비어있습니다. Secrets/환경변수 점검하세요.")
        sys.exit(1)

    ap = argparse.ArgumentParser(description="TarRlteTarService1 areaBasedList1 수집기")
    ap.add_argument("--baseYm", default="202504", help="기준연월 YYYYMM")
    ap.add_argument("--areaCd", default="51", help="시도 코드")
    ap.add_argument("--signguCd", default="51130", help="시군구 코드")
    ap.add_argument("--rows", type=int, default=20, help="한 페이지 결과 수(numOfRows)")
    ap.add_argument("--page", type=int, default=1, help="페이지 번호(pageNo)")
    args = ap.parse_args()

    params = {
        "MobileOS": st.MOBILE_OS,
        "MobileApp": st.MOBILE_APP,
        "_type": "json",
        "baseYm": args.baseYm,
        "areaCd": args.areaCd,
        "signguCd": args.signguCd,
        "numOfRows": args.rows,
        "pageNo": args.page,
    }

    data, used = call_api(st, params)
    items = extract_items(data)

    # 저장 위치
    today = datetime.date.today().strftime("%Y%m%d")
    outdir = pathlib.Path(f"data/raw/{today}")
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "pois.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    (outdir / "meta.json").write_text(json.dumps({"used_url": used, "params": params}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] count={len(items)}")
    print(f" - used: {used}")
    print(f" - saved: {outdir}/pois.json")

if __name__ == "__main__":
    main()
