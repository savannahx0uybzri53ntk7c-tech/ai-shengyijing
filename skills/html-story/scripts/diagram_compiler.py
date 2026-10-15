#!/usr/bin/env python3
"""Compile a small semantic diagram spec into style-aware, accessible SVG.

This is an original HTML Agent adapter informed by the contracts of the two
MIT-licensed reference projects. It intentionally stays dependency-free.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from html import escape
from pathlib import Path
from typing import Any


TYPES = {"architecture", "flow", "cycle", "timeline", "matrix", "comparison"}
EDGE_KINDS = {"primary", "control", "feedback", "async", "output"}
STYLES = {
    "ai-business",
    "ai-business-wine-balanced",
    "ai-business-gold-noir",
    "ai-business-ivory-gold",
    "ai-vitality",
    "humanist",
}
FORMS = {"scroll", "deck"}
SAFE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")

THEMES = {
    "ai-business": {
        "paper": "#210806",
        "paper2": "#3b100c",
        "ink": "#fff4df",
        "muted": "#bea990",
        "rule": "#7d503b",
        "accent": "#d8a657",
        "focus": "#9a2419",
        "control": "#a4261c",
        "feedback": "#d88424",
        "output": "#f0d99e",
        "font": "'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif",
        "mono": "'SFMono-Regular','Menlo','PingFang SC',monospace",
        "radius": 2,
        "stroke": 2,
        "shadow": 0,
    },
    "ai-business-wine-balanced": {
        "paper": "#210806",
        "paper2": "#3b100c",
        "ink": "#fff4df",
        "muted": "#bea990",
        "rule": "#7d503b",
        "accent": "#d8a657",
        "focus": "#9a2419",
        "control": "#a4261c",
        "feedback": "#d88424",
        "output": "#f0d99e",
        "font": "'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif",
        "mono": "'SFMono-Regular','Menlo','PingFang SC',monospace",
        "radius": 2,
        "stroke": 2,
        "shadow": 0,
    },
    "ai-business-gold-noir": {
        "paper": "#0a0a0a",
        "paper2": "#111111",
        "ink": "#f5f0eb",
        "muted": "#a39787",
        "rule": "#6b5f53",
        "accent": "#d4a574",
        "accent_bright": "#e8c49a",
        "focus": "#1a1a1a",
        "control": "#fdba74",
        "feedback": "#d4a574",
        "output": "#6ee7b7",
        "font": "'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif",
        "mono": "'SFMono-Regular','Menlo','PingFang SC',monospace",
        "radius": 2,
        "stroke": 2,
        "shadow": 0,
    },
    "ai-business-ivory-gold": {
        "paper": "#f6eedf",
        "paper2": "#eadcc5",
        "ink": "#2b2118",
        "muted": "#71604f",
        "rule": "#ac916c",
        "accent": "#a4742f",
        "focus": "#d7b97f",
        "control": "#8b4a38",
        "feedback": "#9b7a42",
        "output": "#6f4c20",
        "font": "'Noto Sans SC','PingFang SC','Microsoft YaHei',sans-serif",
        "mono": "'SFMono-Regular','Menlo','PingFang SC',monospace",
        "radius": 2,
        "stroke": 2,
        "shadow": 0,
    },
    "ai-vitality": {
        "paper": "#ffffff",
        "paper2": "#ffffff",
        "ink": "#000000",
        "muted": "#444444",
        "rule": "#000000",
        "accent": "#FF3B00",
        "focus": "#FFDE59",
        "control": "#FF3B00",
        "feedback": "#000000",
        "output": "#FF3B00",
        "font": "'SFMono-Regular','Menlo','PingFang SC',monospace",
        "mono": "'SFMono-Regular','Menlo','PingFang SC',monospace",
        "radius": 0,
        "stroke": 3,
        "shadow": 7,
    },
    "humanist": {
        "paper": "#f3eadc",
        "paper2": "#e8dcc9",
        "ink": "#2a211b",
        "muted": "#746455",
        "rule": "#9d8975",
        "accent": "#9e4f35",
        "focus": "#d9b987",
        "control": "#9e4f35",
        "feedback": "#60735c",
        "output": "#7a6046",
        "font": "'Songti SC','STSong','Noto Serif SC',serif",
        "mono": "'SFMono-Regular','Menlo','PingFang SC',monospace",
        "radius": 4,
        "stroke": 1.6,
        "shadow": 0,
    },
}


class DiagramContractError(ValueError):
    pass


def _text(value: Any, field: str, limit: int | None = None) -> str:
    result = str(value or "").strip()
    if not result:
        raise DiagramContractError(f"{field} must be non-empty")
    if limit is not None and len(result) > limit:
        raise DiagramContractError(f"{field} exceeds {limit} characters")
    return result


def validate_spec(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise DiagramContractError("diagram spec must be a JSON object")
    spec = dict(raw)
    if spec.get("schema_version") != 1:
        raise DiagramContractError("schema_version must be 1")
    diagram_id = _text(spec.get("id"), "id")
    if not SAFE_ID.fullmatch(diagram_id):
        raise DiagramContractError("id must start with a letter and use only A-Z, a-z, 0-9, _ or -")
    kind = _text(spec.get("type"), "type")
    if kind not in TYPES:
        raise DiagramContractError(f"unsupported diagram type: {kind}")
    spec["title"] = _text(spec.get("title"), "title", 40)
    spec["description"] = _text(spec.get("description"), "description", 120)
    if spec.get("audience", "mixed") not in {"executive", "mixed", "engineer"}:
        raise DiagramContractError("audience must be executive, mixed or engineer")
    if spec.get("detail", "balanced") not in {"simplified", "balanced"}:
        raise DiagramContractError("detail must be simplified or balanced")

    nodes = spec.get("nodes")
    if not isinstance(nodes, list) or len(nodes) < 2:
        raise DiagramContractError("nodes must contain at least 2 items")
    if len(nodes) > 9:
        raise DiagramContractError("SPLIT_REQUIRED: one diagram may contain at most 9 nodes")
    node_ids: set[str] = set()
    focal_count = 0
    normalized_nodes: list[dict[str, Any]] = []
    for index, item in enumerate(nodes):
        if not isinstance(item, dict):
            raise DiagramContractError(f"nodes[{index}] must be an object")
        node = dict(item)
        node_id = _text(node.get("id"), f"nodes[{index}].id")
        if not SAFE_ID.fullmatch(node_id) or node_id in node_ids:
            raise DiagramContractError(f"nodes[{index}].id must be unique and safe")
        node_ids.add(node_id)
        node["label"] = _text(node.get("label"), f"nodes[{index}].label", 14)
        note = str(node.get("note") or "").strip()
        if len(note) > 22:
            raise DiagramContractError(f"nodes[{index}].note exceeds 22 characters")
        node["note"] = note
        node["focal"] = bool(node.get("focal", False))
        node["kind"] = str(node.get("kind") or "concept").strip().lower()
        focal_count += int(node["focal"])
        if kind == "matrix":
            for axis in ("x", "y"):
                value = node.get(axis)
                if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
                    raise DiagramContractError(f"nodes[{index}].{axis} must be between 0 and 1")
        normalized_nodes.append(node)
    if focal_count > 2:
        raise DiagramContractError("at most 2 focal nodes are allowed")
    spec["nodes"] = normalized_nodes

    groups_raw = spec.get("groups", [])
    if not isinstance(groups_raw, list):
        raise DiagramContractError("groups must be an array")
    groups: list[dict[str, str]] = []
    group_ids: set[str] = set()
    for index, item in enumerate(groups_raw):
        if not isinstance(item, dict):
            raise DiagramContractError(f"groups[{index}] must be an object")
        group_id = _text(item.get("id"), f"groups[{index}].id")
        if group_id in group_ids:
            raise DiagramContractError(f"duplicate group id: {group_id}")
        group_ids.add(group_id)
        groups.append({"id": group_id, "label": _text(item.get("label"), f"groups[{index}].label", 14)})
    if kind == "architecture" and not groups:
        raise DiagramContractError("architecture requires ordered groups")
    if kind == "comparison" and not 2 <= len(groups) <= 3:
        raise DiagramContractError("comparison requires 2 or 3 groups")
    if kind in {"architecture", "comparison"}:
        for index, node in enumerate(normalized_nodes):
            if node.get("group") not in group_ids:
                raise DiagramContractError(f"nodes[{index}].group references an unknown group")
    spec["groups"] = groups

    edges_raw = spec.get("edges", [])
    if not isinstance(edges_raw, list):
        raise DiagramContractError("edges must be an array")
    edges: list[dict[str, str]] = []
    for index, item in enumerate(edges_raw):
        if not isinstance(item, dict):
            raise DiagramContractError(f"edges[{index}] must be an object")
        source = _text(item.get("from"), f"edges[{index}].from")
        target = _text(item.get("to"), f"edges[{index}].to")
        if source not in node_ids or target not in node_ids or source == target:
            raise DiagramContractError(f"edges[{index}] has invalid endpoints")
        edge_kind = str(item.get("kind") or "primary")
        if edge_kind not in EDGE_KINDS:
            raise DiagramContractError(f"edges[{index}].kind is unsupported")
        label = str(item.get("label") or "").strip()
        if len(label) > 10:
            raise DiagramContractError(f"edges[{index}].label exceeds 10 characters")
        edges.append({"from": source, "to": target, "kind": edge_kind, "label": label})
    if kind in {"flow", "cycle"} and not edges:
        pairs = list(zip(normalized_nodes, normalized_nodes[1:]))
        if kind == "cycle":
            pairs.append((normalized_nodes[-1], normalized_nodes[0]))
        edges = [{"from": a["id"], "to": b["id"], "kind": "primary", "label": ""} for a, b in pairs]
    spec["edges"] = edges

    ledger = spec.get("fidelity_ledger", {})
    if not isinstance(ledger, dict):
        raise DiagramContractError("fidelity_ledger must be an object")
    source_count = ledger.get("source_node_count", len(nodes))
    if not isinstance(source_count, int) or source_count < len(nodes):
        raise DiagramContractError("fidelity_ledger.source_node_count must be >= drawn node count")
    notes = ledger.get("notes", [])
    if not isinstance(notes, list) or any(not str(note).strip() for note in notes):
        raise DiagramContractError("fidelity_ledger.notes must be non-empty strings")
    if source_count > len(nodes) and not notes:
        raise DiagramContractError("fidelity ledger must explain every reduction")
    spec["fidelity_ledger"] = {"source_node_count": source_count, "notes": [str(note) for note in notes]}
    spec["caption"] = str(spec.get("caption") or "").strip()
    return spec


def load_spec(path: Path) -> dict[str, Any]:
    return validate_spec(json.loads(path.read_text(encoding="utf-8")))


def _layout_architecture(spec: dict[str, Any], mobile: bool) -> tuple[int, int, dict[str, tuple[float, float, float, float]], list[tuple[str, str, float, float, float, float]]]:
    width = 520 if mobile else 1120
    margin = 38 if mobile else 64
    node_h = 70 if mobile else 76
    positions: dict[str, tuple[float, float, float, float]] = {}
    group_boxes: list[tuple[str, str, float, float, float, float]] = []
    y = 46
    for group in spec["groups"]:
        members = [node for node in spec["nodes"] if node.get("group") == group["id"]]
        if mobile:
            # Mobile is the primary delivery surface: use a compact two-column
            # card grid inside each layer instead of a long desktop-like rail.
            # This keeps the hierarchy visible without turning one diagram into
            # a full-screen scroll trap.
            col_gap = 18
            node_w = 190
            columns = 2
            rows = math.ceil(len(members) / columns)
            row_gap = 16
            node_h = 82
            group_h = 48 + rows * node_h + max(0, rows - 1) * row_gap + 20
            group_boxes.append((group["id"], group["label"], margin, y, width - 2 * margin, group_h))
            for index, node in enumerate(members):
                row, col = divmod(index, columns)
                positions[node["id"]] = (
                    margin + 22 + col * (node_w + col_gap),
                    y + 40 + row * (node_h + row_gap),
                    node_w,
                    node_h,
                )
        else:
            group_h = 146
            group_boxes.append((group["id"], group["label"], margin, y, width - 2 * margin, group_h))
            gap = 36
            usable = width - 2 * margin - 52
            node_w = min(250, (usable - gap * max(0, len(members) - 1)) / max(1, len(members)))
            total = len(members) * node_w + max(0, len(members) - 1) * gap
            start_x = (width - total) / 2
            for index, node in enumerate(members):
                positions[node["id"]] = (start_x + index * (node_w + gap), y + 48, node_w, node_h)
        y += group_h + (34 if mobile else 30)
    return width, int(y + 40), positions, group_boxes


def _layout_flow(spec: dict[str, Any], mobile: bool) -> tuple[int, int, dict[str, tuple[float, float, float, float]], list[Any]]:
    nodes = spec["nodes"]
    if mobile:
        width, node_w, node_h, gap = 520, 360, 76, 54
        positions = {node["id"]: ((width - node_w) / 2, 54 + index * (node_h + gap), node_w, node_h) for index, node in enumerate(nodes)}
        return width, 108 + len(nodes) * (node_h + gap), positions, []
    width, node_h = 1120, 80
    rows = 1 if len(nodes) <= 5 else 2
    per_row = math.ceil(len(nodes) / rows)
    node_w = min(190, (width - 120 - (per_row - 1) * 34) / per_row)
    positions: dict[str, tuple[float, float, float, float]] = {}
    for index, node in enumerate(nodes):
        row, col = divmod(index, per_row)
        count = min(per_row, len(nodes) - row * per_row)
        total = count * node_w + (count - 1) * 34
        x = (width - total) / 2 + col * (node_w + 34)
        positions[node["id"]] = (x, 90 + row * 190, node_w, node_h)
    return width, 280 if rows == 1 else 470, positions, []


def _layout_cycle(spec: dict[str, Any], mobile: bool) -> tuple[int, int, dict[str, tuple[float, float, float, float]], list[Any]]:
    nodes = spec["nodes"]
    if mobile:
        width, node_w, node_h = 520, 190, 70
        positions = {}
        for index, node in enumerate(nodes):
            x = 42 if index % 2 == 0 else width - node_w - 42
            positions[node["id"]] = (x, 62 + index * 108, node_w, node_h)
        return width, 150 + len(nodes) * 108, positions, []
    width, height, node_w, node_h = 920, 680, 174, 72
    cx, cy, radius = width / 2, height / 2, 230
    positions = {}
    for index, node in enumerate(nodes):
        angle = -math.pi / 2 + 2 * math.pi * index / len(nodes)
        x = cx + radius * math.cos(angle) - node_w / 2
        y = cy + radius * math.sin(angle) - node_h / 2
        positions[node["id"]] = (x, y, node_w, node_h)
    return width, height, positions, []


def _layout_timeline(spec: dict[str, Any], mobile: bool) -> tuple[int, int, dict[str, tuple[float, float, float, float]], list[Any]]:
    nodes = spec["nodes"]
    if mobile:
        width, node_w, node_h = 520, 330, 74
        positions = {node["id"]: (130, 54 + index * 120, node_w, node_h) for index, node in enumerate(nodes)}
        return width, 120 + len(nodes) * 120, positions, []
    width, node_w, node_h = 1120, min(176, (1000 - (len(nodes) - 1) * 24) / len(nodes)), 84
    total = len(nodes) * node_w + (len(nodes) - 1) * 24
    start = (width - total) / 2
    positions = {node["id"]: (start + index * (node_w + 24), 158, node_w, node_h) for index, node in enumerate(nodes)}
    return width, 390, positions, []


def _layout_matrix(spec: dict[str, Any], mobile: bool) -> tuple[int, int, dict[str, tuple[float, float, float, float]], list[Any]]:
    width, height = (520, 680) if mobile else (960, 620)
    left, top, right, bottom = (74, 74, width - 44, height - 90)
    node_w, node_h = (132, 58) if mobile else (156, 64)
    positions = {}
    for node in spec["nodes"]:
        cx = left + float(node["x"]) * (right - left)
        cy = bottom - float(node["y"]) * (bottom - top)
        positions[node["id"]] = (max(12, min(width - node_w - 12, cx - node_w / 2)), max(18, min(height - node_h - 18, cy - node_h / 2)), node_w, node_h)
    return width, height, positions, [("matrix", "", left, top, right - left, bottom - top)]


def _layout_comparison(spec: dict[str, Any], mobile: bool) -> tuple[int, int, dict[str, tuple[float, float, float, float]], list[tuple[str, str, float, float, float, float]]]:
    width = 520 if mobile else 1120
    positions: dict[str, tuple[float, float, float, float]] = {}
    boxes: list[tuple[str, str, float, float, float, float]] = []
    if mobile:
        y = 40
        for group in spec["groups"]:
            members = [node for node in spec["nodes"] if node.get("group") == group["id"]]
            height = 54 + len(members) * 92
            boxes.append((group["id"], group["label"], 36, y, width - 72, height))
            for index, node in enumerate(members):
                positions[node["id"]] = (62, y + 42 + index * 92, width - 124, 66)
            y += height + 28
        return width, y + 30, positions, boxes
    gap, margin = 28, 46
    col_w = (width - 2 * margin - gap * (len(spec["groups"]) - 1)) / len(spec["groups"])
    max_members = max(len([n for n in spec["nodes"] if n.get("group") == group["id"]]) for group in spec["groups"])
    height = 100 + max_members * 100
    for gi, group in enumerate(spec["groups"]):
        x = margin + gi * (col_w + gap)
        boxes.append((group["id"], group["label"], x, 42, col_w, height - 82))
        members = [node for node in spec["nodes"] if node.get("group") == group["id"]]
        for index, node in enumerate(members):
            positions[node["id"]] = (x + 24, 92 + index * 96, col_w - 48, 68)
    return width, height, positions, boxes


def _layout(spec: dict[str, Any], mobile: bool):
    return {
        "architecture": _layout_architecture,
        "flow": _layout_flow,
        "cycle": _layout_cycle,
        "timeline": _layout_timeline,
        "matrix": _layout_matrix,
        "comparison": _layout_comparison,
    }[spec["type"]](spec, mobile)


def _edge_color(theme: dict[str, Any], kind: str) -> str:
    # Dark-luxury diagrams use one visual language. Edge kind is still
    # encoded by line style, but not by a rainbow of competing colors.
    if theme.get("paper") == "#0a0a0a":
        return {
            "primary": theme["accent"],
            "control": theme["accent"],
            "feedback": theme["muted"],
            "async": theme["rule"],
            "output": theme["accent_bright"],
        }[kind]
    return {
        "primary": theme["accent"],
        "control": theme["control"],
        "feedback": theme["feedback"],
        "async": theme["muted"],
        "output": theme["output"],
    }[kind]


def _node_color(theme: dict[str, Any], node: dict[str, Any]) -> str:
    """Keep dark-luxury nodes restrained; semantics stay in the data layer."""
    if theme.get("paper") == "#0a0a0a":
        return theme["accent"]
    return theme["accent"]


def _route(source: tuple[float, float, float, float], target: tuple[float, float, float, float], curved: bool) -> tuple[str, float, float]:
    sx, sy, sw, sh = source
    tx, ty, tw, th = target
    ax, ay = sx + sw / 2, sy + sh / 2
    bx, by = tx + tw / 2, ty + th / 2
    if curved:
        cx, cy = (ax + bx) / 2 + (by - ay) * 0.12, (ay + by) / 2 - (bx - ax) * 0.12
        return f"M {ax:.1f} {ay:.1f} Q {cx:.1f} {cy:.1f} {bx:.1f} {by:.1f}", cx, cy
    if abs(by - ay) >= abs(bx - ax):
        mid = (ay + by) / 2
        return f"M {ax:.1f} {ay:.1f} V {mid:.1f} H {bx:.1f} V {by:.1f}", (ax + bx) / 2, mid - 8
    mid = (ax + bx) / 2
    return f"M {ax:.1f} {ay:.1f} H {mid:.1f} V {by:.1f} H {bx:.1f}", mid, (ay + by) / 2 - 8


def _render_vitality_flow(spec: dict[str, Any], theme: dict[str, Any], mobile: bool) -> str:
    """AI活力的流程图使用节拍轨道，而非堆叠卡片。"""
    nodes = spec["nodes"]
    variant = "mobile" if mobile else "desktop"
    prefix = f"{spec['id']}-{variant}"
    title_id, desc_id = f"{prefix}-title", f"{prefix}-desc"
    if mobile:
        width, top, step, rail_x = 520, 72, 126, 102
        height = top + (len(nodes) - 1) * step + 96
        coords = {node["id"]: (rail_x, top + index * step) for index, node in enumerate(nodes)}
    else:
        width, height, rail_y = 1120, 430, 216
        left, right = 116, 1004
        step = (right - left) / max(1, len(nodes) - 1)
        coords = {node["id"]: (left + index * step, rail_y) for index, node in enumerate(nodes)}
    lines = [
        f'<svg class="ha-diagram ha-diagram-{variant} ha-diagram-vitality-track" data-diagram-type="flow" data-diagram-contract="v1" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{title_id} {desc_id}" xmlns="http://www.w3.org/2000/svg">',
        f'<title id="{title_id}">{escape(spec["title"])}</title>',
        f'<desc id="{desc_id}">{escape(spec["description"])}</desc>',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]
    for edge_index, edge in enumerate(spec["edges"]):
        sx, sy = coords[edge["from"]]
        tx, ty = coords[edge["to"]]
        color = _edge_color(theme, edge["kind"])
        lines.append(f'<path data-edge="{edge_index}" d="M {sx:.1f} {sy:.1f} L {tx:.1f} {ty:.1f}" fill="none" stroke="{color}" stroke-width="5"/>')
        if edge["label"]:
            label_x, label_y = ((sx + tx) / 2, (sy + ty) / 2 - 12) if not mobile else (rail_x + 38, (sy + ty) / 2 + 4)
            lines.append(f'<text x="{label_x:.1f}" y="{label_y:.1f}" fill="{color}" font-family="{theme["mono"]}" font-size="13" font-weight="900">{escape(edge["label"])}</text>')
    for index, node in enumerate(nodes, start=1):
        x, y = coords[node["id"]]
        fill = theme["focus"] if node["focal"] else "#ffffff"
        stroke = theme["accent"] if node["focal"] else "#000000"
        lines.append(f'<g data-node="{escape(node["id"])}"><circle cx="{x:.1f}" cy="{y:.1f}" r="30" fill="{fill}" stroke="{stroke}" stroke-width="5"/>')
        lines.append(f'<text x="{x:.1f}" y="{y+7:.1f}" text-anchor="middle" fill="#000000" font-family="{theme["mono"]}" font-size="17" font-weight="900">{index:02d}</text>')
        if mobile:
            lines.append(f'<text x="{x+54:.1f}" y="{y-3:.1f}" fill="#000000" font-family="{theme["font"]}" font-size="20" font-weight="900">{escape(node["label"])}</text>')
            if node["note"]:
                lines.append(f'<text x="{x+54:.1f}" y="{y+24:.1f}" fill="{theme["muted"]}" font-family="{theme["mono"]}" font-size="12">{escape(node["note"])}</text>')
        else:
            label_y = y - 52 if index % 2 else y + 74
            lines.append(f'<text x="{x:.1f}" y="{label_y:.1f}" text-anchor="middle" fill="#000000" font-family="{theme["font"]}" font-size="18" font-weight="900">{escape(node["label"])}</text>')
            if node["note"]:
                lines.append(f'<text x="{x:.1f}" y="{label_y+22:.1f}" text-anchor="middle" fill="{theme["muted"]}" font-family="{theme["mono"]}" font-size="11">{escape(node["note"])}</text>')
        lines.append("</g>")
    lines.append("</svg>")
    return "".join(lines)


def render_svg(spec: dict[str, Any], style: str, mobile: bool = False) -> str:
    if style not in STYLES:
        raise DiagramContractError(f"unsupported style: {style}")
    theme = THEMES[style]
    if style == "ai-vitality" and spec["type"] == "flow":
        return _render_vitality_flow(spec, theme, mobile)
    width, height, positions, group_boxes = _layout(spec, mobile)
    variant = "mobile" if mobile else "desktop"
    prefix = f"{spec['id']}-{variant}"
    title_id, desc_id = f"{prefix}-title", f"{prefix}-desc"
    lines = [
        f'<svg class="ha-diagram ha-diagram-{variant}" data-diagram-type="{spec["type"]}" data-diagram-contract="v1" viewBox="0 0 {width} {height}" role="img" aria-labelledby="{title_id} {desc_id}" xmlns="http://www.w3.org/2000/svg">',
        f'<title id="{title_id}">{escape(spec["title"])}</title>',
        f'<desc id="{desc_id}">{escape(spec["description"])}</desc>',
        "<defs>",
    ]
    used_kinds = sorted({edge["kind"] for edge in spec["edges"]})
    for edge_kind in used_kinds or ["primary"]:
        color = _edge_color(theme, edge_kind)
        lines.append(f'<marker id="{prefix}-arrow-{edge_kind}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="{color}"/></marker>')
    lines.extend(["</defs>", f'<rect width="{width}" height="{height}" fill="{theme["paper"]}"/>'])

    if spec["type"] == "matrix":
        _, _, x, y, w, h = group_boxes[0]
        lines.append(f'<path d="M {x:.1f} {y+h:.1f} H {x+w:.1f} M {x:.1f} {y+h:.1f} V {y:.1f}" fill="none" stroke="{theme["rule"]}" stroke-width="{theme["stroke"]}"/>')
        x_label = escape(str(spec.get("x_label") or "横轴：从低到高"))
        y_label = escape(str(spec.get("y_label") or "纵轴：从低到高"))
        lines.append(f'<text x="{x+w:.1f}" y="{y+h+30:.1f}" text-anchor="end" fill="{theme["muted"]}" font-family="{theme["mono"]}" font-size="13">{x_label}</text>')
        lines.append(f'<text x="{x:.1f}" y="{y-20:.1f}" fill="{theme["muted"]}" font-family="{theme["mono"]}" font-size="13">{y_label}</text>')
    else:
        for group_id, group_label, x, y, w, h in group_boxes:
            if theme.get("paper") == "#0a0a0a":
                lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" fill="none" stroke="{theme["accent"]}" stroke-width="0.8" stroke-dasharray="7 5" opacity="0.55"/>')
            else:
                lines.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{theme["radius"]}" fill="{theme["paper2"]}" stroke="{theme["rule"]}" stroke-width="{theme["stroke"]}" opacity="0.96"/>')
            if group_label:
                group_font = "Georgia, 'Times New Roman', serif" if theme.get("paper") == "#0a0a0a" else theme["mono"]
                group_size = "14" if theme.get("paper") == "#0a0a0a" else "12"
                group_fill = theme["accent"] if theme.get("paper") == "#0a0a0a" else theme["muted"]
                lines.append(f'<text x="{x+18:.1f}" y="{y+25:.1f}" fill="{group_fill}" font-family="{group_font}" font-size="{group_size}" font-weight="700" letter-spacing="1.1" opacity="0.82">{escape(group_label.upper())}</text>')

    node_groups = {node["id"]: node.get("group") for node in spec["nodes"]}
    for index, edge in enumerate(spec["edges"]):
        path, label_x, label_y = _route(positions[edge["from"]], positions[edge["to"]], spec["type"] == "cycle")
        color = _edge_color(theme, edge["kind"])
        dash = ' stroke-dasharray="7 6"' if edge["kind"] in {"control", "async"} else ""
        lines.append(f'<path data-edge="{index}" d="{path}" fill="none" stroke="{color}" stroke-width="{theme["stroke"]}"{dash} marker-end="url(#{prefix}-arrow-{edge["kind"]})"/>')
        show_label = bool(edge["label"]) and (not mobile or node_groups.get(edge["from"]) != node_groups.get(edge["to"]))
        if show_label:
            label = escape(edge["label"])
            mask_w = max(42, 15 * len(edge["label"]) + 14)
            label_size = 10 if mobile else 12
            label_h = 20 if mobile else 23
            lines.append(f'<rect x="{label_x-mask_w/2:.1f}" y="{label_y-label_h+5:.1f}" width="{mask_w:.1f}" height="{label_h}" fill="{theme["paper"]}"/>')
            lines.append(f'<text x="{label_x:.1f}" y="{label_y+3:.1f}" text-anchor="middle" fill="{color}" font-family="{theme["mono"]}" font-size="{label_size}" font-weight="700">{label}</text>')

    for node in spec["nodes"]:
        x, y, w, h = positions[node["id"]]
        if theme["shadow"]:
            lines.append(f'<rect x="{x+theme["shadow"]:.1f}" y="{y+theme["shadow"]:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{theme["ink"]}"/>')
        node_color = _node_color(theme, node)
        is_luxury = theme.get("paper") == "#0a0a0a"
        fill = theme["focus"] if node["focal"] else theme["paper2"]
        stroke = theme.get("accent_bright", theme["accent"]) if node["focal"] and is_luxury else node_color if is_luxury else theme["accent"] if node["focal"] else theme["rule"]
        radius = 6 if is_luxury else theme["radius"]
        lines.append(f'<g data-node="{escape(node["id"])}" data-node-kind="{escape(node["kind"])}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{1.5 if is_luxury else theme["stroke"]}"/>')
        label_y = y + (h / 2 - 2 if node["note"] else h / 2 + 6)
        label_fill = theme["accent_bright"] if is_luxury and node["focal"] else theme["ink"] if is_luxury else theme["ink"]
        lines.append(f'<text x="{x+w/2:.1f}" y="{label_y:.1f}" text-anchor="middle" fill="{label_fill}" font-family="{theme["font"]}" font-size="{16 if mobile else 17}" font-weight="800">{escape(node["label"])}</text>')
        if node["note"]:
            lines.append(f'<text x="{x+w/2:.1f}" y="{label_y+22:.1f}" text-anchor="middle" fill="{theme["muted"]}" font-family="{theme["mono"]}" font-size="{10 if mobile else 11}">{escape(node["note"])}</text>')
        if spec["type"] == "timeline" and node.get("time"):
            lines.append(f'<text x="{x+w/2:.1f}" y="{y-15:.1f}" text-anchor="middle" fill="{theme["accent"]}" font-family="{theme["mono"]}" font-size="12" font-weight="800">{escape(str(node["time"]))}</text>')
        lines.append("</g>")

    lines.append("</svg>")
    return "".join(lines)


def render_fragment(spec: dict[str, Any], style: str, form: str) -> str:
    if form not in FORMS:
        raise DiagramContractError(f"unsupported form: {form}")
    desktop = render_svg(spec, style, mobile=False)
    mobile = render_svg(spec, style, mobile=True) if form == "scroll" else ""
    caption = f'<figcaption>{escape(spec["caption"])}</figcaption>' if spec.get("caption") else ""
    return (
        f'<figure class="ha-diagram-figure" data-diagram-id="{escape(spec["id"])}">'
        f'<div class="ha-diagram-desktop-wrap">{desktop}</div>'
        f'<div class="ha-diagram-mobile-wrap">{mobile}</div>'
        f'{caption}'
        "</figure>"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--style", choices=sorted(STYLES), default="ai-business")
    parser.add_argument("--form", choices=sorted(FORMS), default="scroll")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    try:
        spec = load_spec(args.spec)
        if args.check_only:
            print(f"PASS diagram-contract type={spec['type']} nodes={len(spec['nodes'])} edges={len(spec['edges'])}")
            return 0
        if not args.output:
            raise DiagramContractError("--output is required unless --check-only is used")
        fragment = render_fragment(spec, args.style, args.form)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(fragment, encoding="utf-8")
        print(args.output.resolve())
        return 0
    except (DiagramContractError, json.JSONDecodeError) as error:
        print(f"FAIL diagram-contract: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
