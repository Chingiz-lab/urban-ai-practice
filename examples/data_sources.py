from __future__ import annotations

import gzip
import json
import math
import re
from pathlib import Path
from typing import Iterable

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from shapely.geometry import box, shape

MICROSOFT_DATASET_URL = (
    "https://bfppub.blob.core.windows.net/%24web/2026-08-13/dataset-links.csv"
)
OFFICIAL_POPULATION = 408_487
OFFICIAL_POPULATION_DATE = "01.01.2025"
OFFICIAL_POPULATION_SOURCE = (
    "Росстат; Правительство Челябинской области, "
    "https://gubernator74.ru/news/rosstat-podschital-chislennost-naseleniya-yuzhnogo-urala"
)

LAND_USE_RULES = {
    "residential": "LandUse.RESIDENTIAL",
    "apartments": "LandUse.RESIDENTIAL",
    "house": "LandUse.RESIDENTIAL",
    "dormitory": "LandUse.RESIDENTIAL",
    "commercial": "LandUse.BUSINESS",
    "retail": "LandUse.BUSINESS",
    "office": "LandUse.BUSINESS",
    "business": "LandUse.BUSINESS",
    "industrial": "LandUse.INDUSTRIAL",
    "garages": "LandUse.INDUSTRIAL",
    "brownfield": "LandUse.INDUSTRIAL",
    "quarry": "LandUse.INDUSTRIAL",
    "landfill": "LandUse.SPECIAL",
    "construction": "LandUse.SPECIAL",
    "cemetery": "LandUse.SPECIAL",
    "grave_yard": "LandUse.SPECIAL",
    "military": "LandUse.SPECIAL",
    "religious": "LandUse.SPECIAL",
    "special": "LandUse.SPECIAL",
    "education": "LandUse.SPECIAL",
    "school": "LandUse.SPECIAL",
    "kindergarten": "LandUse.SPECIAL",
    "hospital": "LandUse.SPECIAL",
    "clinic": "LandUse.SPECIAL",
    "university": "LandUse.SPECIAL",
    "college": "LandUse.SPECIAL",
    "recreation_ground": "LandUse.RECREATION",
    "grass": "LandUse.RECREATION",
    "meadow": "LandUse.RECREATION",
    "forest": "LandUse.RECREATION",
    "wood": "LandUse.RECREATION",
    "scrub": "LandUse.RECREATION",
    "heath": "LandUse.RECREATION",
    "grassland": "LandUse.RECREATION",
    "park": "LandUse.RECREATION",
    "garden": "LandUse.RECREATION",
    "nature_reserve": "LandUse.RECREATION",
    "pitch": "LandUse.RECREATION",
    "playground": "LandUse.RECREATION",
    "flowerbed": "LandUse.RECREATION",
    "village_green": "LandUse.RECREATION",
    "greenfield": "LandUse.RECREATION",
    "allotments": "LandUse.AGRICULTURE",
    "orchard": "LandUse.AGRICULTURE",
    "vineyard": "LandUse.AGRICULTURE",
    "farmland": "LandUse.AGRICULTURE",
    "farmyard": "LandUse.AGRICULTURE",
    "greenhouse_horticulture": "LandUse.AGRICULTURE",
    "aquaculture": "LandUse.AGRICULTURE",
    "railway": "LandUse.TRANSPORT",
    "transport": "LandUse.TRANSPORT",
    "basin": "LandUse.SPECIAL",
    "reservoir": "LandUse.SPECIAL",
}

ZONE_ALIASES = {
    "жил": "residential",
    "многоэтаж": "residential",
    "среднеэтаж": "residential",
    "малоэтаж": "residential",
    "индивидуальн": "residential",
    "общественно-делов": "commercial",
    "коммерц": "commercial",
    "бизнес": "commercial",
    "производ": "industrial",
    "промыш": "industrial",
    "инженерн": "industrial",
    "рекреа": "recreation_ground",
    "парк": "park",
    "лесопарк": "forest",
    "лес": "forest",
    "транспорт": "transport",
    "улиц": "transport",
    "дорог": "transport",
    "сельскохоз": "farmland",
    "дач": "allotments",
    "садов": "allotments",
    "огород": "allotments",
    "кладбищ": "cemetery",
    "воен": "military",
    "специальн": "special",
    "водн": "basin",
}

OFFICIAL_SOURCE_REGISTRY = [
    {
        "group": "Федеральные",
        "name": "НСПД / ПКК Росреестра",
        "url": "https://nspd.gov.ru",
        "role": "Границы, земельные участки, контуры зданий и этажность",
        "status": "нужна выгрузка или доступ к API",
    },
    {
        "group": "Региональные",
        "name": "ГИСОГД Челябинской области",
        "url": "https://gisogd74.gov74.ru",
        "role": "Генплан, правила землепользования и застройки, функциональные зоны",
        "status": "нужна выгрузка из портала",
    },
    {
        "group": "Муниципальные",
        "name": "ГИС-портал Магнитогорска",
        "url": "https://gisportal.magnitogorsk.ru",
        "role": "Слои генплана, ПЗЗ, адресный план и объекты инфраструктуры",
        "status": "нужна выгрузка WFS/WMS или файл ГИС",
    },
    {
        "group": "Федеральные",
        "name": "ЕГРН / ГИС ЖКХ",
        "url": "https://dom.gosuslugi.ru",
        "role": "Жилой фонд, этажность, площади и число проживающих",
        "status": "нужна авторизация и выгрузка",
    },
    {
        "group": "Федеральные",
        "name": "Росстат",
        "url": "https://rosstat.gov.ru",
        "role": "Официальная численность населения на контрольную дату",
        "status": "используется как контрольная сумма",
    },
    {
        "group": "Региональные",
        "name": "Минобр Челябинской области / bus.gov.ru",
        "url": "https://bus.gov.ru",
        "role": "Школы, дошкольные учреждения и их проектная ёмкость",
        "status": "нужна выгрузка или сверка",
    },
    {
        "group": "Дополнительные",
        "name": "OpenStreetMap",
        "url": "https://www.openstreetmap.org",
        "role": "Дороги, вода, здания, сервисы и первичные функциональные зоны",
        "status": "используется",
    },
    {
        "group": "Дополнительные",
        "name": "Microsoft GlobalMLBuildingFootprints",
        "url": "https://github.com/microsoft/GlobalMLBuildingFootprints",
        "role": "Дополнение контуров зданий там, где OSM неполон",
        "status": "используется как дополнение",
    },
]

OFFICIAL_FILENAMES = {
    "boundary": [
        "boundary.geojson",
        "official_boundary.geojson",
        "boundaries.geojson",
        "boundary.gpkg",
        "official_boundary.gpkg",
    ],
    "landuse": [
        "landuse.geojson",
        "functional_zones.geojson",
        "zones.geojson",
        "official_zones.geojson",
        "pzz.geojson",
        "landuse.gpkg",
        "functional_zones.gpkg",
    ],
    "buildings": [
        "buildings.geojson",
        "official_buildings.geojson",
        "buildings.gpkg",
        "official_buildings.gpkg",
    ],
    "population": [
        "population.csv",
        "population_by_block.csv",
        "blocks_population.csv",
    ],
}


def find_official_file(directory: str | Path, kind: str) -> Path | None:
    directory = Path(directory)
    if not directory.exists():
        return None
    for name in OFFICIAL_FILENAMES.get(kind, []):
        path = directory / name
        if path.exists():
            return path
    return None


def load_official_boundary(directory: str | Path) -> gpd.GeoDataFrame | None:
    path = find_official_file(directory, "boundary")
    if path is None:
        return None
    gdf = gpd.read_file(path)
    if gdf.empty:
        return None
    gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty].copy()
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    return gdf.to_crs(4326)


def _first_existing_column(gdf: gpd.GeoDataFrame, names: Iterable[str]) -> str | None:
    lower = {str(column).strip().lower(): column for column in gdf.columns}
    for name in names:
        if name.lower() in lower:
            return lower[name.lower()]
    return None


def _zone_value(value: object) -> str:
    text = str(value).strip()
    if not text or text.lower() in {
        "nan",
        "none",
        "нет",
        "не определено",
        "polygon",
        "multipolygon",
        "linestring",
        "multilinestring",
        "point",
        "node",
        "way",
        "relation",
    }:
        return ""
    lowered = text.lower()
    if lowered.startswith("landuse."):
        lowered = lowered.split(".", 1)[1]
    if lowered in LAND_USE_RULES:
        return lowered
    for token, zone in ZONE_ALIASES.items():
        if token in lowered:
            return zone
    return lowered


def normalize_functional_zones(
    gdf: gpd.GeoDataFrame,
    crs,
    source: str = "osm",
) -> gpd.GeoDataFrame:
    if gdf is None or gdf.empty:
        return gpd.GeoDataFrame(
            {"functional_zone": [], "source": [], "geometry": []},
            geometry="geometry",
            crs=crs,
        )
    gdf = gdf[gdf.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    if gdf.empty:
        return gpd.GeoDataFrame(
            {"functional_zone": [], "source": [], "geometry": []},
            geometry="geometry",
            crs=crs,
        )
    candidate_columns = [
        "functional_zone",
        "landuse",
        "land_use",
        "zone",
        "zonetype",
        "type",
        "leisure",
        "amenity",
        "natural",
        "категория",
        "вид_разрешенного_использования",
        "назначение",
    ]
    lower = {str(column).strip().lower(): column for column in gdf.columns}
    zone_columns = [lower[name.lower()] for name in candidate_columns if name.lower() in lower]
    if not zone_columns:
        return gpd.GeoDataFrame(
            {"functional_zone": [], "source": [], "geometry": []},
            geometry="geometry",
            crs=crs,
        )
    values = pd.Series("", index=gdf.index, dtype="object")
    for column in reversed(zone_columns):
        mapped = gdf[column].map(_zone_value)
        values = mapped.where(mapped != "", values)
    zones = gpd.GeoDataFrame(
        {"functional_zone": values, "geometry": gdf.geometry},
        geometry="geometry",
        crs=gdf.crs,
    )
    zones = zones[zones["functional_zone"] != ""].copy()
    zones["source"] = source
    if zones.crs != crs:
        zones = zones.to_crs(crs)
    return zones.reset_index(drop=True)


def load_official_landuse(directory: str | Path, crs) -> gpd.GeoDataFrame | None:
    path = find_official_file(directory, "landuse")
    if path is None:
        return None
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    gdf = gdf.to_crs(crs)
    zones = normalize_functional_zones(gdf, crs, source="official")
    return zones if not zones.empty else None


def _numeric_column(gdf: gpd.GeoDataFrame, names: Iterable[str]) -> pd.Series:
    column = _first_existing_column(gdf, names)
    if column is None:
        return pd.Series(np.nan, index=gdf.index, dtype="float64")
    return pd.to_numeric(gdf[column], errors="coerce")


def _living_from_tags(tags: pd.Series) -> pd.Series:
    living_tags = {
        "residential",
        "house",
        "apartments",
        "detached",
        "terrace",
        "dormitory",
        "residential_building",
        "жилой",
        "жилое",
    }
    return tags.fillna("").astype(str).str.lower().isin(living_tags)


def normalize_buildings(
    gdf: gpd.GeoDataFrame,
    crs,
    source: str,
    default_living: bool = False,
) -> gpd.GeoDataFrame:
    if gdf is None or gdf.empty:
        return gpd.GeoDataFrame(
            {
                "building": [],
                "is_living": [],
                "number_of_floors": [],
                "source": [],
                "geometry": [],
            },
            geometry="geometry",
            crs=crs,
        )
    gdf = gdf[gdf.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    if gdf.empty:
        return gpd.GeoDataFrame(
            {
                "building": [],
                "is_living": [],
                "number_of_floors": [],
                "source": [],
                "geometry": [],
            },
            geometry="geometry",
            crs=crs,
        )
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    if gdf.crs != crs:
        gdf = gdf.to_crs(crs)

    building_column = _first_existing_column(
        gdf, ["building", "building_type", "type", "use", "назначение", "тип"]
    )
    building = (
        gdf[building_column].astype(str)
        if building_column is not None
        else pd.Series("yes", index=gdf.index)
    )
    floors = _numeric_column(
        gdf,
        [
            "number_of_floors",
            "floors",
            "building:levels",
            "levels",
            "этажность",
            "этажи",
        ],
    )
    height = _numeric_column(gdf, ["height", "building:height", "высота"])
    floors = floors.where(floors > 0)
    height_floors = (height / 3.0).round().clip(lower=1)
    floors = floors.fillna(height_floors)

    living_column = _first_existing_column(
        gdf, ["is_living", "living", "residential", "жилой", "жилая"]
    )
    if living_column is not None:
        raw = gdf[living_column]
        if pd.api.types.is_bool_dtype(raw):
            is_living = raw.fillna(False).astype(bool)
        else:
            is_living = raw.fillna("").astype(str).str.lower().isin(
                {"1", "true", "yes", "да", "жилой", "жилая"}
            )
    else:
        is_living = _living_from_tags(building)
        use_column = _first_existing_column(gdf, ["building:use", "building_use"])
        if use_column is not None:
            is_living = is_living | _living_from_tags(gdf[use_column])
    if default_living and living_column is None:
        is_living = pd.Series(True, index=gdf.index)

    normalized = gpd.GeoDataFrame(
        {
            "building": building.fillna("yes").replace("", "yes"),
            "is_living": is_living.astype(bool),
            "number_of_floors": floors,
            "source": source,
            "geometry": gdf.geometry,
        },
        geometry="geometry",
        crs=crs,
    )
    normalized = normalized[normalized.geometry.notna() & ~normalized.geometry.is_empty]
    return normalized.reset_index(drop=True)


def reclassify_generic_residential(
    buildings: gpd.GeoDataFrame,
    blocks: gpd.GeoDataFrame,
    min_floors: int = 2,
) -> tuple[gpd.GeoDataFrame, int]:
    """Признать жилыми OSM-здания building=yes в жилых зонах при известной этажности."""
    if buildings.empty or "land_use" not in blocks.columns:
        return buildings, 0

    residential_mask = blocks["land_use"].astype(str).str.contains("RESIDENTIAL", na=False)
    if not residential_mask.any():
        return buildings, 0

    residential_area = blocks.loc[residential_mask, "geometry"].union_all()
    generic = (
        buildings["building"].fillna("").astype(str).str.strip().str.lower().isin({"yes", "building"})
    )
    source = (
        buildings["source"].fillna("").astype(str)
        if "source" in buildings.columns
        else pd.Series("", index=buildings.index)
    )
    floors = pd.to_numeric(buildings["number_of_floors"], errors="coerce")
    candidates = (
        ~buildings["is_living"].fillna(False).astype(bool)
        & generic
        & source.ne("official")
        & (floors >= min_floors)
    )
    if not candidates.any():
        return buildings, 0

    inside = buildings.geometry.representative_point().within(residential_area)
    reclassified = candidates & inside
    result = buildings.copy()
    result.loc[reclassified, "is_living"] = True
    return result, int(reclassified.sum())


def load_official_buildings(
    directory: str | Path,
    crs,
    default_living: bool = False,
) -> gpd.GeoDataFrame | None:
    path = find_official_file(directory, "buildings")
    if path is None:
        return None
    gdf = gpd.read_file(path)
    buildings = normalize_buildings(gdf, crs, source="official", default_living=default_living)
    return buildings if not buildings.empty else None


def load_official_services(
    directory: str | Path,
    service: str,
    crs,
) -> gpd.GeoDataFrame | None:
    directory = Path(directory)
    candidates = [
        directory / f"services_{service}.geojson",
        directory / f"{service}.geojson",
        directory / f"{service}s.geojson",
        directory / "services.geojson",
    ]
    path = next((path for path in candidates if path.exists()), None)
    if path is None:
        return None
    gdf = gpd.read_file(path)
    if gdf.crs is None:
        gdf = gdf.set_crs(4326)
    gdf = gdf.to_crs(crs)
    amenity_column = _first_existing_column(gdf, ["amenity", "service", "type", "тип"])
    if amenity_column is not None and path.name == "services.geojson":
        gdf = gdf[gdf[amenity_column].astype(str).str.lower() == service].copy()
    if gdf.empty:
        return None
    if "amenity" not in gdf.columns:
        gdf["amenity"] = service
    return gdf


def load_official_population(
    directory: str | Path,
    blocks: gpd.GeoDataFrame,
) -> pd.Series | None:
    path = find_official_file(directory, "population")
    if path is None:
        return None
    table = pd.read_csv(path)
    population_column = _first_existing_column(table, ["population", "население", "value"])
    if population_column is None:
        return None
    block_column = _first_existing_column(table, ["block_id", "id", "quarter_id", "квартал"])
    if block_column is not None:
        values = pd.to_numeric(table[population_column], errors="coerce")
        series = pd.Series(values.to_numpy(), index=table[block_column].to_numpy())
        return series.reindex(blocks.index).astype("float64")
    geometry_column = _first_existing_column(table, ["geometry", "wkt", "geom"])
    if geometry_column is None:
        return None
    points = gpd.GeoDataFrame(
        table,
        geometry=gpd.GeoSeries.from_wkt(table[geometry_column], crs=4326),
    ).to_crs(blocks.crs)
    joined = gpd.sjoin(points, blocks[["geometry"]], predicate="within", how="left")
    return (
        pd.to_numeric(joined[population_column], errors="coerce")
        .groupby(joined["index_right"])
        .sum()
        .reindex(blocks.index)
        .astype("float64")
    )


def calibrate_population(
    blocks: gpd.GeoDataFrame,
    target: int,
    population_column: str = "population",
    raw_column: str = "population_model_raw",
) -> tuple[gpd.GeoDataFrame, dict[str, float | int | None]]:
    blocks = blocks.copy()
    raw = pd.to_numeric(blocks[population_column], errors="coerce").fillna(0).clip(lower=0)
    blocks[raw_column] = raw
    raw_total = float(raw.sum())
    if raw_total <= 0:
        return blocks, {
            "model_total": 0,
            "official_total": int(target),
            "factor": None,
            "blocks_with_population": 0,
        }

    scaled = raw / raw_total * float(target)
    base = np.floor(scaled).astype(int)
    remainder = int(target - base.sum())
    if remainder:
        order = np.argsort(-(scaled - base).to_numpy())
        base.iloc[order[:remainder]] += 1
    blocks[population_column] = base.astype("float64")
    return blocks, {
        "model_total": raw_total,
        "official_total": int(target),
        "factor": float(target) / raw_total,
        "blocks_with_population": int((blocks[population_column] > 0).sum()),
    }


def _drop_centroid_inside(
    candidate: gpd.GeoDataFrame,
    reference: gpd.GeoDataFrame,
) -> gpd.GeoDataFrame:
    if candidate.empty or reference.empty:
        return candidate
    candidate = candidate[~candidate.geometry.is_empty].copy()
    reference = reference[~reference.geometry.is_empty].copy()
    centroids = candidate.geometry.centroid
    points = gpd.GeoDataFrame(geometry=centroids, crs=candidate.crs)
    joined = gpd.sjoin(points, reference[["geometry"]], predicate="within", how="inner")
    duplicated = pd.Index(joined.index).unique()
    return candidate.drop(index=duplicated)


def infer_microsoft_living(
    microsoft: gpd.GeoDataFrame,
    osm: gpd.GeoDataFrame,
    residential_area=None,
    max_distance: float = 100.0,
) -> gpd.GeoDataFrame:
    if microsoft.empty:
        return microsoft
    microsoft = microsoft.copy()
    microsoft["is_living"] = False
    living = osm[osm["is_living"]].copy()
    if not living.empty:
        try:
            nearest = gpd.sjoin_nearest(
                microsoft[["geometry"]],
                living[["geometry"]],
                how="left",
                max_distance=max_distance,
                distance_col="_distance",
            )
            near_ids = pd.Index(nearest.loc[nearest["index_right"].notna()].index).unique()
            microsoft.loc[microsoft.index.isin(near_ids), "is_living"] = True
        except Exception:
            buffered = living.geometry.buffer(max_distance)
            near_ids = _drop_centroid_inside(microsoft, gpd.GeoDataFrame(geometry=buffered, crs=microsoft.crs)).index
            microsoft.loc[~microsoft.index.isin(near_ids), "is_living"] = True
    if residential_area is not None and not residential_area.is_empty:
        inside = microsoft.geometry.centroid.within(residential_area)
        microsoft.loc[inside, "is_living"] = True
    microsoft.loc[microsoft.geometry.area < 25, "is_living"] = False
    return microsoft


def combine_buildings(
    osm: gpd.GeoDataFrame,
    microsoft: gpd.GeoDataFrame | None = None,
    official: gpd.GeoDataFrame | None = None,
) -> gpd.GeoDataFrame:
    parts: list[gpd.GeoDataFrame] = []
    reference = gpd.GeoDataFrame(geometry=[], crs=osm.crs)
    for layer in (official, osm, microsoft):
        if layer is None or layer.empty:
            continue
        layer = layer.copy()
        if not reference.empty:
            layer = _drop_centroid_inside(layer, reference)
        if layer.empty:
            continue
        parts.append(layer)
        reference = gpd.GeoDataFrame(
            pd.concat([reference, layer[["geometry"]]], ignore_index=True),
            geometry="geometry",
            crs=osm.crs,
        )
    if not parts:
        return gpd.GeoDataFrame(
            {
                "building": [],
                "is_living": [],
                "number_of_floors": [],
                "source": [],
                "geometry": [],
            },
            geometry="geometry",
            crs=osm.crs,
        )
    combined = pd.concat(parts, ignore_index=True)
    return gpd.GeoDataFrame(combined, geometry="geometry", crs=osm.crs).reset_index(drop=True)


def _quadkey_to_xy(quadkey: str) -> tuple[int, int]:
    x = y = 0
    for index, digit in enumerate(quadkey):
        mask = 1 << (len(quadkey) - index - 1)
        if digit == "1":
            x |= mask
        elif digit == "2":
            y |= mask
        elif digit == "3":
            x |= mask
            y |= mask
    return x, y


def quadkey_bounds(quadkey: str) -> tuple[float, float, float, float]:
    x, y = _quadkey_to_xy(quadkey)
    level = len(quadkey)
    count = 2 ** level

    def lon(tile_x: int) -> float:
        return tile_x / count * 360.0 - 180.0

    def lat(tile_y: int) -> float:
        return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * tile_y / count))))

    return lon(x), lat(y + 1), lon(x + 1), lat(y)


def _download(url: str, path: Path, force: bool = False) -> Path:
    if path.exists() and not force and path.stat().st_size > 0:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=180) as response:
        response.raise_for_status()
        with path.open("wb") as file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file.write(chunk)
    return path


def download_microsoft_buildings(
    boundary: gpd.GeoDataFrame,
    cache_dir: str | Path,
    crs,
    force: bool = False,
) -> gpd.GeoDataFrame:
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    boundary_4326 = boundary.to_crs(4326)
    bounds = boundary_4326.total_bounds

    links_path = _download(
        MICROSOFT_DATASET_URL,
        cache_dir / "dataset-links.csv",
        force=force,
    )
    links = pd.read_csv(links_path, dtype=str)
    if "QuadKey" not in links.columns or "Url" not in links.columns:
        raise ValueError("В dataset-links.csv нет колонок QuadKey/Url")

    minx, miny, maxx, maxy = bounds
    selected: list[pd.Series] = []
    for _, row in links.iterrows():
        quadkey = str(row["QuadKey"]).strip()
        if not quadkey.isdigit():
            continue
        west, south, east, north = quadkey_bounds(quadkey)
        if east < minx or west > maxx or north < miny or south > maxy:
            continue
        selected.append(row)
    if not selected:
        raise ValueError("Не найдены тайлы Microsoft для границы территории")

    features: list[dict[str, object]] = []
    for row in selected:
        url = str(row["Url"]).strip()
        filename = Path(url.split("?")[0]).name
        path = _download(url, cache_dir / filename, force=force)
        with gzip.open(path, "rt", encoding="utf-8") as file:
            for line in file:
                line = line.strip().rstrip(",")
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    geometry = item.get("geometry")
                    if geometry is None:
                        continue
                    features.append(
                        {
                            "height": item.get("properties", {}).get("height"),
                            "confidence": item.get("properties", {}).get("confidence"),
                            "geometry": shape(geometry),
                        }
                    )
                except (json.JSONDecodeError, TypeError, ValueError):
                    continue

    if not features:
        return gpd.GeoDataFrame(
            {"building": [], "is_living": [], "number_of_floors": [], "source": [], "geometry": []},
            geometry="geometry",
            crs=crs,
        )
    microsoft = gpd.GeoDataFrame(features, geometry="geometry", crs=4326)
    microsoft = microsoft[microsoft.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    microsoft = gpd.clip(microsoft, boundary_4326)
    microsoft = normalize_buildings(
        microsoft,
        crs,
        source="microsoft",
        default_living=False,
    )
    return microsoft


def json_safe(value):
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def write_provenance(path: str | Path, payload: dict) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(json_safe(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path
