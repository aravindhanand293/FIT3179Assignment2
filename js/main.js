// One shared look for every chart, so fonts and greys match the page.
const vegaTheme = {
  background: "transparent",
  padding: {"left": 0, "top": 5, "right": 5, "bottom": 5},
  font: "Source Sans 3",
  title: {
    font: "Bitter",
    fontWeight: 700,
    color: "#2b2620",
    subtitleFont: "Source Sans 3",
    subtitleColor: "#6b6257",
    anchor: "start"
  },
  axis: {
    labelFont: "Source Sans 3",
    titleFont: "Source Sans 3",
    labelColor: "#6b6257",
    titleColor: "#2b2620",
    labelFontSize: 12,
    titleFontSize: 12,
    titleFontWeight: 600,
    gridColor: "#e4ddd0",
    domainColor: "#b9ae9c",
    tickColor: "#b9ae9c"
  },
  legend: {
    labelFont: "Source Sans 3",
    titleFont: "Source Sans 3",
    labelColor: "#2b2620",
    titleColor: "#2b2620",
    labelFontSize: 12,
    titleFontSize: 12,
    titleLimit: 320,
    labelLimit: 320,
    gradientLength: 240
  },
  view: { stroke: null }
};

const options = { actions: false, renderer: "svg", config: vegaTheme };

// container id -> spec file
const charts = {
  linked_timeline: "specs/linked_timeline.vl.json",
  map_choropleth: "specs/map_choropleth.vl.json",
  map_bins_updated: "specs/map_bins_updated.vl.json",
  chart_waffle: "specs/chart_waffle.vl.json",
  map_symbols: "specs/map_symbols.vl.json",
  chart_lollipop: "specs/chart_lollipop.vl.json",
  chart_jitter_updated: "specs/chart_jitter_updated.vl.json",
  chart_connected_scatter: "specs/chart_connected_scatter.vl.json",
  chart_connected_dot_plot: "specs/chart_connected_dot_plot.vl.json",
  chart_diverging_bar_chart: "specs/chart_diverging_bar_chart.vl.json"
};

// Wait for the web fonts so the charts are measured with the right typeface.
document.fonts.ready.then(() => {
  for (const [id, spec] of Object.entries(charts)) {
    vegaEmbed("#" + id, spec, options).catch(console.error);
  }
});
