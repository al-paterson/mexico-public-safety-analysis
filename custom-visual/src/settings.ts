"use strict";

import { formattingSettings } from "powerbi-visuals-utils-formattingmodel";

import FormattingSettingsCard = formattingSettings.SimpleCard;
import FormattingSettingsSlice = formattingSettings.Slice;
import FormattingSettingsModel = formattingSettings.Model;

/** Panel frame: fill, radius, border. Mode selects backboard/header/card/panel. */
class PanelCard extends FormattingSettingsCard {
    mode = new formattingSettings.ItemDropdown({
        name: "mode",
        displayName: "Mode",
        items: [
            { displayName: "Card", value: "card" },
            { displayName: "Panel", value: "panel" },
            { displayName: "Header", value: "header" },
            { displayName: "Backboard", value: "backboard" },
            { displayName: "Sidebar", value: "sidebar" }
        ],
        value: { displayName: "Card", value: "card" }
    });
    fill = new formattingSettings.ColorPicker({ name: "fill", displayName: "Fill color", value: { value: "#FFFFFF" } });
    radius = new formattingSettings.NumUpDown({ name: "radius", displayName: "Corner radius", value: 10 });
    borderShow = new formattingSettings.ToggleSwitch({ name: "borderShow", displayName: "Border", value: true });
    borderColor = new formattingSettings.ColorPicker({ name: "borderColor", displayName: "Border color", value: { value: "#E8E8E8" } });

    name: string = "panel";
    displayName: string = "Panel";
    slices: Array<FormattingSettingsSlice> = [this.mode, this.fill, this.radius, this.borderShow, this.borderColor];
}

/** Title + subtitle for header/panel modes. */
class TitleCard extends FormattingSettingsCard {
    show = new formattingSettings.ToggleSwitch({ name: "show", displayName: "Show", value: true });
    text = new formattingSettings.TextInput({ name: "text", displayName: "Text", value: "", placeholder: "Title" });
    subtitle = new formattingSettings.TextInput({ name: "subtitle", displayName: "Subtitle", value: "", placeholder: "Subtitle" });
    fontSize = new formattingSettings.NumUpDown({ name: "fontSize", displayName: "Text size", value: 13 });
    color = new formattingSettings.ColorPicker({ name: "color", displayName: "Color", value: { value: "#252423" } });
    subtitleColor = new formattingSettings.ColorPicker({ name: "subtitleColor", displayName: "Subtitle color", value: { value: "#605E5C" } });

    name: string = "titleText";
    displayName: string = "Title";
    slices: Array<FormattingSettingsSlice> = [this.show, this.text, this.subtitle, this.fontSize, this.color, this.subtitleColor];
}

/** Icon left of the title/label. */
class IconCard extends FormattingSettingsCard {
    show = new formattingSettings.ToggleSwitch({ name: "show", displayName: "Show", value: true });
    iconName = new formattingSettings.ItemDropdown({
        name: "name",
        displayName: "Icon",
        items: [
            { displayName: "Chart", value: "chart" },
            { displayName: "Bar chart", value: "bar" },
            { displayName: "Pie", value: "pie" },
            { displayName: "Percent", value: "percent" },
            { displayName: "People", value: "people" },
            { displayName: "Map pin", value: "pin" },
            { displayName: "Shield", value: "shield" },
            { displayName: "Table", value: "table" },
            { displayName: "Box", value: "box" },
            { displayName: "Shield (Material)", value: "shield-m" },
            { displayName: "Location (Material)", value: "pin-m" },
            { displayName: "Map pin (Lucide)", value: "map-pin" },
            { displayName: "Map", value: "map" },
            { displayName: "Sigma (total)", value: "sigma" },
            { displayName: "Trending up", value: "trending-up" },
            { displayName: "Trending down", value: "trending-down" },
            { displayName: "Users", value: "users" },
            { displayName: "Layers", value: "layers" },
            { displayName: "Activity", value: "activity" },
            { displayName: "Bar chart (horizontal)", value: "chart-bar" },
            { displayName: "Column chart", value: "chart-column" },
            { displayName: "Pie chart", value: "chart-pie" }
        ],
        value: { displayName: "Chart", value: "chart" }
    });
    size = new formattingSettings.NumUpDown({ name: "size", displayName: "Size", value: 18 });
    color = new formattingSettings.ColorPicker({ name: "color", displayName: "Color", value: { value: "#4B8B3B" } });

    name: string = "icon";
    displayName: string = "Icon";
    slices: Array<FormattingSettingsSlice> = [this.show, this.iconName, this.size, this.color];
}

/** Card value + label typography. */
class ValueCard extends FormattingSettingsCard {
    label = new formattingSettings.TextInput({ name: "label", displayName: "Label", value: "", placeholder: "Label" });
    fontSize = new formattingSettings.NumUpDown({ name: "fontSize", displayName: "Value size", value: 30 });
    color = new formattingSettings.ColorPicker({ name: "color", displayName: "Value color", value: { value: "#252423" } });
    labelColor = new formattingSettings.ColorPicker({ name: "labelColor", displayName: "Label color", value: { value: "#252423" } });
    precision = new formattingSettings.NumUpDown({ name: "precision", displayName: "Decimals", value: 0 });

    name: string = "value";
    displayName: string = "Value (card)";
    slices: Array<FormattingSettingsSlice> = [this.label, this.fontSize, this.color, this.labelColor, this.precision];
}

/** Trend pill driven by Value vs Comparison. */
class PillCard extends FormattingSettingsCard {
    show = new formattingSettings.ToggleSwitch({ name: "show", displayName: "Show", value: false });
    goodColor = new formattingSettings.ColorPicker({ name: "goodColor", displayName: "Good color", value: { value: "#4B8B3B" } });
    badColor = new formattingSettings.ColorPicker({ name: "badColor", displayName: "Bad color", value: { value: "#D64550" } });
    invert = new formattingSettings.ToggleSwitch({ name: "invert", displayName: "Invert (down is good)", value: false });

    name: string = "pill";
    displayName: string = "Trend pill";
    slices: Array<FormattingSettingsSlice> = [this.show, this.goodColor, this.badColor, this.invert];
}

export class VisualFormattingSettingsModel extends FormattingSettingsModel {
    panelCard = new PanelCard();
    titleCard = new TitleCard();
    iconCard = new IconCard();
    valueCard = new ValueCard();
    pillCard = new PillCard();

    cards = [this.panelCard, this.titleCard, this.iconCard, this.valueCard, this.pillCard];
}
