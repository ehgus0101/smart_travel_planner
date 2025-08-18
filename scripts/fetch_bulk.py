# scripts/fetch_bulk.py
import os, json, time, argparse
from pathlib import Path
from datetime import datetime
import requests
from app.config import get_settings

"""
여러 지역/시군구에 대해 TarRlteTarService1/areaBasedList1를 반복 호출하여
하루 폴더(data/raw/YYYYMMDD)에 개별 JSON과 통합 pois.json을 저장
"""

def build_params(st, area_cd, signgu_cd, page, rows):
    return {
        "MobileOS": st.MOBILE_OS,
        "MobileApp": st.MOBILE_APP,
        "_type": "json",
        "areaCode": area_cd,
        "sigunguCode": signgu_cd,
        "listYN": "Y",
        "arrange": "A",
        "numOfRows": rows,
        "pageNo": page,
    }

def safe_get(url, params, svc):
    # serviceKey(인코딩 유무)에 따라 전달
    if "%" in svc:
        full = f"{url}?serviceKey={svc}"
        r = requests.get(full, params=params, timeout=20)
    else:
        r = requests.get(url, params={**params, "serviceKey": svc}, timeout=20)
    r.raise_for_status()
    return r

def fetch_one_region(st, area_cd, signgu_cd, rows=100, max_pages=50, base_url_override=None):
    url = (base_url_override or st.BASE_URL).rstrip("/") + "/areaBasedList1"
    all_items = []
    used_url = None
    for page in range(1, max_pages + 1):
        params = build_params(st, area_cd, signgu_cd, page, rows)
        r = safe_get(url, params, st.SERVICE_KEY.strip())
        used_url = r.url
        # JSON 파싱
        try:
            data = r.json()
        except Exception:
            # SOAP/HTML 등일 경우 종료
            break
        header = (((data.get("response") or {}).get("header")) or {})
        code = header.get("resultCode")
        if code != "0000":
            break
        items = (((data.get("response") or {}).get("body") or {}).get("items") or {}).get("item") or []
        if isinstance(items, dict):
            items = [items]
        if not items:
            break
        for it in items:
            it["baseYm"] = it.get("baseYm") or datetime.utcnow().strftime("%Y%m")
            all_items.append(it)
        # 페이지 소진 조건: numOfRows 보다 적게 올 때
        if len(items) < rows:
            break
        time.sleep(0.2)
    return all_items, used_url

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="data/seed/regions.csv")
    ap.add_argument("--rows", type=int, default=200)
    ap.add_argument("--max-pages", type=int, default=40)
    ap.add_argument("--base-url", default="")  # 필요시 https로 시도 안될 때 http 등
    args = ap.parse_args()

    st = get_settings()
    if not st.SERVICE_KEY:
        raise SystemExit("SERVICE_KEY가 비어있습니다. .env 또는 GitHub Secrets를 확인하세요.")

    # 저장 경로
    date_tag = datetime.utcnow().strftime("%Y%m%d")
    out_dir = Path(f"data/raw/{date_tag}")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 시드 읽기
    rows = []
    with open(args.seed, "r", encoding="utf-8") as f:
        header = None
        for i, line in enumerate(f):
            line = line.strip()
            if not line: 
                continue
            if i == 0:
                header = [h.strip() for h in line.split(",")]
                continue
            cols = [c.strip() for c in line.split(",")]
            rec = dict(zip(header, cols))
            rows.append(rec)

    grand = []
    for rec in rows:
        area_cd = rec["areaCd"]
        signgu_cd = rec["signguCd"]
        items, used = fetch_one_region(
            st, area_cd, signgu_cd, rows=args.rows, max_pages=args.max_pages,
            base_url_override=(args.base_url or None),
        )
        # 개별 저장
        unit_path = out_dir / f"{area_cd}_{signgu_cd}.json"
        with open(unit_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"[OK] {area_cd}-{signgu_cd}: {len(items)}  -> {unit_path.name}")
        grand.extend(items)

    # 통합 저장
    pois_path = out_dir / "pois.json"
    with open(pois_path, "w", encoding="utf-8") as f:
        json.dump(grand, f, ensure_ascii=False, indent=2)
    print(f"[DONE] 통합 저장: {pois_path} (rows={len(grand)})")

if __name__ == "__main__":
    main()
