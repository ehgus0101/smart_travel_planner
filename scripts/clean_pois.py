# scripts/clean_pois.py
from __future__ import annotations
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _coerce_rank(s: pd.Series) -> pd.Series:
    """문자/숫자 혼합 랭크를 안전하게 숫자로 변환."""
    return pd.to_numeric(s, errors="coerce")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """TarRlteTarService1 관련 POI 원본을 정제."""
    df = df.copy()

    # 컬럼 공백 제거 (대소문자 규칙은 팀 컨벤션에 맞춰 필요시 적용)
    df.columns = [c.strip() for c in df.columns]

    # --- baseYm -> datetime (안전 변환) ---
    if "baseYm" in df.columns:
        # 1) 문자열화 (숫자/문자 혼합 대비)
        bym = df["baseYm"].astype(str)
        # 2) 숫자만 남기고 6자리(YYYYMM)까지 자르기
        bym = bym.str.replace(r"\D", "", regex=True).str.slice(0, 6)
        # 3) 6자 미만이면 패딩(희귀 케이스 방어)
        bym = bym.str.pad(6, fillchar="0")
        # 4) 날짜 문자열 만들기(YYYYMM01) -> datetime
        df["baseYm_dt"] = pd.to_datetime(bym + "01", format="%Y%m%d", errors="coerce")

    # --- 랭크 숫자화 (문자/숫자 혼합 대비) ---
    if "rlteRank" in df.columns:
        df["rlteRank_num"] = _coerce_rank(df["rlteRank"])

    # --- 중복/결측 기본 정리(예시) ---
    key_cols = [c for c in ["tAtsNm", "rlteTatsNm"] if c in df.columns]
    if key_cols:
        df = df.drop_duplicates(key_cols)

    # 분석/추천 가독성을 위한 컬럼 정렬(존재하는 것만 유지)
    prefer_order = [
        "baseYm", "baseYm_dt",
        "tAtsNm", "areaNm", "signguNm",
        "rlteTatsNm", "rlteRegnNm", "rlteSignguNm",
        "rlteCtgryLclsNm", "rlteCtgryMclsNm", "rlteCtgrySclsNm",
        "rlteRank", "rlteRank_num",
    ]
    cols = [c for c in prefer_order if c in df.columns] + [c for c in df.columns if c not in prefer_order]
    df = df[cols]

    return df


def load_latest_pois() -> tuple[pd.DataFrame, Path]:
    """data/raw/YYYYMMDD/pois.json 중 가장 최신 파일을 읽어온다."""
    candidates = sorted(RAW_DIR.glob("*/pois.json"))
    if not candidates:
        raise FileNotFoundError("data/raw/YYYYMMDD/pois.json 이 없습니다.")
    pois_path = candidates[-1]
    df = pd.read_json(pois_path)
    return df, pois_path


def main() -> Path:
    df, src = load_latest_pois()
    df_clean = clean(df)
    out = OUT_DIR / "clean_pois.parquet"
    df_clean.to_parquet(out, index=False)
    print(f"[OK] cleaned: {out}  (src: {src})")
    return out


if __name__ == "__main__":
    main()
