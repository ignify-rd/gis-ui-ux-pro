# Research: web GIS / GIS dashboard UI-UX rules

Date: 2026-11-14. Each rule lists: ID | name | Do | Don't | Why | severity | source.

**[synth]** marks rules synthesized from several sources rather than stated by one. Verify these before quoting any number.

**Unverified items:**
- OSMF's 500px exemption
- MapLibre's default control positions
- GeoJSON size thresholds in MB
- any numeric maximum on the number of layers

## 1. Layout (L)
- **L01 Full vs partial map by task.** Full-map layouts suit exploration; map + side panel suits task-funneled workflows. Don't default to one layout without thinking about the task. Severity: high. [Esri Canada](https://resources.esri.ca/education-and-research/choosing-the-right-arcgis-app-builder-a-ux-ui-design-perspective-part-1)
- **L02 Primary panel on the reading-start side.** Left panel for LTR, mirrored for RTL. Severity: medium. Source: same as L01.
- **L03 Shell layout.** Header + action bar (icon rail) opening collapsible panels + map in the content area. Don't stack always-open widgets over the map. Severity: high. Sources: [Calcite mapping app](https://developers.arcgis.com/calcite-design-system/tutorials/create-a-mapping-app), [JS layouts](https://developers.arcgis.com/javascript/latest/creating-app-layouts/)
- **L04 Action bar overflow.** The action bar collapses into a "more" menu when the screen is short; don't clip tools silently. Severity: medium. [Calcite adaptive grid](https://developers.arcgis.com/calcite-design-system/sample-code/app-adaptive-grid/)
- **L05 Size elements by importance.** The most critical element (the map or the headline KPI) is the largest; avoid a uniform tile grid. Severity: high. [Esri effective dashboards](https://doc.arcgis.com/en/dashboards/latest/reference/author-effective-dashboards.htm)
- **L06 Group related elements.** Keep the legend next to the map and details next to the list. Severity: high. Source: same as L05.
- **L07 Audience and display target first.** Test on the real display (a wall screen vs a laptop). Severity: high. Source: same as L05.
- **L08 Only what users need.** Leave out nice-to-have charts; clutter also slows the app. Severity: high. Source: same as L05.
- **L09 Mobile layout.** Below 768px, put the map on top (about 70vh) and a bottom sheet (30vh or less) underneath, with touch-sized controls. Don't squeeze a side panel next to the map. Severity: high. Sources: [CodePen](https://codepen.io/Rachael-E/pen/wvVXBpo), [Experience Builder mobile](https://developers.arcgis.com/documentation/app-builders/low-code/arcgis-experience-builder/build-mobile-solutions/)
- **L10 Short title and an about panel.** Explain the app's purpose and data briefly. Severity: medium. [Esri mobile apps](https://www.esri.com/arcgis-blog/products/configurable-apps/sharing-collaboration/configure-apps-with-mobile-in-mind)
- **L11 Z-order [synth].** From bottom to top: basemap, thematic, reference labels/boundaries, selection highlight, controls, panels, popups, modals/toasts. Attribution stays uncovered. Severity: high. Sources: [Esri cartography principles](https://www.esri.com/arcgis-blog/products/arcgis-pro/mapping/primary-design-principles-for-cartography), [Mapbox attribution](https://docs.mapbox.com/help/dive-deeper/attribution/)
- **L12 Map-first vs data-first [synth].** Use map-first when the question is "where?". Use list-first for lookup tasks, with the list sorted by distance or time. Severity: medium. [Google store locator](https://developers.google.com/maps/solutions/store-locator/best-practices)

## 2. Map controls (C)
- **C01 Attribution always visible.** It must be visible without any interaction; it may collapse only after it has been shown. Never hide it behind an "i" on load. Severity: critical. [OSMF](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines)
- **C02 Mapbox logo and text.** Keep both on the map (default: logo bottom-left, text bottom-right). The logo may not be restyled. Severity: critical. [Mapbox](https://docs.mapbox.com/help/dive-deeper/attribution/)
- **C03 Attribution in Leaflet/OpenLayers.** Add it manually; these libraries don't add Mapbox attribution automatically. Severity: critical. Source: same as C02.
- **C04 Corner conventions [synth].** Zoom/compass/geolocate/fullscreen stacked top-right, scale bar bottom-left, attribution at the bottom, search top-left or in the header. Severity: medium. Sources: [AWS Location](https://docs.aws.amazon.com/location/latest/developerguide/how-to-add-control-on-map.html), [Mapbox example](https://docs.mapbox.com/mapbox-gl-js/example/attribution-position/)
- **C05 Compass only if the map can rotate.** Clicking it resets to north. Severity: low. Source: AWS (C04).
- **C06 Scale bar with locale units.** Use metric or imperial to match the locale; never show a fixed "1:50,000" ratio on a web map. Severity: medium. Source: AWS (C04).
- **C07 Geolocate states.** Show off / locating / tracking / error. Ask for permission on tap, not on page load. Severity: medium. Source: AWS (C04).
- **C08 Keyboard shortcuts help.** A help control placed before the map in focus order. Severity: medium. [leaflet.a11y](https://github.com/nfreear/leaflet.a11y)
- **C09 Search or coordinate input as a drag alternative.** Severity: high. [WCAG 2.5.7](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements)
- **C10 Measure/draw tools.** Show area and length live; the geometry must be editable and exportable. Severity: medium. [Planet Explorer](https://developers.planet.com/tag/explorer3.html)
- **C11 Basemap switcher [synth].** 2–4 thumbnails. Re-check overlay contrast on each basemap. Severity: medium. [CARTO](https://carto.com/carto-colors/)

## 3. Layers (Y)
- **Y01 Only purposeful layers.** Turn non-essential layers off by default. Severity: high. [Esri web map checklist](https://www.esri.com/arcgis-blog/products/mapping/mapping/intelligent-maps-checklist-web-maps)
- **Y02 Set min/max visible scale on every layer.** Severity: high. Source: same as Y01.
- **Y03 Grey out layers outside their visible scale [synth].** Offer "zoom to visible". Severity: medium. Source: same as Y01.
- **Y04 Human-readable layer titles and field aliases.** Hide OBJECTID and coded values. Severity: high. Source: same as Y01.
- **Y05 Layer order.** Basemap, then thematic, then reference lines/labels on top. Raster goes under vector. Severity: high. [Esri cartography](https://www.esri.com/arcgis-blog/products/arcgis-pro/mapping/primary-design-principles-for-cartography)
- **Y06 Per-layer opacity slider.** Especially for rasters. Severity: medium. [Copernicus Browser](https://documentation.dataspace.copernicus.eu/Applications/Browser.html)
- **Y07 Grouping [synth].** Collapsible theme groups. Mutually exclusive rasters use radio buttons, never two opaque rasters at once. Avoid a flat list of more than 15 checkboxes. Severity: medium. Source: same as Y01.

## 4. Symbology & legend (S)
- **S01 Normalize choropleths.** Map rates, never raw counts. Severity: critical. [Axis Maps](https://axismaps.com/guide/choropleth)
- **S02 Totals as proportional symbols or dot density.** Severity: high. [Axis Maps](https://axismaps.com/guide/proportional-symbols)
- **S03 Dot density needs an equal-area projection.** Severity: high. [Axis Maps](https://axismaps.com/guide/dot-density)
- **S04 Number of classes.** Sequential 3–7 (CARTO caps at 7, ColorBrewer at 9); diverging at most 11; qualitative at most 8–12. Severity: high. Sources: [CARTOframes](https://cartoframes.readthedocs.io/en/v0.9.2/styling.html), [ArcUser](https://www.esri.com/about/newsroom/arcuser/better-breaks-define-your-maps-purpose)
- **S05 Classification method.**
  - Jenks for clustered data on a single map.
  - Quantile for rankings or evenly spread data.
  - Equal interval for familiar ranges.
  - Fixed breaks when maps must be compared.

  Severity: high. [Esri classification](https://doc.esri.com/en/arcgis-pro/latest/help/mapping/layer-properties/data-classification-methods.html)
- **S06 Ramp type matches the data.** Sequential for ordered values; diverging only when there is a meaningful midpoint; qualitative for categories. Severity: high. [CARTO](https://carto.com/carto-colors/)
- **S07 Lightness direction follows the basemap.** On a light basemap dark = high; on a dark basemap bright = high. Severity: high. Sources: CARTO, [Carbon](https://carbondesignsystem.com/data-visualization/color-palettes/)
- **S08 No rainbow or jet ramps for continuous data.** Severity: high. [NASA Earth Observatory](https://earthobservatory.nasa.gov/blogs/elegantfigures/2013/08/12/subtleties-of-color-part-3-of-6/)
- **S09 Colorblind-safe palettes.** Use ColorBrewer CB-safe or CARTO Safe; never encode meaning with red–green alone. Severity: critical. Sources: CARTO, NASA.
- **S10 Muted basemap, strong data.** Severity: high. Sources: [Mapbox guide](https://go.mapbox.com/rs/117-NXK-490/images/the-guide-to-map-design.pdf), [Esri muted imagery](https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/mapping/imagery-basemap-ready-for-data)
- **S11 Reveal detail progressively by zoom.** Severity: medium. Source: Mapbox guide.
- **S12 Use color only for data differences.** Severity: medium. Sources: [Esri dashboards](https://enterprise.arcgis.com/en/dashboards/11.0/reference/author-effective-dashboards.htm), [OCHA checklist](https://humanitarian.atlassian.net/wiki/download/attachments/42047091/humanitarian_snapshot_quality_control_checklist.pdf?api=v2)
- **S13 Minimal legend.** Single column for a ramp, units labeled, no entries for hidden layers; drop the legend if direct labels are enough. Severity: medium. [Esri legend tips](https://www.esri.com/arcgis-blog/products/product/mapping/tips-for-legend-design)
- **S14 Legend reflects what is drawn [synth].** Only visible, in-scale layers and the current filter. Severity: medium. [Esri storymaps legends](https://www.esri.com/arcgis-blog/products/arcgis-storymaps/constituent-engagement/legends-for-storytelling-part-1-optimizing-the-basics)
- **S15 Heatmap vs choropleth.** Heatmaps show event intensity; choropleths show rates per unit. Never ask users to read values off a heatmap. Severity: medium. [CARTO map types](https://carto.com/blog/popular-thematic-map-types-techniques-spatial-data)
- **S16 Cluster dense points at low zoom.** Clusters show a count; set clusterMaxZoom. Severity: high. Sources: [Mapbox large GeoJSON](https://docs.mapbox.com/help/troubleshooting/working-with-large-geojson-data/), [Google clustering](https://developers.google.com/maps/documentation/javascript/marker-clustering)
- **S17 Cluster popups summarize.** Show count, dominant category, and browse / zoom-to actions. Severity: medium. [ArcGIS cluster popups](https://developers.arcgis.com/javascript/latest/api-reference/esri-smartMapping-popup-clusters.html)

## 5. Interaction (I)
- **I01 Roth's interaction operators.** Pan, zoom, filter, search, retrieve, overlay, resymbolize, reexpress, sequence, arrange, calculate, reproject. Severity: medium. [Roth 2013](https://geography.wisc.edu/cartography/projects/publications/Roth_2013_TVCG.pdf)
- **I02 Hover highlights, click opens details.** Hover changes feature-state and the cursor; a full popup opens only on click. Severity: high. [Mapbox hover](https://docs.mapbox.com/mapbox-gl-js/example/hover-styles/)
- **I03 Clear the previous highlight.** Severity: medium. Source: same as I02.
- **I04 Curated popup fields.** Aliases and formatted values, title first; never dump every attribute. Severity: high. Source: Esri checklist (Y01).
- **I05 Linked brushing across map, chart and table [synth].** One shared selection state and one highlight color. Severity: high. Sources: Esri dashboards, Roth.
- **I06 flyTo.** Defaults speed 1.2 and curve 1.42; set maxDuration; respect prefers-reduced-motion (skipped unless `essential`). Severity: medium. [Mapbox API](https://docs.mapbox.com/mapbox-gl-js/api/properties/)
- **I07 Locator results list.** Name, distance, hours and Directions, kept in sync with the markers. Severity: medium. Source: Google locator (L12).
- **I08 URL holds the view state [synth].** Center, zoom, layers, time and selection. Severity: medium. [NASA Worldview embed](https://www.earthdata.nasa.gov/learn/tutorials/embedded-worldview-examples)
- **I09 Show active filters [synth].** Filter chips plus "N of M features shown". Severity: high. [ArcGIS cluster filter](https://developers.arcgis.com/javascript/latest/sample-code/featurereduction-cluster-filter/)

## 6. Temporal (T)
- **T01 Compare modes.** Swipe (default), opacity fade, spy lens. Severity: high. [Worldview compare](https://www.earthdata.nasa.gov/news/blog/introducing-worldviews-comparison-feature)
- **T02 Label the A/B dates on both halves.** Severity: high. Source: same as T01.
- **T03 Swipe controls.** Add swap and orientation controls; remember the legend may not apply to both sides. Severity: medium. [Experience Builder swipe](https://doc.arcgis.com/en/experience-builder/latest/configure-widgets/swipe-widget.htm)
- **T04 Time slider.** Explicit stops, instant or window mode, configurable rate and loop; pause playback while the view is loading. Severity: medium. [ArcGIS TimeSlider](https://developers.arcgis.com/javascript/latest/api-reference/esri-widgets-TimeSlider.html)
- **T05 Timelapse export.** Choose range, fps and frequency; export GIF or MP4; say which visualization is being animated. Severity: low. [cop4schools](https://cop4schools.readthedocs.io/en/latest/part4/4_1.html)
- **T06 Cloud cover filter.** Default max 30% (as in Copernicus Browser for S2 L2A), adjustable. Severity: high. [Copernicus Browser](https://documentation.dataspace.copernicus.eu/Applications/Browser.html)
- **T07 Disclose that cloud % is per scene, not per AOI.** Or compute it for the AOI. Severity: high. [EO Browser guide](https://www.sentinel-hub.com/explore/eobrowser/user-guide/)
- **T08 Date picker marks acquisition dates [synth].** Grey out dates with no data. Severity: medium. Source: EO Browser guide.
- **T09 Time series flag or remove cloudy observations.** Severity: high. [Sentinel Hub multi-year](https://medium.com/sentinel-hub/multi-year-time-series-of-multi-spectral-data-viewed-and-analyzed-in-sentinel-hub-5628ec4fad9c)

## 7. Dashboard widgets (D)
- **D01 A few KPIs, each with a reference value and units.** Severity: high. Source: Esri dashboards.
- **D02 Show data freshness ("last updated").** Align refresh with the layer refresh. Severity: high. [Esri bug 000147531](https://support.esri.com/en-us/bug/the-indicator-widget-in-arcgis-dashboards-does-not-refl-bug-000147531)
- **D03 Pre-aggregate at the source and load only the needed fields.** Severity: high. [Esri slides](https://www.esri.com/content/dam/esrisites/en-us/media/powerpoints/design-impactful-arcgis-dashboards-with-best-practices.pdf)
- **D04 Prefer attribute filters over extent filters on high-traffic dashboards.** Severity: medium. [Esri dev summit](https://www.esri.com/content/dam/esrisites/en-us/events/conferences/2021/developer-summit/12527-arcgis-dashboards-tips-and-tricks.pdf)
- **D05 Limit relative-date filters at scale.** Severity: low. [Esri scalable](https://doc.arcgis.com/en/dashboards/latest/reference/build-highly-scalable-dashboards.htm)
- **D06 One categorical palette shared by map and charts.** Severity: high. Source: Carbon.
- **D07 Label chart series directly.** Severity: low. [Carbon anatomy](https://carbondesignsystem.com/data-visualization/chart-anatomy/)
- **D08 Encode uncertainty.** A VSUP or a separate confidence channel. Severity: high. [VSUP CHI 2018](https://www.tableau.com/research/publications/value-suppressing-uncertainty-palettes)
- **D09 Alert list ↔ map [synth].** Sort by severity and time; clicking zooms and highlights; the list scrolls to the selected item. Severity: high. Source: Esri dashboards.

## 8. Earth observation (E)
- **E01 Name composites by purpose.** For example "True color", "False color (vegetation)", "NDVI"; never show bare band strings. Severity: high. Source: EO Browser guide.
- **E02 S2 true color is B04/B03/B02.** Label every other combination "false color". Severity: medium. [gis4schools](https://gis4schools.readthedocs.io/en/latest/part3/rs_satelliteimages.html)
- **E03 Fixed index domains [synth].** NDVI/NDWI use −1..1 with a ticked legend; never auto-stretch per scene. Severity: high. Source: NASA EO.
- **E04 SAR in dB.** Composite VV, VH, VV−VH; explain that water is dark and urban is bright. Severity: medium. Sources: [ArcGIS SAR flood](https://pro.arcgis.com/en/pro-app/latest/help/analysis/image-analyst/interpret-sar-data-for-flood-mapping.htm), [SH custom script](https://custom-scripts.sentinel-hub.com/sentinel-1/sar_false_color_visualization)
- **E05 Scene cards.** Thumbnail, date, AOI coverage %, resolution, sensor, cloud %. Severity: high. [Planet Explorer filters](https://support.planet.com/hc/en-us/articles/212642197-Search-Criteria-and-Filters-in-Planet-Explorer)
- **E06 AOI coverage filter.** Show the footprint on hover. Severity: medium. [Planet ArcGIS](https://developers.planet.com/docs/integrations/arcgis/v1/search)
- **E07 Mute imagery under detections.** Severity: medium. [Esri highlight effects](https://www.esri.com/arcgis-blog/products/arcgis-online/mapping/highlighting-areas-effects)
- **E08 Show AI detection confidence [synth].** In the popup and the list, with a threshold slider, and as a visual encoding (opacity or dash). Severity: high. Source: VSUP.

## 9. Performance (P)
- **P01 Large data → vector tiles.** MTS, PMTiles or MVT. Severity: high. Source: Mapbox large GeoJSON.
- **P02 Slim GeoJSON.** At most 6 decimals, only the needed properties, loaded by URL, source maxzoom below 18. Severity: high. Source: same as P01.
- **P03 Clustering with supercluster.** Severity: high; stop using per-point DOM markers beyond a few hundred points. [Supercluster](https://blog.mapbox.com/clustering-millions-of-points-on-a-map-with-supercluster-272046ec5c97)
- **P04 Feedback by response time.**
  - Under 0.1 s: show nothing.
  - Around 1 s: a subtle indicator.
  - 2–10 s: a spinner or skeleton.
  - Over 10 s: a percent bar.

  Severity: medium. [uxtigers](https://www.uxtigers.com/post/progress-indicators)
- **P05 Skeletons for panels; a thin bar or fade-in for the map [synth].** Severity: low. [Carbon loading](https://carbondesignsystem.com/patterns/loading-pattern)
- **P06 Per-layer error state with retry [synth].** Other layers keep working. Severity: high.
- **P07 Scale-dependent rendering and simplification.** Severity: medium.

## 10. Accessibility (A)
- **A01 Text alternative.** A summary plus a feature table or list (WCAG 1.1.1). Severity: critical. [SitePen](https://sitepen.com/blog/navigating-accessibility-in-two-dimensions)
- **A02 Keyboard-operable map and features.** Arrow keys pan, +/− zoom, Enter opens. Severity: critical. [Leaflet a11y](https://leafletjs.com/examples/accessibility/)
- **A03 No keyboard trap; add a skip link before the map.** Severity: critical. [WCAG checklist](https://gisyaliny.github.io/webgis/docs/General/WCAG_2_1_AA_Developer_Checklist.html)
- **A04 Visible focus and logical order.** Skip link, search, controls, map, panels. Severity: high. [Esri a11y slides](https://jimmieego.github.io/2019-uc-a11y-slides)
- **A05 Non-drag alternatives.** Pan, swipe and the time slider all need one (WCAG 2.5.7). Severity: high.
- **A06 Contrast.** Text at least 4.5:1; symbols and outlines at least 3:1 (1.4.11). Severity: high. [NSGIC](https://nsgic.org/wp-content/uploads/2025/10/Making-GIS-Data-Accessible-and-ADA-Compliant.pdf)
- **A07 Never use color alone.** Add an icon, pattern or label (1.4.1). Severity: critical. [BOIA](https://boia.org/blog/interactive-maps-and-accessibility-4-tips)
- **A08 Accessible names on markers; make decorative maps inert.** Severity: high. Source: Leaflet a11y.
- **A09 prefers-reduced-motion.** Disables flyTo, autoplay and pulsing. Severity: medium. Source: Mapbox API.
- **A10 Focus management for popups [synth].** Move focus in, announce, and return focus on close. Severity: high.
- **A11 Touch targets at least 44px on mobile (24px is the WCAG minimum).** Severity: medium. Source: Experience Builder mobile.

## Follow-up sources not yet read
- [OCHA stylebook maps](https://humanitarian.atlassian.net/wiki/download/attachments/2209349672/OCHA+Graphics+Stylebook_Maps+%28002%29.pdf?version=1)
- [Roth 2012](https://geography.wisc.edu/cartography/projects/publications/Roth_2012_CJ.pdf)
- [Usability heuristics for web maps](https://ica-proc.copernicus.org/articles/4/70/2021/ica-proc-4-70-2021.pdf)
