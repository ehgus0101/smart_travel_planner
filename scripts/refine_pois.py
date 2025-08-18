# scripts/refine_pois.py
from pathlib import Path
import pandas as pd

SRC = Path("data/processed/clean_pois.parquet")
DST_DIR = Path("data/processed")
DST = DST_DIR / "final_pois.parquet"
PREVIEW = Path("notebooks/output/final_preview.csv")

def refine(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    print("[refine] input rows:", len(df))

    # 1) 텍스트 정규화
    for c in df.select_dtypes(include="object").columns:
        df[c] = (
            df[c].astype(str)
                 .str.replace("\u3000"," ", regex=False)
                 .str.replace(r"\s+"," ", regex=True)
                 .str.strip()
        )

    # 2) baseYm_dt 보강
    if "baseYm_dt" not in df.columns and "baseYm" in df.columns:
        base = df["baseYm"].astype(str).str.replace(r"\D","", regex=True).str.slice(0,6).str.pad(6, fillchar="0")
        df["baseYm_dt"] = pd.to_datetime(base + "01", format="%Y%m%d", errors="coerce")

    # 3) 랭크 숫자화
    if "rlteRank_num" not in df.columns and "rlteRank" in df.columns:
        df["rlteRank_num"] = pd.to_numeric(df["rlteRank"], errors="coerce")

    # 4) 랭크 범위 필터(유연화)
    if "rlteRank_num" in df.columns:
        before = len(df)
        # 유효값이 아예 없으면 필터를 건너지 않음
        nonnull = df["rlteRank_num"].notna().sum()
        if nonnull > 0:
            # 합리적 범위 추정: [1, max(20, 상위 95%값)]
            q95 = pd.to_numeric(df["rlteRank_num"], errors="coerce").quantile(0.95)
            upper = max(20, (int(q95) if pd.notna(q95) else 20))
            df = df[df["rlteRank_num"].between(1, upper, inclusive="both")]
            print(f"[refine] rank filter: {before} -> {len(df)} (upper={upper})")
        else:
            print("[refine] rank filter skipped (no valid rlteRank_num)")
    else:
        print("[refine] rank column missing, skip range filter")

    # 5) 불필요 코드 컬럼 제거(있을 때만)
    drop_candidates = [
        "tAtsCd", "rlteTatsCd", "rlteRegnCd", "rlteSignguCd",
        "rlteCtgryLclsCd", "rlteCtgryMclsCd", "rlteCtgrySclsCd"
    ]
    drop_cols = [c for c in drop_candidates if c in df.columns]
    if drop_cols:
        df = df.drop(columns=drop_cols, errors="ignore")

    # 6) 중복 제거 (너무 강하면 완화)
    key_cols = [c for c in ["areaNm", "signguNm", "rlteTatsNm"] if c in df.columns]
    if key_cols:
        before = len(df)
        df = df.sort_values(["rlteRank_num"], na_position="last").drop_duplicates(subset=key_cols, keep="first")
        print(f"[refine] dedup by {key_cols}: {before} -> {len(df)}")
    else:
        print("[refine] dedup skipped (key cols missing)")

    # 7) 컬럼 순서
    preferred = [
        "baseYm","baseYm_dt","areaNm","signguNm",
        "tAtsNm","rlteTatsNm",
        "rlteCtgryLclsNm","rlteCtgryMclsNm","rlteCtgrySclsNm",
        "rlteRank","rlteRank_num"
    ]
    cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
    df = df[cols]

    if len(df) == 0:
        # 바로 실패하지 말고 원본 일부라도 살려서 문제를 보고할 수 있게 CSV 미리보기 떨굼
        sample = df.head(0)
        print("[refine][WARN] result empty — rank filter or dedup may be too strict.")
    return df

def main():
    if not SRC.exists():
        raise SystemExit(f"입력 파일이 없습니다: {SRC}")
    df = pd.read_parquet(SRC)
    out = refine(df)

    # 결과가 비어도 파일은 남겨서 UI/디버깅 가능하게 함
    DST_DIR.mkdir(parents=True, exist_ok=True)
    if len(out) == 0:
        # 비어있으면 CSV로라도 로그 남김
        (Path("notebooks/output")).mkdir(parents=True, exist_ok=True)
        df.head(100).to_csv("notebooks/output/refine_input_sample.csv", index=False, encoding="utf-8-sig")
        print("[refine] saved input sample to notebooks/output/refine_input_sample.csv")
        raise SystemExit("정제 후 결과가 비었습니다. notebooks/output/refine_input_sample.csv를 참고하여 필터 조건을 조정하세요.")

    out.to_parquet(DST, index=False)
    (Path("notebooks/output")).mkdir(parents=True, exist_ok=True)
    out.head(50).to_csv("notebooks/output/final_preview.csv", index=False, encoding="utf-8-sig")
    print(f"[OK] saved -> {DST} (rows={len(out)})")
    print("      preview -> notebooks/output/final_preview.csv")

if __name__ == "__main__":
    main()
