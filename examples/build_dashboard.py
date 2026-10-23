from __future__ import annotations

import argparse
import html
import json
import math
import warnings
import webbrowser
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import mapping


warnings.filterwarnings("ignore", category=RuntimeWarning)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "output"
DEFAULT_HTML = DEFAULT_OUTPUT_DIR / "dashboard.html"

LAND_USE_LABELS = {
    "LandUse.RESIDENTIAL": "Жилая",
    "LandUse.BUSINESS": "Деловая",
    "LandUse.RECREATION": "Рекреационная",
    "LandUse.INDUSTRIAL": "Промышленная",
    "LandUse.TRANSPORT": "Транспортная",
    "LandUse.SPECIAL": "Специальная",
    "LandUse.AGRICULTURE": "Сельскохозяйственная",
}

LAND_USE_COLORS = {
    "Жилая": "#4e79a7",
    "Деловая": "#f28e2b",
    "Рекреационная": "#59a14f",
    "Промышленная": "#9c755f",
    "Транспортная": "#bab0ac",
    "Специальная": "#e15759",
    "Сельскохозяйственная": "#76b7b2",
    "Не определено": "#d9d9d9",
}

SPACEMATRIX_LABELS = {
    "low-rise low-density non-residential": "Малоэтажная низкоплотная нежилая",
    "low-rise low-density residential": "Малоэтажная низкоплотная жилая",
    "low-rise low-density mixed-use": "Малоэтажная низкоплотная смешанная",
    "mid-rise low-density non-residential": "Среднеэтажная низкоплотная нежилая",
    "mid-rise low-density residential": "Среднеэтажная низкоплотная жилая",
    "mid-rise low-density mixed-use": "Среднеэтажная низкоплотная смешанная",
    "high-mid-rise mixed-use": "Повышенной этажности смешанная",
    "low-rise high-density non-residential": "Малоэтажная высокоплотная нежилая",
    "low-rise high-density residential": "Малоэтажная высокоплотная жилая",
    "mid-rise high-density residential": "Среднеэтажная высокоплотная жилая",
}

STRELKA_LABELS = {
    "low-rise non-residential": "Малоэтажная нежилая",
    "low-rise model": "Малоэтажная модель Strelka",
    "individual residential": "Индивидуальная жилая",
    "mid-rise": "Среднеэтажная",
    "mid-rise non-residential": "Среднеэтажная нежилая",
    "mid-rise block": "Среднеэтажный квартал",
    "mid-rise microdistrict": "Среднеэтажный микрорайон",
    "high-rise": "Высотная",
}

SERVICE_LABELS = {
    "school": "Школы",
    "kindergarten": "Детские сады",
    "hospital": "Больницы",
    "clinic": "Поликлиники",
    "pharmacy": "Аптеки",
}

SERVICE_UNITS = {
    "school": "мест",
    "kindergarten": "мест",
    "hospital": "коек",
    "clinic": "посещений",
    "pharmacy": "объектов",
}

CATEGORY_PALETTE = [
    "#4e79a7",
    "#f28e2b",
    "#59a14f",
    "#e15759",
    "#76b7b2",
    "#edc948",
    "#b07aa1",
    "#9c755f",
    "#bab0ac",
    "#ff9da7",
]

SEQ_RED = ["#ffffcc", "#ffeda0", "#feb24c", "#f03b20", "#bd0026"]
SEQ_BLUE = ["#f7fbff", "#c6dbef", "#6baed6", "#2171b5", "#08306b"]
SEQ_GREEN = ["#ffffe5", "#d9f0a3", "#78c679", "#238443", "#004529"]
SEQ_PURPLE = ["#fcfbfd", "#dadaeb", "#9e9ac8", "#6a51a3", "#3f007d"]

INTERPRETATION_LABELS = {
    "low-rise": "малоэтажная",
    "mid-rise": "среднеэтажная",
    "high-rise": "высотная",
    "high-mid-rise": "повышенной этажности",
    "low-density": "низкоплотная",
    "medium-density": "среднеплотная",
    "high-density": "высокоплотная",
    "non-residential": "нежилая",
    "residential": "жилая",
    "mixed-use": "смешанная",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Собрать dashboard.html из сохранённых результатов исследования."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--html", type=Path, default=None)
    parser.add_argument("--service", default="school")
    parser.add_argument(
        "--territory",
        default="Магнитогорский городской округ, Челябинская область",
    )
    parser.add_argument(
        "--title",
        default="Кварталы Магнитогорского городского округа: интерактивный дашборд",
    )
    parser.add_argument("--open", action="store_true", dest="open_browser")
    return parser.parse_args()


def read_csv_table(path: Path, required: bool = True) -> pd.DataFrame | None:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Не найден обязательный файл: {path}")
        return None
    return pd.read_csv(path, index_col=0)


def read_geodata(path: Path, required: bool = True) -> gpd.GeoDataFrame | None:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Не найден обязательный файл: {path}")
        return None
    return gpd.read_file(path)


def land_use_label(value: object) -> str:
    if value is None:
        return "Не определено"
    if isinstance(value, float) and math.isnan(value):
        return "Не определено"
    return LAND_USE_LABELS.get(str(value), str(value))


def translate_morphotype(value: object, mapping: dict[str, str]) -> str:
    if value is None:
        return "Нет данных"
    if isinstance(value, float) and math.isnan(value):
        return "Нет данных"
    text = str(value).strip()
    if not text:
        return "Нет данных"
    return mapping.get(text, text)


def translate_interpretation(value: object) -> str:
    if value is None:
        return "—"
    if isinstance(value, float) and math.isnan(value):
        return "—"
    text = str(value).strip()
    return INTERPRETATION_LABELS.get(text, text)


def json_safe(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def fmt_number(value: object, digits: int = 1) -> str:
    number = json_safe(value)
    if number is None:
        return "—"
    if digits == 0:
        return f"{float(number):,.0f}".replace(",", " ")
    return f"{float(number):,.{digits}f}".replace(",", " ").replace(".", ",")


def stats(values: object) -> dict[str, float | int] | None:
    series = pd.to_numeric(pd.Series(values), errors="coerce").astype("float64")
    series = series.replace([np.inf, -np.inf], np.nan).dropna()
    if series.empty:
        return None
    return {
        "n": int(series.size),
        "mean": float(series.mean()),
        "median": float(series.median()),
        "p25": float(series.quantile(0.25)),
        "p75": float(series.quantile(0.75)),
        "min": float(series.min()),
        "max": float(series.max()),
    }


def quantile_classes(
    values: object,
    colors: list[str],
    digits: int,
    unit: str = "",
    n_classes: int = 5,
) -> dict[str, object]:
    series = pd.to_numeric(pd.Series(values), errors="coerce")
    series = series.replace([np.inf, -np.inf], np.nan).dropna()
    if series.empty:
        return {"breaks": [], "labels": [], "colors": []}
    quantiles = np.linspace(0, 1, n_classes + 1)
    raw_breaks = np.quantile(series.to_numpy(), quantiles)
    breaks: list[float] = []
    for raw in raw_breaks:
        value = float(raw)
        if not breaks or abs(value - breaks[-1]) > 1e-9:
            breaks.append(value)
    if len(breaks) < 2:
        breaks = [float(series.min()), float(series.max()) + 1e-9]
    breaks[-1] += 1e-9
    labels = [
        f"{fmt_number(left, digits)}–{fmt_number(right, digits)}"
        for left, right in zip(breaks[:-1], breaks[1:])
    ]
    if unit:
        labels = [f"{label} {unit}" for label in labels]
    return {
        "breaks": [round(value, 9) for value in breaks],
        "labels": labels,
        "colors": colors[: len(breaks) - 1],
    }


def custom_classes(
    breaks: list[float],
    labels: list[str],
    colors: list[str],
    unit: str = "",
) -> dict[str, object]:
    if unit:
        labels = [f"{label} {unit}" for label in labels]
    return {"breaks": breaks, "labels": labels, "colors": colors}


def category_color_map(
    values: object, preferred: dict[str, str] | None = None
) -> dict[str, str]:
    colors = dict(preferred or {})
    unique = sorted({str(value) for value in pd.Series(values).dropna().unique()})
    palette_index = 0
    for value in unique:
        if value in colors or value == "Нет данных":
            continue
        colors[value] = CATEGORY_PALETTE[palette_index % len(CATEGORY_PALETTE)]
        palette_index += 1
    colors.setdefault("Нет данных", "#d9d9d9")
    return colors


def file_meta(path: Path, purpose: str) -> dict[str, object]:
    stat = path.stat()
    return {
        "name": path.name,
        "purpose": purpose,
        "size": f"{stat.st_size / 1024 / 1024:.1f} МБ",
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M"),
    }


def make_geojson(gdf: gpd.GeoDataFrame, properties: pd.DataFrame) -> dict[str, object]:
    features = []
    for block_id, geometry in zip(gdf.index, gdf.geometry):
        if geometry is None or geometry.is_empty:
            continue
        values = {
            key: json_safe(properties.at[block_id, key])
            for key in properties.columns
        }
        values["block_id"] = int(block_id)
        features.append(
            {
                "type": "Feature",
                "id": int(block_id),
                "geometry": mapping(geometry),
                "properties": values,
            }
        )
    return {"type": "FeatureCollection", "features": features}


def kpi_card(label: str, value: str, unit: str, note: str = "") -> str:
    note_html = f'<div class="kpi-note">{html.escape(note)}</div>' if note else ""
    return (
        '<div class="kpi">'
        f'<div class="kpi-label">{html.escape(label)}</div>'
        f'<div class="kpi-value">{value}<span>{html.escape(unit)}</span></div>'
        f"{note_html}"
        "</div>"
    )


def kpi_chip(label: str, value: str, unit: str) -> str:
    return (
        '<div class="kpi-chip">'
        f'<span>{html.escape(label)}</span>'
        f'<strong>{value}</strong>'
        f'<em>{html.escape(unit)}</em>'
        "</div>"
    )


def build_summary_table(rows: list[list[str]]) -> str:
    header = (
        "<thead><tr>"
        "<th>Показатель</th><th>Ед.</th><th>Выборка</th><th>N</th>"
        "<th>Среднее</th><th>Медиана</th><th>P25</th><th>P75</th>"
        "<th>Мин.</th><th>Макс.</th><th>Источник</th>"
        "</tr></thead>"
    )
    body = "<tbody>" + "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    ) + "</tbody>"
    return f'<table class="data-table">{header}{body}</table>'


def build_cluster_table(rows: list[list[str]]) -> str:
    header = (
        "<thead><tr>"
        "<th>Кластер</th><th>Кварталов</th><th>L, этажей</th>"
        "<th>FSI</th><th>MXI</th><th>Этажность</th><th>Плотность</th>"
        "<th>Использование</th><th>Морфотип</th>"
        "</tr></thead>"
    )
    body = "<tbody>" + "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    ) + "</tbody>"
    return f'<table class="data-table">{header}{body}</table>'


def build_sources_table(rows: list[dict[str, object]]) -> str:
    header = (
        "<thead><tr><th>Файл</th><th>Назначение</th><th>Размер</th><th>Изменён</th></tr></thead>"
    )
    body = "<tbody>" + "".join(
        "<tr>"
        f"<td><code>{html.escape(str(row['name']))}</code></td>"
        f"<td>{html.escape(str(row['purpose']))}</td>"
        f"<td>{html.escape(str(row['size']))}</td>"
        f"<td>{html.escape(str(row['modified']))}</td>"
        "</tr>"
        for row in rows
    ) + "</tbody>"
    return f'<table class="data-table">{header}{body}</table>'


def build_provenance_table(provenance: dict[str, object]) -> str:
    if not provenance:
        return '<p class="caption">Паспорт источников не найден.</p>'

    population = provenance.get("population") or {}
    buildings = provenance.get("buildings") or {}
    residential_rule = provenance.get("residential_rule") or {}
    landuse = provenance.get("landuse") or {}
    boundary = provenance.get("boundary") or {}
    services = provenance.get("services") or {}
    official_inputs = provenance.get("official_inputs") or {}

    mode = population.get("mode")
    mode_label = {
        "proportional_calibration": "пропорциональная калибровка",
        "official_by_block": "официальные данные по кварталам",
    }.get(str(mode), str(mode or "—"))
    factor = population.get("factor")
    factor_label = fmt_number(factor, 3) if factor is not None else "—"

    rows: list[tuple[str, str, str]] = [
        ("Территория", str(provenance.get("territory", "—")), "—"),
        (
            "Граница",
            str(boundary.get("source", "—")),
            f"{fmt_number(boundary.get('area_km2'), 1)} км²",
        ),
        (
            "Население: модельная оценка",
            f"{fmt_number(population.get('model_total'), 0)} чел.",
            mode_label,
        ),
        (
            "Население: официальный контроль",
            f"{fmt_number(population.get('official_total'), 0)} чел.",
            f"на {population.get('official_date', '—')}",
        ),
        ("Коэффициент калибровки", factor_label, "модель → официальный итог"),
        (
            "Здания",
            f"OSM {fmt_number(buildings.get('osm'), 0)}; "
            f"Microsoft {fmt_number(buildings.get('microsoft'), 0)}; "
            f"официальные {fmt_number(buildings.get('official'), 0)}",
            f"после дедупликации {fmt_number(buildings.get('combined'), 0)}",
        ),
        (
            "Жилая классификация",
            "building=yes в жилой зоне, этажность ≥ 2",
            f"переклассифицировано {fmt_number(residential_rule.get('generic_building_yes_reclassified'), 0)} зданий",
        ),
        (
            "Землепользование",
            f"OSM {fmt_number(landuse.get('osm'), 0)} зон; "
            f"официальные {fmt_number(landuse.get('official'), 0)} зон",
            f"заполнено у {fmt_number(landuse.get('blocks_with_land_use'), 0)} "
            f"из {fmt_number(landuse.get('blocks_total'), 0)} кварталов",
        ),
        (
            "Сервисы",
            str(services.get("source", "—")),
            str(services.get("type", "—")),
        ),
        (
            "Официальные файлы",
            str(len(official_inputs)) + " шт.",
            ", ".join(sorted(official_inputs)) if official_inputs else "не найдены",
        ),
    ]
    for source in provenance.get("sources") or []:
        rows.append(
            (
                str(source.get("name", "—")),
                str(source.get("role", "—")),
                str(source.get("status", "—")),
            )
        )

    header = (
        "<thead><tr><th>Источник или блок</th><th>Что даёт</th>"
        "<th>Статус</th></tr></thead>"
    )
    body = "<tbody>" + "".join(
        "<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    ) + "</tbody>"
    return f'<table class="data-table">{header}{body}</table>'


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    html_path = (args.html or (output_dir / "dashboard.html")).resolve()
    service = args.service.strip()
    if not service:
        raise ValueError("Параметр --service не должен быть пустым")

    service_label = SERVICE_LABELS.get(service, service)
    service_unit = SERVICE_UNITS.get(service, "ед.")

    blocks_path = output_dir / "blocks.geojson"
    buildings_path = output_dir / "buildings_blocks.geojson"
    services_path = output_dir / f"services_blocks_{service}.geojson"
    density_path = output_dir / "density_df.csv"
    prov_path = output_dir / f"prov_df_{service}.csv"
    links_path = output_dir / f"links_df_{service}.csv"
    spacematrix_path = output_dir / "spacematrix_df.csv"
    spacematrix_clusters_path = output_dir / "spacematrix_clusters.csv"
    strelka_path = output_dir / "strelka_df.csv"
    accessibility_path = output_dir / "area_accessibility.csv"
    matrix_path = output_dir / "accessibility_matrix_drive.parquet"
    provenance_path = output_dir / "data_provenance.json"

    blocks = read_geodata(blocks_path)
    buildings = read_geodata(buildings_path)
    services = read_geodata(services_path)
    density = read_csv_table(density_path)
    provision = read_csv_table(prov_path)
    links = read_csv_table(links_path, required=False)
    spacematrix = read_csv_table(spacematrix_path)
    spacematrix_clusters = pd.read_csv(spacematrix_clusters_path)
    strelka = read_csv_table(strelka_path)
    accessibility = read_csv_table(accessibility_path)
    matrix = pd.read_parquet(matrix_path) if matrix_path.exists() else None
    provenance = (
        json.loads(provenance_path.read_text(encoding="utf-8"))
        if provenance_path.exists()
        else {}
    )

    if blocks.crs is None:
        raise ValueError("У слоя кварталов не задана система координат")
    if not blocks.index.is_unique:
        raise ValueError("Индекс кварталов должен быть уникальным")

    for table_name, table in [
        ("buildings_blocks.geojson", buildings),
        ("density_df.csv", density),
        ("prov_df", provision),
        ("spacematrix_df.csv", spacematrix),
        ("strelka_df.csv", strelka),
        ("area_accessibility.csv", accessibility),
    ]:
        missing = set(blocks.index) - set(table.index)
        if missing:
            raise ValueError(
                f"{table_name}: нет данных для {len(missing)} кварталов. "
                "Проверьте, что файлы относятся к одному запуску ноутбука."
            )

    merged = pd.DataFrame(index=blocks.index)
    merged["land_use_label"] = blocks["land_use"].apply(land_use_label)
    merged = merged.join(
        buildings[
            [
                "population",
                "count",
                "footprint_area",
                "build_floor_area",
                "living_area",
                "non_living_area",
            ]
        ].rename(columns={"count": "count_buildings"}),
        how="left",
    )
    merged = merged.join(
        services[["capacity", "count"]].rename(columns={"count": "count_services"}),
        how="left",
    )
    merged = merged.join(
        density[
            [
                "site_area",
                "fsi",
                "gsi",
                "mxi",
                "l",
                "osr",
                "share_living",
                "share_non_living",
            ]
        ],
        how="left",
    )
    merged = merged.join(
        provision[
            [
                "demand",
                "demand_left",
                "demand_within",
                "demand_without",
                "capacity_left",
                "capacity_within",
                "capacity_without",
                "provision_strong",
                "provision_weak",
            ]
        ],
        how="left",
    )
    merged = merged.join(
        spacematrix[["cluster", "morphotype"]].rename(
            columns={"morphotype": "morphotype_spacematrix"}
        ),
        how="left",
    )
    merged = merged.join(
        strelka[["morphotype"]].rename(columns={"morphotype": "morphotype_strelka"}),
        how="left",
    )
    merged = merged.join(accessibility[["area_accessibility"]], how="left")
    merged["block_id"] = merged.index.astype(int)
    merged["site_area_ha"] = merged["site_area"] / 10000.0
    merged["morphotype_spacematrix"] = merged["morphotype_spacematrix"].apply(
        lambda value: translate_morphotype(value, SPACEMATRIX_LABELS)
    )
    merged["morphotype_strelka"] = merged["morphotype_strelka"].apply(
        lambda value: translate_morphotype(value, STRELKA_LABELS)
    )

    built_mask = pd.to_numeric(merged["build_floor_area"], errors="coerce").fillna(0) > 0
    provision_mask = merged["provision_strong"].notna()
    built = merged.loc[built_mask].copy()
    population = pd.to_numeric(merged["population"], errors="coerce").fillna(0)
    capacity = pd.to_numeric(merged["capacity"], errors="coerce").fillna(0)
    demand = pd.to_numeric(merged["demand"], errors="coerce").fillna(0)
    provision_values = pd.to_numeric(
        merged["provision_strong"], errors="coerce"
    ).dropna()
    site_area_total = float(pd.to_numeric(merged["site_area"], errors="coerce").sum())
    total_area_km2 = site_area_total / 1_000_000.0
    population_total = float(population.sum())
    capacity_total = float(capacity.sum())
    demand_total = float(demand.sum())
    deficit_total = demand_total - capacity_total
    populated_blocks = int((population > 0).sum())
    provided_blocks = int((provision_values >= 0.999).sum())
    unprovided_blocks = int((provision_values <= 0.001).sum())
    partial_blocks = int(len(provision_values) - provided_blocks - unprovided_blocks)
    links_count = int(len(links)) if links is not None else 0
    links_value = float(pd.to_numeric(links["value"], errors="coerce").sum()) if links is not None else 0.0

    if matrix is not None:
        matrix_values = matrix.to_numpy(dtype=np.float64)
        matrix_values = matrix_values[np.isfinite(matrix_values) & (matrix_values > 0)]
        travel_stats = stats(matrix_values)
        travel_sample = "пары кварталов"
    else:
        matrix_values = np.array([])
        travel_stats = None
        travel_sample = "нет файла"

    travel_hist_bins = np.array([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 75, 90, 120], dtype=float)
    if matrix_values.size:
        travel_counts, _ = np.histogram(matrix_values, bins=travel_hist_bins)
        travel_labels = [
            "0–5",
            "5–10",
            "10–15",
            "15–20",
            "20–25",
            "25–30",
            "30–35",
            "35–40",
            "40–45",
            "45–50",
            "50–55",
            "55–60",
            "60–75",
            "75–90",
            "90+",
        ]
    else:
        travel_counts = np.array([])
        travel_labels = []

    land_use_area = (
        merged.groupby("land_use_label")["site_area"].sum().sort_values(ascending=False) / 10000.0
    )
    land_use_population = (
        merged.groupby("land_use_label")["population"].sum().reindex(land_use_area.index).fillna(0)
    )
    land_use_colors = [LAND_USE_COLORS.get(label, "#9e9e9e") for label in land_use_area.index]

    fsi_bins = np.array([0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0])
    fsi_values = pd.to_numeric(built["fsi"], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    fsi_counts, _ = np.histogram(fsi_values.to_numpy(), bins=fsi_bins)
    fsi_labels = [
        "0–0,05",
        "0,05–0,10",
        "0,10–0,15",
        "0,15–0,20",
        "0,20–0,30",
        "0,30–0,40",
        "0,40–0,50",
        "0,50–0,75",
        "0,75–1,00",
        "1,00–1,50",
        "1,50–2,00",
        "2,00–3,00",
        "3,00+",
    ]

    accessibility_bins = np.array([15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80], dtype=float)
    accessibility_values = pd.to_numeric(
        merged["area_accessibility"], errors="coerce"
    ).replace([np.inf, -np.inf], np.nan).dropna()
    accessibility_counts, _ = np.histogram(
        accessibility_values.to_numpy(), bins=accessibility_bins
    )
    accessibility_labels = [
        "15–20",
        "20–25",
        "25–30",
        "30–35",
        "35–40",
        "40–45",
        "45–50",
        "50–60",
        "60–70",
        "70+",
    ]

    provision_categories = [
        ("1,00 — полностью", int((provision_values >= 0.999).sum()), "#1a9850"),
        (
            "0,50–1,00 — частично",
            int(((provision_values > 0.001) & (provision_values < 0.999)).sum()),
            "#fee08b",
        ),
        ("0,00 — не обеспечены", int((provision_values <= 0.001).sum()), "#d73027"),
        ("Нет данных", int(merged["provision_strong"].isna().sum()), "#d9d9d9"),
    ]

    spacematrix_counts = (
        merged.loc[built_mask, "morphotype_spacematrix"]
        .replace("Нет данных", np.nan)
        .dropna()
        .value_counts()
    )
    strelka_counts = (
        merged.loc[built_mask, "morphotype_strelka"]
        .replace("Нет данных", np.nan)
        .dropna()
        .value_counts()
    )
    spacematrix_colors = category_color_map(spacematrix_counts.index)
    strelka_colors = category_color_map(strelka_counts.index)
    morphotype_spacematrix_colors = category_color_map(merged["morphotype_spacematrix"])
    morphotype_strelka_colors = category_color_map(merged["morphotype_strelka"])

    map_metrics = [
        {
            "key": "land_use_label",
            "label": "Землепользование",
            "shortLabel": "Землепользование",
            "kind": "category",
            "unit": "",
            "help": "Тип функционального использования квартала по данным BlocksNet и OpenStreetMap.",
            "colors": LAND_USE_COLORS,
        },
        {
            "key": "population",
            "label": "Население",
            "shortLabel": "Население",
            "kind": "numeric",
            "unit": "чел.",
            "help": (
                "Оценка населения квартала по зданиям и этажности. OSM-здания "
                "с тегом building=yes в жилой зоне и этажностью 2+ считаются жилыми."
            ),
            "classes": custom_classes(
                [0, 1, 51, 151, 301, float(max(302, np.nanmax(population.to_numpy()) + 1))],
                ["0", "1–50", "51–150", "151–300", "301+"],
                ["#e5e7eb", "#c6dbef", "#6baed6", "#2171b5", "#08306b"],
            ),
        },
        {
            "key": "capacity",
            "label": f"Ёмкость «{service_label}»",
            "shortLabel": "Ёмкость",
            "kind": "numeric",
            "unit": service_unit,
            "help": "Суммарная оценённая ёмкость объектов выбранного сервиса в квартале.",
            "classes": custom_classes(
                [0, 1, 101, 301, 601, float(max(602, np.nanmax(capacity.to_numpy()) + 1))],
                ["0", "1–100", "101–300", "301–600", "601+"],
                SEQ_GREEN,
            ),
        },
        {
            "key": "demand",
            "label": f"Спрос на «{service_label}»",
            "shortLabel": "Спрос",
            "kind": "numeric",
            "unit": service_unit,
            "help": "Оценённый спрос на сервис с учётом населения квартала и норматива BlocksNet.",
            "classes": custom_classes(
                [0, 1, 51, 151, 301, float(max(302, np.nanmax(demand.to_numpy()) + 1))],
                ["0", "1–50", "51–150", "151–300", "301+"],
                SEQ_RED,
            ),
        },
        {
            "key": "provision_strong",
            "label": f"Обеспеченность «{service_label}»",
            "shortLabel": "Обеспеченность",
            "kind": "numeric",
            "unit": "доля",
            "help": "Конкурентная обеспеченность: 1 — спрос покрыт, 0 — не покрыт. Рассчитана с порогом доступности BlocksNet.",
            "classes": custom_classes(
                [-1e-9, 1e-6, 0.5, 0.999999, 1.000001],
                ["0,00 — не обеспечен", "0,00–0,50", "0,50–1,00", "1,00 — обеспечен"],
                ["#d73027", "#fc8d59", "#fee08b", "#1a9850"],
            ),
        },
        {
            "key": "fsi",
            "label": "FSI — коэффициент использования территории",
            "shortLabel": "FSI",
            "kind": "numeric",
            "unit": "",
            "help": "FSI = общая площадь застройки / площадь квартала.",
            "classes": custom_classes(
                [0, 0.05, 0.10, 0.20, 0.50, float(max(0.51, np.nanmax(pd.to_numeric(merged["fsi"], errors="coerce").to_numpy()) + 0.001))],
                ["0–0,05", "0,05–0,10", "0,10–0,20", "0,20–0,50", "0,50+"],
                SEQ_PURPLE,
            ),
        },
        {
            "key": "gsi",
            "label": "GSI — коэффициент застройки",
            "shortLabel": "GSI",
            "kind": "numeric",
            "unit": "",
            "help": "GSI = площадь застройки / площадь квартала, ограничен диапазоном 0–1.",
            "classes": custom_classes(
                [0, 0.05, 0.10, 0.20, 0.40, 1.0001],
                ["0–0,05", "0,05–0,10", "0,10–0,20", "0,20–0,40", "0,40–1,00"],
                SEQ_RED,
            ),
        },
        {
            "key": "mxi",
            "label": "MXI — доля жилой площади",
            "shortLabel": "MXI",
            "kind": "numeric",
            "unit": "",
            "help": "MXI = жилая площадь / общая площадь застройки, ограничен диапазоном 0–1.",
            "classes": custom_classes(
                [0, 0.20, 0.50, 0.80, 1.0001],
                ["0–0,20", "0,20–0,50", "0,50–0,80", "0,80–1,00"],
                SEQ_GREEN,
            ),
        },
        {
            "key": "l",
            "label": "Средняя этажность L",
            "shortLabel": "Этажность L",
            "kind": "numeric",
            "unit": "этажей",
            "help": "L = общая площадь застройки / площадь застройки; приблизительная средняя этажность.",
            "classes": custom_classes(
                [0, 1.5, 2.5, 4.5, 7.5, float(max(8.5, np.nanmax(pd.to_numeric(merged["l"], errors="coerce").to_numpy()) + 0.1))],
                ["1", "2", "3–4", "5–7", "8+"],
                SEQ_PURPLE,
            ),
        },
        {
            "key": "area_accessibility",
            "label": "Доступность территории",
            "shortLabel": "Доступность",
            "kind": "numeric",
            "unit": "мин",
            "help": "Средневзвешенное по площади время в пути от квартала до остальных кварталов. Чем меньше, тем лучше.",
            "classes": quantile_classes(
                merged["area_accessibility"], SEQ_BLUE, digits=1, unit="мин", n_classes=5
            ),
        },
        {
            "key": "morphotype_spacematrix",
            "label": "Морфотип Spacematrix",
            "shortLabel": "Spacematrix",
            "kind": "category",
            "unit": "",
            "help": "Классификация застройки по этажности, плотности и использованию (Spacematrix).",
            "colors": morphotype_spacematrix_colors,
        },
        {
            "key": "morphotype_strelka",
            "label": "Морфотип Strelka",
            "shortLabel": "Strelka",
            "kind": "category",
            "unit": "",
            "help": "Альтернативная классификация морфотипов застройки Strelka.",
            "colors": morphotype_strelka_colors,
        },
    ]

    table_columns = [
        {"key": "block_id", "label": "№ квартала", "type": "number", "digits": 0},
        {"key": "land_use_label", "label": "Землепользование", "type": "text"},
        {"key": "site_area_ha", "label": "Площадь квартала, га", "type": "number", "digits": 2},
        {"key": "population", "label": "Население, чел.", "type": "number", "digits": 0},
        {"key": "count_buildings", "label": "Зданий, шт.", "type": "number", "digits": 0},
        {"key": "footprint_area", "label": "Площадь застройки, м²", "type": "number", "digits": 0},
        {"key": "build_floor_area", "label": "Общая площадь застройки, м²", "type": "number", "digits": 0},
        {"key": "living_area", "label": "Жилая площадь, м²", "type": "number", "digits": 0},
        {"key": "non_living_area", "label": "Нежилая площадь, м²", "type": "number", "digits": 0},
        {"key": "fsi", "label": "FSI", "type": "number", "digits": 3},
        {"key": "gsi", "label": "GSI", "type": "number", "digits": 3},
        {"key": "mxi", "label": "MXI", "type": "number", "digits": 3},
        {"key": "l", "label": "L, этажей", "type": "number", "digits": 2},
        {"key": "osr", "label": "OSR", "type": "number", "digits": 2},
        {"key": "share_living", "label": "Жилая площадь / площадь застройки", "type": "number", "digits": 3},
        {"key": "share_non_living", "label": "Нежилая площадь / площадь застройки", "type": "number", "digits": 3},
        {"key": "count_services", "label": f"Объектов «{service_label}», шт.", "type": "number", "digits": 0},
        {"key": "capacity", "label": f"Ёмкость «{service_label}», {service_unit}", "type": "number", "digits": 0},
        {"key": "demand", "label": f"Спрос «{service_label}», {service_unit}", "type": "number", "digits": 0},
        {"key": "demand_left", "label": f"Неудовлетворённый спрос, {service_unit}", "type": "number", "digits": 0},
        {"key": "demand_within", "label": f"Спрос в зоне доступности, {service_unit}", "type": "number", "digits": 0},
        {"key": "demand_without", "label": f"Спрос вне зоны доступности, {service_unit}", "type": "number", "digits": 0},
        {"key": "capacity_left", "label": f"Неиспользованная ёмкость, {service_unit}", "type": "number", "digits": 0},
        {"key": "capacity_within", "label": f"Ёмкость в зоне доступности, {service_unit}", "type": "number", "digits": 0},
        {"key": "capacity_without", "label": f"Ёмкость вне зоны доступности, {service_unit}", "type": "number", "digits": 0},
        {"key": "provision_strong", "label": "Обеспеченность (strong), доля", "type": "number", "digits": 2},
        {"key": "provision_weak", "label": "Обеспеченность (weak), доля", "type": "number", "digits": 2},
        {"key": "cluster", "label": "Кластер Spacematrix", "type": "number", "digits": 0},
        {"key": "morphotype_spacematrix", "label": "Морфотип Spacematrix", "type": "text"},
        {"key": "morphotype_strelka", "label": "Морфотип Strelka", "type": "text"},
        {"key": "area_accessibility", "label": "Доступность, мин", "type": "number", "digits": 1},
    ]

    table_rows: list[list[object]] = []
    for _, row in merged.iterrows():
        values: list[object] = []
        for column in table_columns:
            value = row[column["key"]]
            if column["type"] == "number":
                values.append(json_safe(value))
            else:
                values.append(str(value) if value is not None else "—")
        table_rows.append(values)

    summary_specs = [
        ("site_area", "Площадь квартала", "м²", "все кварталы", None, "density_df.csv", 0),
        ("footprint_area", "Площадь застройки", "м²", "все кварталы", None, "buildings_blocks.geojson", 0),
        ("build_floor_area", "Общая площадь застройки", "м²", "все кварталы", None, "buildings_blocks.geojson", 0),
        ("living_area", "Жилая площадь", "м²", "все кварталы", None, "buildings_blocks.geojson", 0),
        ("non_living_area", "Нежилая площадь", "м²", "все кварталы", None, "buildings_blocks.geojson", 0),
        ("population", "Население", "чел.", "все кварталы", None, "buildings_blocks.geojson", 0),
        ("count_buildings", "Количество зданий", "шт.", "все кварталы", None, "buildings_blocks.geojson", 0),
        ("count_services", f"Объектов «{service_label}»", "шт.", "все кварталы", None, f"services_blocks_{service}.geojson", 0),
        ("capacity", f"Ёмкость «{service_label}»", service_unit, "все кварталы", None, f"services_blocks_{service}.geojson", 0),
        ("demand", f"Спрос на «{service_label}»", service_unit, "со спросом", provision_mask, f"prov_df_{service}.csv", 0),
        ("demand_left", "Неудовлетворённый спрос", service_unit, "со спросом", provision_mask, f"prov_df_{service}.csv", 0),
        ("demand_within", "Спрос в зоне доступности", service_unit, "со спросом", provision_mask, f"prov_df_{service}.csv", 0),
        ("demand_without", "Спрос вне зоны доступности", service_unit, "со спросом", provision_mask, f"prov_df_{service}.csv", 0),
        ("capacity_left", "Неиспользованная ёмкость", service_unit, "со спросом", provision_mask, f"prov_df_{service}.csv", 0),
        ("capacity_within", "Ёмкость в зоне доступности", service_unit, "со спросом", provision_mask, f"prov_df_{service}.csv", 0),
        ("capacity_without", "Ёмкость вне зоны доступности", service_unit, "со спросом", provision_mask, f"prov_df_{service}.csv", 0),
        ("provision_strong", "Обеспеченность (strong)", "доля 0–1", "со спросом", provision_mask, f"prov_df_{service}.csv", 2),
        ("provision_weak", "Обеспеченность (weak)", "доля 0–1", "со спросом", provision_mask, f"prov_df_{service}.csv", 2),
        ("fsi", "FSI", "безразм.", "застроенные", built_mask, "density_df.csv", 3),
        ("gsi", "GSI", "безразм.", "застроенные", built_mask, "density_df.csv", 3),
        ("mxi", "MXI", "безразм.", "застроенные", built_mask, "density_df.csv", 3),
        ("l", "Средняя этажность L", "этажей", "застроенные", built_mask, "density_df.csv", 2),
        ("osr", "OSR", "м²/м²", "застроенные", built_mask, "density_df.csv", 2),
        ("share_living", "Жилая площадь / площадь застройки", "безразм.", "застроенные", built_mask, "density_df.csv", 3),
        ("share_non_living", "Нежилая площадь / площадь застройки", "безразм.", "застроенные", built_mask, "density_df.csv", 3),
        ("area_accessibility", "Доступность территории", "мин", "все кварталы", None, "area_accessibility.csv", 1),
    ]

    summary_rows: list[list[str]] = []
    for key, label, unit, sample, mask, source, digits in summary_specs:
        values = merged[key] if mask is None else merged.loc[mask, key]
        summary = stats(values)
        if summary is None:
            summary_rows.append([label, unit, sample, "0", "—", "—", "—", "—", "—", "—", source])
            continue
        summary_rows.append(
            [
                label,
                unit,
                sample,
                str(summary["n"]),
                fmt_number(summary["mean"], digits),
                fmt_number(summary["median"], digits),
                fmt_number(summary["p25"], digits),
                fmt_number(summary["p75"], digits),
                fmt_number(summary["min"], digits),
                fmt_number(summary["max"], digits),
                source,
            ]
        )
    if travel_stats is not None:
        summary_rows.append(
            [
                "Время в пути между кварталами",
                "мин",
                travel_sample,
                str(travel_stats["n"]),
                fmt_number(travel_stats["mean"], 1),
                fmt_number(travel_stats["median"], 1),
                fmt_number(travel_stats["p25"], 1),
                fmt_number(travel_stats["p75"], 1),
                fmt_number(travel_stats["min"], 1),
                fmt_number(travel_stats["max"], 1),
                "accessibility_matrix_drive.parquet",
            ]
        )

    cluster_rows: list[list[str]] = []
    cluster_counts = merged["cluster"].value_counts()
    for _, row in spacematrix_clusters.iterrows():
        cluster_id = int(row["cluster"])
        cluster_rows.append(
            [
                str(cluster_id),
                str(int(cluster_counts.get(cluster_id, 0))),
                fmt_number(row.get("l"), 2),
                fmt_number(row.get("fsi"), 3),
                fmt_number(row.get("mxi"), 3),
                html.escape(translate_interpretation(row.get("l_interpretation"))),
                html.escape(translate_interpretation(row.get("fsi_interpretation"))),
                html.escape(translate_interpretation(row.get("mxi_interpretation"))),
                html.escape(translate_morphotype(row.get("morphotype"), SPACEMATRIX_LABELS)),
            ]
        )

    source_specs = [
        (blocks_path, "Кварталы с землепользованием"),
        (buildings_path, "Здания, население и площади по кварталам"),
        (services_path, f"Ёмкость сервиса «{service_label}» по кварталам"),
        (density_path, "Плотностные показатели (FSI, GSI, MXI, L, OSR)"),
        (prov_path, f"Обеспеченность сервисом «{service_label}»"),
        (spacematrix_path, "Морфотипы Spacematrix по кварталам"),
        (spacematrix_clusters_path, "Справочник кластеров Spacematrix"),
        (strelka_path, "Морфотипы Strelka по кварталам"),
        (accessibility_path, "Доступность территории"),
        (provenance_path, "Паспорт источников и калибровка населения"),
    ]
    if links is not None:
        source_specs.insert(5, (links_path, f"Связи «{service_label} — квартал»"))
    if matrix_path.exists():
        source_specs.append((matrix_path, "Матрица времени в пути (автомобиль, минуты)"))
    source_rows = [file_meta(path, purpose) for path, purpose in source_specs if path.exists()]
    last_modified = max(
        (datetime.fromtimestamp(path.stat().st_mtime) for path, _ in source_specs if path.exists()),
        default=datetime.now(),
    )

    top_land_use = land_use_area.head(4)
    top_land_use_text = "; ".join(
        f"{label} — {fmt_number(value, 0)} га ({fmt_number(value / land_use_area.sum() * 100, 1)}%)"
        for label, value in top_land_use.items()
    )
    top_spacematrix = spacematrix_counts.head(3)
    top_spacematrix_text = "; ".join(
        f"{label} — {count}" for label, count in top_spacematrix.items()
    )
    top_strelka = strelka_counts.head(3)
    top_strelka_text = "; ".join(
        f"{label} — {count}" for label, count in top_strelka.items()
    )
    no_land_use = int((merged["land_use_label"] == "Не определено").sum())
    no_morphotype = int((merged["morphotype_spacematrix"] == "Нет данных").sum())
    median_fsi_built = stats(built["fsi"])
    median_gsi_built = stats(built["gsi"])
    median_l_built = stats(built["l"])
    median_mxi_built = stats(built["mxi"])
    accessibility_stats = stats(merged["area_accessibility"])
    population_density = population_total / total_area_km2 if total_area_km2 else 0
    provision_share = provided_blocks / len(provision_values) * 100 if len(provision_values) else 0

    population_control = provenance.get("population") or {}
    residential_rule = provenance.get("residential_rule") or {}
    reclassified_buildings = residential_rule.get("generic_building_yes_reclassified")
    official_population = population_control.get("official_total")
    population_note = "оценка BlocksNet"
    if official_population:
        population_note = f"калибровка по официальным {fmt_number(official_population, 0)} чел."
    population_factor = population_control.get("factor")
    calibration_text = (
        f" Модельная оценка {fmt_number(population_control.get('model_total'), 0)} чел. "
        f"приведена к официальному итогу {fmt_number(official_population, 0)} чел."
        if official_population
        else ""
    )
    if population_factor:
        calibration_text += f" Коэффициент калибровки — {fmt_number(population_factor, 3)}."

    kpis = [
        kpi_card("Кварталов", fmt_number(len(merged), 0), "шт.", "после нарезки территории"),
        kpi_card("Площадь кварталов", fmt_number(total_area_km2, 1), "км²", "сумма площадей кварталов"),
        kpi_card("Население", fmt_number(population_total, 0), "чел.", population_note),
        kpi_card("Застроенных кварталов", fmt_number(int(built_mask.sum()), 0), "из " + fmt_number(len(merged), 0), "есть здания и площади"),
        kpi_card(f"Ёмкость «{service_label}»", fmt_number(capacity_total, 0), service_unit, "сумма по кварталам"),
        kpi_card(f"Спрос на «{service_label}»", fmt_number(demand_total, 0), service_unit, f"{fmt_number(populated_blocks, 0)} кварталов с населением"),
        kpi_card("Баланс спроса и ёмкости", fmt_number(abs(deficit_total), 0), service_unit, "дефицит" if deficit_total > 0 else "профицит"),
        kpi_card("Полностью обеспечены", fmt_number(provided_blocks, 0), "из " + fmt_number(len(provision_values), 0), fmt_number(provision_share, 1) + "% кварталов со спросом"),
        kpi_card("Медианное время в пути", fmt_number(travel_stats["median"] if travel_stats else None, 1), "мин", "автомобиль, пары кварталов"),
        kpi_card("Медианная доступность", fmt_number(accessibility_stats["median"] if accessibility_stats else None, 1), "мин", "взвешено по площади кварталов"),
        kpi_card("Медианный FSI", fmt_number(median_fsi_built["median"] if median_fsi_built else None, 3), "безразм.", "застроенные кварталы"),
        kpi_card("Плотность населения", fmt_number(population_density, 0), "чел./км²", "по площади кварталов"),
    ]

    top_kpis = [
        kpi_chip("Кварталов", fmt_number(len(merged), 0), "шт."),
        kpi_chip("Население", fmt_number(population_total, 0), "чел."),
        kpi_chip("Площадь", fmt_number(total_area_km2, 1), "км²"),
        kpi_chip(f"Ёмкость «{service_label}»", fmt_number(capacity_total, 0), service_unit),
        kpi_chip("Баланс", fmt_number(abs(deficit_total), 0), "дефицит" if deficit_total > 0 else "профицит"),
        kpi_chip(
            "Обеспечены",
            fmt_number(provided_blocks, 0) + " / " + fmt_number(len(provision_values), 0),
            "кварталов",
        ),
        kpi_chip(
            "Медианное время",
            fmt_number(travel_stats["median"] if travel_stats else None, 1),
            "мин",
        ),
    ]

    conclusions = [
        (
            f"В выборке {fmt_number(len(merged), 0)} кварталов общей площадью {fmt_number(total_area_km2, 1)} км². "
            f"Здания есть в {fmt_number(int(built_mask.sum()), 0)} из {fmt_number(len(merged), 0)} кварталов, население и спрос на сервис — в "
            f"{fmt_number(populated_blocks, 0)}. У {fmt_number(no_morphotype, 0)} кварталов морфотип не определён, "
            "потому что в них нет застройки."
        ),
        (
            f"Оценка населения территории — {fmt_number(population_total, 0)} чел., средняя плотность — "
            f"{fmt_number(population_density, 0)} чел./км².{calibration_text} "
            f"По площади кварталов лидируют: {top_land_use_text}. "
            f"Землепользование не определено у {fmt_number(no_land_use, 0)} кварталов, поэтому эту категорию "
            "нужно интерпретировать осторожно."
        ),
        (
            f"В жилых зонах {fmt_number(reclassified_buildings, 0)} OSM-зданий с тегом building=yes "
            "и этажностью 2+ дополнительно признаны жилыми. Это уточняет распределение населения "
            "между кварталами, но итог по-прежнему калибруется на официальную численность."
        ),
        (
            f"По сервису «{service_label}» суммарная ёмкость — {fmt_number(capacity_total, 0)} {service_unit}, "
            f"спрос — {fmt_number(demand_total, 0)} {service_unit}; баланс — "
            f"{'дефицит' if deficit_total > 0 else 'профицит'} {fmt_number(abs(deficit_total), 0)} {service_unit}. "
            f"Полностью обеспечены {fmt_number(provided_blocks, 0)} из {fmt_number(len(provision_values), 0)} кварталов "
            f"со спросом ({fmt_number(provision_share, 1)}%), не обеспечены {fmt_number(unprovided_blocks, 0)}, "
            f"частично — {fmt_number(partial_blocks, 0)}."
        ),
        (
            f"Среди {fmt_number(int(built_mask.sum()), 0)} застроенных кварталов медианный FSI — "
            f"{fmt_number(median_fsi_built['median'] if median_fsi_built else None, 3)}, GSI — "
            f"{fmt_number(median_gsi_built['median'] if median_gsi_built else None, 3)}, MXI — "
            f"{fmt_number(median_mxi_built['median'] if median_mxi_built else None, 3)}, L — "
            f"{fmt_number(median_l_built['median'] if median_l_built else None, 2)} этажа. Это указывает на "
            "преимущественно малоэтажную низкоплотную застройку при наличии отдельных более плотных кварталов."
        ),
        (
            f"Медианное время в пути между кварталами на автомобиле — "
            f"{fmt_number(travel_stats['median'] if travel_stats else None, 1)} мин; 75% пар кварталов "
            f"связаны за {fmt_number(travel_stats['p75'] if travel_stats else None, 1)} мин. "
            f"Медианная доступность территории — "
            f"{fmt_number(accessibility_stats['median'] if accessibility_stats else None, 1)} мин."
        ),
        (
            f"Самые частые морфотипы Spacematrix: {top_spacematrix_text}. По Strelka: {top_strelka_text}. "
            "Классификация опирается на оценённые площади и этажность, а не на официальные данные о застройке."
        ),
    ]

    payload = {
        "service": service,
        "serviceLabel": service_label,
        "serviceUnit": service_unit,
        "territory": args.territory,
        "map": {"metrics": map_metrics},
        "table": {"columns": table_columns, "rows": table_rows},
        "charts": {
            "landUse": {
                "canvas": "chartLandUse",
                "type": "bar",
                "title": "Площадь кварталов по землепользованию",
                "shortLabel": "Землепользование",
                "caption": "Сумма площадей кварталов по категориям, гектары.",
                "labels": list(land_use_area.index),
                "values": [float(value) for value in land_use_area.to_numpy()],
                "colors": land_use_colors,
                "datasetLabel": "Площадь",
                "unit": "га",
                "horizontal": True,
            },
            "populationByLandUse": {
                "canvas": "chartPopulation",
                "type": "bar",
                "title": "Население по землепользованию",
                "shortLabel": "Население",
                "caption": "Оценка населения BlocksNet по категориям, человек.",
                "labels": list(land_use_area.index),
                "values": [float(value) for value in land_use_population.to_numpy()],
                "colors": land_use_colors,
                "datasetLabel": "Население",
                "unit": "чел.",
                "horizontal": True,
            },
            "provision": {
                "canvas": "chartProvision",
                "type": "doughnut",
                "title": "Обеспеченность сервисом",
                "shortLabel": "Обеспеченность",
                "caption": "Количество кварталов по уровням обеспеченности, шт.",
                "labels": [item[0] for item in provision_categories],
                "values": [item[1] for item in provision_categories],
                "colors": [item[2] for item in provision_categories],
                "datasetLabel": "Кварталов",
                "unit": "шт.",
            },
            "fsi": {
                "canvas": "chartFsi",
                "type": "bar",
                "title": "Распределение FSI в застроенных кварталах",
                "shortLabel": "FSI",
                "caption": "Количество застроенных кварталов по интервалам FSI, шт.",
                "labels": fsi_labels,
                "values": [int(value) for value in fsi_counts],
                "colors": ["#6a51a3"] * len(fsi_labels),
                "datasetLabel": "Кварталов",
                "unit": "шт.",
                "horizontal": False,
            },
            "travel": {
                "canvas": "chartTravel",
                "type": "bar",
                "title": "Распределение времени в пути на автомобиле",
                "shortLabel": "Время в пути",
                "caption": "Пары кварталов по интервалам времени, минуты; нули исключены.",
                "labels": travel_labels,
                "values": [int(value) for value in travel_counts],
                "colors": ["#2171b5"] * len(travel_labels),
                "datasetLabel": "Пар кварталов",
                "unit": "пар",
                "horizontal": False,
            },
            "accessibility": {
                "canvas": "chartAccessibility",
                "type": "bar",
                "title": "Распределение доступности территории",
                "shortLabel": "Доступность",
                "caption": "Кварталы по интервалам средневзвешенного времени, минуты.",
                "labels": accessibility_labels,
                "values": [int(value) for value in accessibility_counts],
                "colors": ["#238443"] * len(accessibility_labels),
                "datasetLabel": "Кварталов",
                "unit": "шт.",
                "horizontal": False,
            },
            "spacematrix": {
                "canvas": "chartSpacematrix",
                "type": "bar",
                "title": "Морфотипы Spacematrix",
                "shortLabel": "Spacematrix",
                "caption": "Количество застроенных кварталов по морфотипам, шт.",
                "labels": list(spacematrix_counts.index),
                "values": [int(value) for value in spacematrix_counts.to_numpy()],
                "colors": [spacematrix_colors.get(label, "#999999") for label in spacematrix_counts.index],
                "datasetLabel": "Кварталов",
                "unit": "шт.",
                "horizontal": True,
            },
            "strelka": {
                "canvas": "chartStrelka",
                "type": "bar",
                "title": "Морфотипы Strelka",
                "shortLabel": "Strelka",
                "caption": "Количество застроенных кварталов по морфотипам, шт.",
                "labels": list(strelka_counts.index),
                "values": [int(value) for value in strelka_counts.to_numpy()],
                "colors": [strelka_colors.get(label, "#999999") for label in strelka_counts.index],
                "datasetLabel": "Кварталов",
                "unit": "шт.",
                "horizontal": True,
            },
        },
    }

    map_properties = merged[
        [
            "land_use_label",
            "population",
            "capacity",
            "demand",
            "provision_strong",
            "fsi",
            "gsi",
            "mxi",
            "l",
            "area_accessibility",
            "morphotype_spacematrix",
            "morphotype_strelka",
        ]
    ].copy()
    map_gdf = blocks.to_crs(4326)[["geometry"]].copy()
    geojson = make_geojson(map_gdf, map_properties)

    data_json = json.dumps(
        payload, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).replace("</", "<\\/")
    blocks_json = json.dumps(
        geojson, ensure_ascii=False, separators=(",", ":"), allow_nan=False
    ).replace("</", "<\\/")

    template = (Path(__file__).resolve().parent / "dashboard_template.tpl").read_text(encoding="utf-8")
    page = (
        template.replace("{{TITLE}}", html.escape(args.title))
        .replace("{{TERRITORY}}", html.escape(args.territory))
        .replace("{{SERVICE_LABEL}}", html.escape(service_label))
        .replace("{{SERVICE_UNIT}}", html.escape(service_unit))
        .replace("{{BLOCKS_COUNT}}", fmt_number(len(merged), 0))
        .replace("{{GENERATED_AT}}", datetime.now().strftime("%d.%m.%Y %H:%M"))
        .replace("{{LAST_MODIFIED}}", last_modified.strftime("%d.%m.%Y %H:%M"))
        .replace("{{KPI_HTML}}", "".join(kpis))
        .replace("{{KPI_CHIPS}}", "".join(top_kpis))
        .replace("{{CONCLUSIONS_HTML}}", "".join(f"<li>{item}</li>" for item in conclusions))
        .replace("{{SUMMARY_TABLE}}", build_summary_table(summary_rows))
        .replace("{{CLUSTER_TABLE}}", build_cluster_table(cluster_rows))
        .replace("{{PROVENANCE_TABLE}}", build_provenance_table(provenance))
        .replace("{{SOURCES_TABLE}}", build_sources_table(source_rows))
        .replace("{{LINKS_COUNT}}", fmt_number(links_count, 0))
        .replace("{{LINKS_VALUE}}", fmt_number(links_value, 0))
        .replace("{{DATA_JSON}}", data_json)
        .replace("{{BLOCKS_JSON}}", blocks_json)
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    html_path.write_text(page, encoding="utf-8")
    print(f"Дашборд сохранён: {html_path}")
    print(f"Открыть: {html_path.as_uri()}")
    if args.open_browser:
        webbrowser.open(html_path.as_uri())


if __name__ == "__main__":
    main()
