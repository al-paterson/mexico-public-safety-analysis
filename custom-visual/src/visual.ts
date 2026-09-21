"use strict";

import powerbi from "powerbi-visuals-api";
import { FormattingSettingsService } from "powerbi-visuals-utils-formattingmodel";
import "./../style/visual.less";

import VisualConstructorOptions = powerbi.extensibility.visual.VisualConstructorOptions;
import VisualUpdateOptions = powerbi.extensibility.visual.VisualUpdateOptions;
import IVisual = powerbi.extensibility.visual.IVisual;
import DataView = powerbi.DataView;

import { VisualFormattingSettingsModel } from "./settings";

// Icon paths. Most are Lucide 24x24 stroke icons (stroke, no fill); multi-part
// icons are separate paths joined with " M". The two "-m" icons are Material
// Symbols: filled shapes drawn on Material's own 960-unit grid (see MATERIAL_ICONS).
const ICONS: { [k: string]: string } = {
    activity:        "M22 12h-4l-3 9L9 3l-3 9H2",
    "chart-bar":     "M3 3v16a2 2 0 0 0 2 2h16 M7 16h8 M7 11h12 M7 6h3",
    "chart-column":  "M3 3v16a2 2 0 0 0 2 2h16 M18 17V9 M13 17V5 M8 17v-3",
    "chart-pie":     "M21 12c.552 0 1.005-.449.95-.998a10 10 0 0 0-8.953-8.951c-.55-.055-.998.398-.998.95v8a1 1 0 0 0 1 1z M21.21 15.89A10 10 0 1 1 8 2.83",
    chart:           "M3 3v18h18 M7 15l3-4 3 3 5-7",
    "shield-m":      "M480-80q-139-35-229.5-159.5T160-516v-244l320-120 320 120v244q0 152-90.5 276.5T480-80Zm0-84q104-33 172-132t68-220v-189l-240-90-240 90v189q0 121 68 220t172 132Zm0-316Z",
    "pin-m":         "M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 294q122-112 181-203.5T720-552q0-109-69.5-178.5T480-800q-101 0-170.5 69.5T240-552q0 71 59 162.5T480-186Zm0 106Q319-217 239.5-334.5T160-552q0-150 96.5-239T480-880q127 0 223.5 89T800-552q0 100-79.5 217.5T480-80Zm0-480Z",
    "map-pin":       "M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0 M15 10a3 3 0 1 1-6 0 3 3 0 0 1 6 0z",
    map:             "M14.106 5.553a2 2 0 0 0 1.788 0l3.659-1.83A1 1 0 0 1 21 4.619v12.764a1 1 0 0 1-.553.894l-4.553 2.277a2 2 0 0 1-1.788 0l-4.212-2.106a2 2 0 0 0-1.788 0l-3.659 1.83A1 1 0 0 1 3 19.381V6.618a1 1 0 0 1 .553-.894l4.553-2.277a2 2 0 0 1 1.788 0z M15 5.764v15 M9 3.236v15",
    sigma:           "M18 7V4H6l6 8-6 8h12v-3",
    "trending-up":   "M16 7h6v6 M22 7l-8.5 8.5-5-5L2 17",
    "trending-down": "M16 17h6v-6 M22 17l-8.5-8.5-5 5L2 7",
    users:           "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2 M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0z M22 21v-2a4 4 0 0 0-3-3.87 M16 3.13a4 4 0 0 1 0 7.75",
    layers:          "M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z M2 12.18a1 1 0 0 0 .6.9l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 .6-.91 M2 17.18a1 1 0 0 0 .6.9l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 .6-.91",
    bar:             "M4 20V10 M10 20V4 M16 20v-7 M20 20H2",
    pie:             "M12 3a9 9 0 1 0 9 9h-9z M12 3v9",
    percent:         "M19 5 5 19 M9 6.5a2.5 2.5 0 1 1-5 0a2.5 2.5 0 1 1 5 0z M20 17.5a2.5 2.5 0 1 1-5 0a2.5 2.5 0 1 1 5 0z",
    people:          "M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2 M10 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M22 21v-2a4 4 0 0 0-3-3.87 M17 3.13A4 4 0 0 1 17 11",
    pin:             "M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z M12 12a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z",
    shield:          "M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z",
    table:           "M3 3h18v18H3z M3 9h18 M3 15h18 M12 3v18",
    box:             "M21 8V16l-9 5-9-5V8l9-5 9 5z M3 8l9 5 9-5 M12 13v8"
};

// Icons that are not Lucide stroke icons: their own viewBox, drawn filled.
const MATERIAL_ICONS: { [k: string]: { viewBox: string, filled: boolean } } = {
    "shield-m": { viewBox: "0 -960 960 960", filled: true },
    "pin-m":    { viewBox: "0 -960 960 960", filled: true }
};

function svgIcon(name: string, size: number, color: string): string {
    const d = ICONS[name] || ICONS.chart;
    const mat = MATERIAL_ICONS[name];
    const viewBox = mat ? mat.viewBox : "0 0 24 24";
    const paint = mat && mat.filled
        ? `fill="${color}" stroke="none"`
        : `fill="none" stroke="${color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"`;
    const paths = d.split(" M").map((seg, i) => (i === 0 ? seg : "M" + seg))
        .map(p => `<path d="${p}"/>`).join("");
    return `<svg width="${size}" height="${size}" viewBox="${viewBox}" ${paint} ` +
        `preserveAspectRatio="xMidYMid meet">${paths}</svg>`;
}

/**
 * One small set of layout numbers used by every mode: a single corner radius,
 * a few gaps and paddings, and a short type scale. When something looks off,
 * pick another value from this set rather than adding a new one.
 */
const REF = {
    radius: 10,                       // one radius, everywhere
    gap: { flush: 0, related: 5, iconText: 8, iconCol: 10 },
    // padding, per mode
    pad: {
        cardX: 18, cardTop: 10, cardBot: 12,
        panelTop: 9, panelLeft: 10, panelRight: 10, panelBot: 9,
        headerX: 15
    },
    // type scale: supporting 11..16, then the 30 headline value
    type: { subtitle: 11, label: 12, panelTitle: 13, headerTitle: 16, value: 30 },
    weight: { label: "600", title: "600", value: "600" },
    icon: { panel: 16, card: 26, header: 20 },
    valueCentre: 0.61,               // not used: the card value is centred with flex + 22px top padding
    color: {
        foreground: "#252423",
        neutralSecondary: "#605E5C",
        neutralTertiary: "#8A8886",
        accent: "#4B8B3B",
        border: "#E8E8E8",
        headerBorder: "#EDEBE9"
    }
};

// The report canvas is 1280 wide, so the numbers above apply 1:1, no scaling.
// (Set to 1920/1280 only if the canvas were 1920.)
const SCALE = 1;
const px = (n: number): string => Math.round(n * SCALE) + "px";
const sc = (n: number): number => Math.round(n * SCALE);

function firstMeasure(dv: DataView): { value: number | null, comparison: number | null, format: string } {
    const out = { value: null as number | null, comparison: null as number | null, format: "" };
    const vals = dv && dv.categorical && dv.categorical.values;
    if (!vals) return out;
    for (const col of vals) {
        const roles = col.source.roles || {};
        const v = (col.values && col.values.length) ? Number(col.values[col.values.length - 1]) : null;
        if (roles["value"]) { out.value = v; out.format = col.source.format || ""; }
        else if (roles["comparison"]) { out.comparison = v; }
    }
    return out;
}

export class Visual implements IVisual {
    private root: HTMLElement;
    private settings: VisualFormattingSettingsModel;
    private settingsService: FormattingSettingsService;

    constructor(options: VisualConstructorOptions) {
        this.settingsService = new FormattingSettingsService();
        this.root = options.element;
        this.root.style.width = "100%";
        this.root.style.height = "100%";
        this.root.style.overflow = "hidden";
        this.root.style.fontFamily = "'Segoe UI', wf_segoe-ui_normal, helvetica, arial, sans-serif";
    }

    public update(options: VisualUpdateOptions) {
        try {
            this.render(options);
        } catch (e) {
            this.root.innerHTML = "";
            const err = document.createElement("pre");
            err.style.whiteSpace = "pre-wrap";
            err.style.color = "#B00020";
            err.style.fontSize = "10px";
            err.style.margin = "4px";
            err.textContent = "panel error: " + (e && (e as Error).stack ? (e as Error).stack : String(e));
            this.root.appendChild(err);
        }
    }

    private render(options: VisualUpdateOptions) {
        const dv = options.dataViews && options.dataViews[0];
        this.settings = this.settingsService.populateFormattingSettingsModel(VisualFormattingSettingsModel, dv);
        const s = this.settings;

        const mode = (s.panelCard.mode.value.value as string) || "card";
        const fill = s.panelCard.fill.value.value;
        const radius = s.panelCard.radius.value;
        const borderShow = s.panelCard.borderShow.value;
        const borderColor = s.panelCard.borderColor.value.value;

        // frame
        const frame = document.createElement("div");
        frame.style.boxSizing = "border-box";
        frame.style.width = "100%";
        frame.style.height = "100%";
        frame.style.background = (mode === "backboard" || fill) ? fill : "#FFFFFF";
        frame.style.borderRadius = radius + "px";
        frame.style.border = (borderShow && mode !== "backboard") ? `1px solid ${borderColor}` : "none";
        frame.style.display = "flex";
        frame.style.flexDirection = "column";
        frame.style.overflow = "hidden";

        if (mode === "backboard") {
            // just the board
        } else if (mode === "header") {
            frame.appendChild(this.buildHeader(s));
        } else if (mode === "panel") {
            // header strip spans full width with its own padding + bottom border;
            // the body is left empty for a native chart to sit on top.
            frame.appendChild(this.buildPanelHeader(s));
        } else if (mode === "sidebar") {
            // left nav rail: an accent icon near the top; nav buttons sit on top.
            frame.appendChild(this.buildSidebar(s));
        } else { // card
            frame.style.padding = `${px(REF.pad.cardTop)} ${px(REF.pad.cardX)} ${px(REF.pad.cardBot)}`;
            frame.appendChild(this.buildCard(s, dv));
        }

        this.root.innerHTML = "";
        this.root.appendChild(frame);
    }

    /** Sidebar mode: a thin vertical rail with an accent icon near the top. */
    private buildSidebar(s: VisualFormattingSettingsModel): HTMLElement {
        const col = document.createElement("div");
        col.style.display = "flex";
        col.style.flexDirection = "column";
        col.style.alignItems = "center";
        col.style.height = "100%";
        col.style.paddingTop = px(REF.pad.headerX);
        if (s.iconCard.show.value) {
            const ic = document.createElement("div");
            ic.innerHTML = svgIcon(s.iconCard.iconName.value.value as string, sc(s.iconCard.size.value), s.iconCard.color.value.value);
            ic.style.display = "flex";
            col.appendChild(ic);
        }
        return col;
    }

    /** Header mode: box icon + (title over subtitle), left aligned. */
    private buildHeader(s: VisualFormattingSettingsModel): HTMLElement {
        const row = document.createElement("div");
        row.style.display = "flex";
        row.style.alignItems = "center";
        row.style.gap = px(REF.gap.iconCol);
        row.style.height = "100%";
        row.style.padding = `0 ${px(REF.pad.headerX)}`;
        if (s.iconCard.show.value) {
            const ic = document.createElement("div");
            ic.innerHTML = svgIcon(s.iconCard.iconName.value.value as string, sc(REF.icon.header), s.iconCard.color.value.value);
            ic.style.display = "flex";
            row.appendChild(ic);
        }
        row.appendChild(this.titleBlock(s, REF.type.headerTitle));
        return row;
    }

    /** Panel mode: icon + title header strip with a bottom rule; body left empty
     *  for a native chart to overlay (padTop 9, padLeft 10, gap 8). */
    private buildPanelHeader(s: VisualFormattingSettingsModel): HTMLElement {
        const strip = document.createElement("div");
        strip.style.boxSizing = "border-box";
        strip.style.display = "flex";
        strip.style.alignItems = "center";
        strip.style.gap = px(REF.gap.iconText);
        strip.style.padding = `${px(REF.pad.panelTop)} ${px(REF.pad.panelRight)} ${px(REF.pad.panelBot)} ${px(REF.pad.panelLeft)}`;
        strip.style.borderBottom = `1px solid ${REF.color.headerBorder}`;
        if (s.iconCard.show.value) {
            const ic = document.createElement("div");
            ic.innerHTML = svgIcon(s.iconCard.iconName.value.value as string, sc(REF.icon.panel), s.iconCard.color.value.value);
            ic.style.display = "flex";
            strip.appendChild(ic);
        }
        strip.appendChild(this.titleBlock(s, REF.type.panelTitle));
        return strip;
    }

    private titleBlock(s: VisualFormattingSettingsModel, size: number): HTMLElement {
        const box = document.createElement("div");
        box.style.display = "flex";
        box.style.flexDirection = "column";
        box.style.justifyContent = "center";
        const t = document.createElement("div");
        t.textContent = s.titleCard.text.value || "";
        t.style.fontFamily = "'Segoe UI Semibold', 'Segoe UI', sans-serif";
        t.style.fontWeight = REF.weight.title;
        t.style.fontSize = px(size);
        t.style.color = s.titleCard.color.value.value;
        t.style.lineHeight = "1.25";
        box.appendChild(t);
        if (s.titleCard.subtitle.value) {
            const sub = document.createElement("div");
            sub.textContent = s.titleCard.subtitle.value;
            sub.style.fontSize = px(REF.type.subtitle);
            sub.style.fontWeight = "400";
            sub.style.color = s.titleCard.subtitleColor.value.value;
            sub.style.lineHeight = "1.3";
            sub.style.marginTop = "1px";
            box.appendChild(sub);
        }
        return box;
    }

    /** Card mode: icon+label row at top, big value at ~0.61 height, optional trend
     *  pill top-right. Label 12/600, value 30/600, icon size from the Icon card (default 18). */
    private buildCard(s: VisualFormattingSettingsModel, dv: DataView): HTMLElement {
        const wrap = document.createElement("div");
        wrap.style.display = "flex";
        wrap.style.flexDirection = "column";
        wrap.style.height = "100%";

        // label row (icon + label), with pill pushed right
        const top = document.createElement("div");
        top.style.display = "flex";
        top.style.alignItems = "center";
        top.style.gap = px(REF.gap.iconText);
        if (s.iconCard.show.value) {
            const ic = document.createElement("div");
            ic.innerHTML = svgIcon(s.iconCard.iconName.value.value as string, sc(s.iconCard.size.value || REF.icon.card), s.iconCard.color.value.value);
            ic.style.display = "flex";
            top.appendChild(ic);
        }
        const label = document.createElement("div");
        label.textContent = s.valueCard.label.value || "";
        label.style.fontSize = px(REF.type.label);
        label.style.fontWeight = REF.weight.label;
        label.style.color = s.valueCard.labelColor.value.value;
        top.appendChild(label);

        const md = firstMeasure(dv);
        if (s.pillCard.show.value && md.value != null && md.comparison != null && md.comparison !== 0) {
            top.appendChild(this.pill(md.value, md.comparison, s));
        }
        wrap.appendChild(top);

        // big value, centred horizontally in the space below the label row,
        // pushed down 22px so it sits in the lower part of the card
        const valWrap = document.createElement("div");
        valWrap.style.flex = "1";
        valWrap.style.display = "flex";
        valWrap.style.alignItems = "center";
        valWrap.style.justifyContent = "center";
        valWrap.style.paddingTop = "22px";
        const val = document.createElement("div");
        val.style.textAlign = "center";
        val.textContent = this.fmt(md.value, md.format, s.valueCard.precision.value);
        val.style.fontFamily = "'Segoe UI Semibold', 'Segoe UI', sans-serif";
        val.style.fontWeight = REF.weight.value;
        val.style.fontSize = px(s.valueCard.fontSize.value || REF.type.value);
        val.style.color = s.valueCard.color.value.value;
        val.style.lineHeight = "1.1";
        valWrap.appendChild(val);
        wrap.appendChild(valWrap);
        return wrap;
    }

    private pill(value: number, comparison: number, s: VisualFormattingSettingsModel): HTMLElement {
        const pct = (value - comparison) / Math.abs(comparison) * 100;
        let good = pct >= 0;
        if (s.pillCard.invert.value) good = !good;
        const color = good ? s.pillCard.goodColor.value.value : s.pillCard.badColor.value.value;
        const el = document.createElement("div");
        el.style.marginLeft = "auto";
        el.style.display = "inline-flex";
        el.style.alignItems = "center";
        el.style.gap = px(3);
        el.style.padding = `${px(2)} ${px(8)}`;
        el.style.borderRadius = "999px";
        el.style.fontSize = px(REF.type.label);
        el.style.fontWeight = "600";
        el.style.color = color;
        el.style.background = this.tint(color, 0.12);
        const arrow = pct >= 0 ? "↗" : "↘";
        el.textContent = `${arrow} ${pct >= 0 ? "+" : ""}${pct.toFixed(1)}%`;
        return el;
    }

    private fmt(v: number | null, format: string, precision: number): string {
        if (v == null) return "";
        const isPct = /%/.test(format);
        const n = isPct ? v * 100 : v;
        const s = new Intl.NumberFormat("en-US", {
            minimumFractionDigits: precision,
            maximumFractionDigits: precision
        }).format(n);
        // signed measure formats ("+0.0%;-0.0%") need the + shown too
        const sign = format.startsWith("+") && n > 0 ? "+" : "";
        // ratio formats like 0.00"×" keep their × suffix
        const suffix = /×/.test(format) ? "×" : "";
        return sign + (isPct ? s + "%" : s) + suffix;
    }

    private tint(hex: string, alpha: number): string {
        const h = hex.replace("#", "");
        const r = parseInt(h.substring(0, 2), 16);
        const g = parseInt(h.substring(2, 4), 16);
        const b = parseInt(h.substring(4, 6), 16);
        return `rgba(${r},${g},${b},${alpha})`;
    }

    public getFormattingModel(): powerbi.visuals.FormattingModel {
        return this.settingsService.buildFormattingModel(this.settings);
    }
}
