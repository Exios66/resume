-- Pandoc/Quarto filter: draws a chart from the table inside a `::: {.chart}` Div.
-- The table stays on the page after the chart as its accessible, printable source.
-- Design: .github/specs/2026-11-07-interactive-charts-design.md
-- Pure helpers live on the global CHARTS table so tests/test_charts.lua can load
-- this file without Pandoc.

CHARTS = {}
local M = CHARTS

local MINUS = "\u{2212}"

--- Every number in a cell, in order. Handles a Unicode minus, a leading plus,
-- thousands commas and decimals; ignores %, ×, $, words and other text.
-- @param text string Cell text.
-- @return table List of numbers (empty when the cell holds none).
function M.parse_numbers(text)
  local s = (text or ""):gsub(MINUS, "-")
  local out, pos = {}, 1
  while true do
    local a, b, digits = s:find("(%d[%d,]*%.?%d*)", pos)
    if not a then break end
    -- A comma that is not followed by exactly three digits separates two numbers.
    local first = digits:match("^(%d+[%.%d]*)") or digits
    local clean = digits
    if not digits:match("^%d%d?%d?,%d%d%d") then
      clean, b = first, a + #first - 1
    else
      clean = digits:match("^[%d,]+%.?%d*"):gsub(",", "")
      b = a + #digits:match("^[%d,]+%.?%d*") - 1
    end
    clean = clean:gsub("%.$", "")
    local n = tonumber(clean)
    local before = a > 1 and s:sub(a - 1, a - 1) or ""
    local before2 = a > 2 and s:sub(a - 2, a - 2) or ""
    if before == "-" and not before2:match("[%w]") then n = -n end
    out[#out + 1] = n
    pos = b + 1
  end
  return out
end

local function round(x, places)
  local m = 10 ^ (places or 10)
  return math.floor(x * m + 0.5) / m
end

--- Clean tick values (steps of 1, 2, 2.5 or 5 × 10^k) covering lo..hi.
-- @param lo number Smallest value to cover.
-- @param hi number Largest value to cover.
-- @param count integer Rough number of intervals wanted.
-- @return table Ascending tick values, both ends included.
function M.nice_ticks(lo, hi, count)
  if hi <= lo then hi = lo + 1 end
  local raw = (hi - lo) / (count or 5)
  local mag = 10 ^ math.floor(math.log(raw, 10))
  local step = mag * 10
  for _, f in ipairs({ 1, 2, 2.5, 5, 10 }) do
    if f * mag >= raw - 1e-12 then step = f * mag; break end
  end
  local start = math.floor(round(lo / step)) * step
  local stop = math.ceil(round(hi / step)) * step
  local ticks = {}
  for i = 0, math.floor(round((stop - start) / step)) do
    ticks[#ticks + 1] = round(start + i * step) + 0.0
  end
  return ticks
end

local function group_thousands(int)
  local s = int
  while true do
    local n
    s, n = s:gsub("^(%d+)(%d%d%d)", "%1,%2")
    if n == 0 then return s end
  end
end

--- Format a value for labels and tooltips.
-- @param n number Value.
-- @param unit string|nil Suffix such as " pts", "%" or "×".
-- @param signed boolean|nil Prefix positive values with "+".
-- @return string Text using a typographic minus for negatives.
function M.fmt(n, unit, signed)
  local body = string.format("%.10g", math.abs(n))
  local int, frac = body:match("^(%d+)(%.?%d*)$")
  if int then body = group_thousands(int) .. frac end
  local sign = ""
  if n < 0 then sign = MINUS elseif signed and n > 0 then sign = "+" end
  return sign .. body .. (unit or "")
end

-- ------------------------------------------------------------------ drawing

-- Light-theme paint written onto every shape, so a chart still reads if styles.css
-- fails to load. The stylesheet's classes override these for both themes.
local PAINT = { c1 = "#008b9a", c2 = "#4f5fc4", c1s = "#6cb2bb", grid = "#e2e8eb", muted = "#5b6970", paper = "#ffffff" }

local W = 640          -- viewBox width
local GUTTER = 190     -- left column for row labels
local RIGHT = 56       -- room for value labels after the plot
local BAND = 40        -- row height (also the hit-area height)
local BAR = 20         -- bar thickness (dataviz cap is 24)
local R = 5            -- dot radius (8px minimum diameter)

local function esc(s)
  return (tostring(s):gsub("&", "&amp;"):gsub("<", "&lt;"):gsub(">", "&gt;"):gsub('"', "&quot;"))
end

local function num(x) return (string.format("%.1f", x):gsub("%.0$", "")) end

--- Split a label into at most two lines of max_chars, at spaces.
-- @param text string Label.
-- @param max_chars integer Characters per line.
-- @return table One or two lines; the second ends in "…" if text was cut.
function M.wrap_label(text, max_chars)
  if utf8.len(text) <= max_chars then return { text } end
  local first, rest = "", text
  for word in text:gmatch("%S+") do
    local candidate = first == "" and word or (first .. " " .. word)
    if utf8.len(candidate) > max_chars then break end
    first = candidate
  end
  if first == "" then first = text:sub(1, utf8.offset(text, max_chars) - 1) end
  rest = text:sub(#first + 1):gsub("^%s+", "")
  if utf8.len(rest) > max_chars then
    rest = rest:sub(1, utf8.offset(rest, max_chars) - 1):gsub("%s+$", "") .. "…"
  end
  return { first, rest }
end

local function fail(spec, message)
  error("chart: " .. (spec.file or "page") .. ": " .. message, 0)
end

local function column(spec, rows, name)
  if rows[1][name] == nil then fail(spec, "column '" .. tostring(name) .. "' not found") end
end

local function values(spec, rows, name, mode)
  local out = {}
  for i, row in ipairs(rows) do
    local found = M.parse_numbers(row[name])
    if #found == 0 then fail(spec, "no number in column '" .. name .. "', row " .. i) end
    out[i] = mode == "all" and found or found[1]
  end
  return out
end

local function linear(lo, hi, x0, x1)
  return function(v) return x0 + (v - lo) / (hi - lo) * (x1 - x0) end
end

local function text(class, x, y, anchor, body, extra)
  return string.format('<text class="%s" x="%s" y="%s" text-anchor="%s"%s>%s</text>',
    class, num(x), num(y), anchor, extra or "", esc(body))
end

local function line(class, x1, y1, x2, y2, stroke)
  return string.format('<line class="%s" x1="%s" y1="%s" x2="%s" y2="%s" fill="none" stroke="%s"/>',
    class, num(x1), num(y1), num(x2), num(y2), stroke)
end

local function dot(color, cx, cy)
  return string.format('<circle class="dot %s" cx="%s" cy="%s" r="%d" fill="%s" stroke="%s" stroke-width="2"/>',
    color, num(cx), num(cy), R, PAINT[color], PAINT.paper)
end

local function hit(x, y, w, h)
  return string.format('<rect class="hit" x="%s" y="%s" width="%s" height="%s" fill="transparent" stroke="none"/>',
    num(x), num(y), num(w), num(h))
end

local function mark(tip_value, tip_label, body)
  return string.format('<g class="mark" tabindex="0" data-tip-value="%s" data-tip-label="%s">%s</g>',
    esc(tip_value), esc(tip_label), body)
end

-- Row label, right-aligned in the gutter, one or two lines centred on cy.
local function row_label(label, cy)
  local lines = M.wrap_label(label, 26)
  if #lines == 1 then return text("cat", GUTTER - 12, cy + 4.5, "end", lines[1]) end
  return text("cat", GUTTER - 12, cy - 3, "end", lines[1]) .. text("cat", GUTTER - 12, cy + 12, "end", lines[2])
end

-- Vertical gridlines and tick labels for a horizontal value axis.
local function x_axis(ticks, sx, top, bottom, unit)
  local out = {}
  for _, t in ipairs(ticks) do
    out[#out + 1] = line("grid", sx(t), top, sx(t), bottom, PAINT.grid)
    out[#out + 1] = text("tick", sx(t), bottom + 18, "middle", M.fmt(t, unit))
  end
  return table.concat(out)
end

-- Horizontal bar path from the baseline to the value: square at the baseline,
-- 4px rounded corners at the data end, for either direction.
local function bar_path(color, base, value_x, y)
  local r = math.min(4, math.abs(value_x - base))
  local d = value_x >= base and 1 or -1
  local e = value_x - d * r
  return string.format('<path class="bar %s" d="M%s %s H%s Q%s %s %s %s V%s Q%s %s %s %s H%s Z" fill="%s" stroke="none"/>',
    color, num(base), num(y), num(e), num(value_x), num(y), num(value_x), num(y + r),
    num(y + BAR - r), num(value_x), num(y + BAR), num(e), num(y + BAR), num(base), PAINT[color])
end

local function series_colors(spec, rows)
  local colors, order = {}, {}
  if not spec.series then return function() return "c1" end, order end
  column(spec, rows, spec.series)
  for _, row in ipairs(rows) do
    local s = row[spec.series]
    if not colors[s] then
      order[#order + 1] = s
      if #order > 2 then fail(spec, "at most two series") end
      colors[s] = #order == 1 and "c1" or "c2"
    end
  end
  return function(row) return colors[row[spec.series]] end, order
end

local function domain(spec, list, include_zero)
  local lo, hi = math.huge, -math.huge
  for _, v in ipairs(list) do lo, hi = math.min(lo, v), math.max(hi, v) end
  if include_zero then lo, hi = math.min(lo, 0), math.max(hi, 0) end
  if spec.ref then hi = math.max(hi, tonumber(spec.ref)) end
  lo = tonumber(spec.min) or lo
  hi = tonumber(spec.max) or hi
  local ticks = M.nice_ticks(lo, hi, 5)
  if spec.min then ticks[1] = lo end
  return ticks[1], ticks[#ticks], ticks
end

local DRAW = {}

function DRAW.bars(spec, rows)
  column(spec, rows, spec.label); column(spec, rows, spec.value)
  local vals = values(spec, rows, spec.value)
  local color_of, legend = series_colors(spec, rows)
  local lo, hi, ticks = domain(spec, vals, true)
  local top = spec.ref and 26 or 10
  local bottom = top + #rows * BAND
  local sx = linear(lo, hi, GUTTER, W - RIGHT)
  local out = { x_axis(ticks, sx, top, bottom, spec.unit) }
  if lo < 0 then out[#out + 1] = line("zero", sx(0), top, sx(0), bottom, PAINT.muted) end
  if spec.ref then
    local rx = sx(tonumber(spec.ref))
    out[#out + 1] = line("ref", rx, top - 6, rx, bottom, PAINT.muted)
    out[#out + 1] = text("ref-label", rx, top - 12, "end", spec["ref-label"] or M.fmt(tonumber(spec.ref), spec.unit))
  end
  local signed = spec.signed == "true"
  for i, row in ipairs(rows) do
    local y = top + (i - 1) * BAND
    local v, color = vals[i], color_of(row)
    local label = row[spec.label] .. (spec.series and (" · " .. row[spec.series]) or "")
    local value_text = M.fmt(v, spec.unit, signed)
    local vx = sx(v)
    local tip = v >= 0 and text("val", vx + 6, y + BAND / 2 + 4.5, "start", value_text)
      or text("val", vx - 6, y + BAND / 2 + 4.5, "end", value_text)
    out[#out + 1] = mark(value_text, label, hit(0, y, W, BAND) .. row_label(row[spec.label], y + BAND / 2)
      .. bar_path(color, sx(math.max(lo, 0)), vx, y + (BAND - BAR) / 2) .. tip)
  end
  return out, bottom + 28, legend, function(i) return i end
end

function DRAW.dumbbell(spec, rows)
  column(spec, rows, spec.label); column(spec, rows, spec.from); column(spec, rows, spec.to)
  local a, b = values(spec, rows, spec.from), values(spec, rows, spec.to)
  local all = {}
  for i = 1, #rows do all[#all + 1] = a[i]; all[#all + 1] = b[i] end
  local lo, hi, ticks = domain(spec, all, false)
  local top, bottom = 10, 10 + #rows * BAND
  local sx = linear(lo, hi, GUTTER, W - RIGHT)
  local out = { x_axis(ticks, sx, top, bottom, spec.unit) }
  for i, row in ipairs(rows) do
    local y = top + (i - 1) * BAND
    local cy = y + BAND / 2
    local fx, tx = sx(a[i]), sx(b[i])
    out[#out + 1] = mark(M.fmt(a[i], spec.unit) .. " → " .. M.fmt(b[i], spec.unit), row[spec.label],
      hit(0, y, W, BAND) .. row_label(row[spec.label], cy)
      .. line("link", fx, cy, tx, cy, PAINT.muted) .. dot("c1s", fx, cy) .. dot("c1", tx, cy)
      .. text("val", math.max(fx, tx) + 10, cy + 4.5, "start", M.fmt(b[i], spec.unit)))
  end
  return out, bottom + 28, { spec["from-name"] or spec.from, spec["to-name"] or spec.to }, nil
end

function DRAW.step(spec, rows)
  column(spec, rows, spec.label); column(spec, rows, spec.value)
  local xs, ys = values(spec, rows, spec.label), values(spec, rows, spec.value)
  local lo, hi, ticks = domain(spec, ys, false)
  local left, top, bottom = 56, 30, 230
  local l2 = function(v) return math.log(v, 2) end
  local sx = linear(l2(xs[1]), l2(xs[#xs]), left + 24, W - RIGHT)
  local sy = linear(lo, hi, bottom, top)
  local out = { text("axis-note", left - 44, 14, "start",
    (spec["axis-label"] or spec.value) .. " (axis starts at " .. M.fmt(lo, spec.unit) .. ")") }
  for _, t in ipairs(ticks) do
    out[#out + 1] = line("grid", left, sy(t), W - RIGHT + 16, sy(t), PAINT.grid)
    out[#out + 1] = text("tick", left - 8, sy(t) + 4.5, "end", M.fmt(t, spec.unit))
  end
  local d = {}
  for i = 1, #xs do
    d[#d + 1] = (i == 1 and "M" or ("H" .. num(sx(l2(xs[i]))) .. " V")) .. (i == 1 and (num(sx(l2(xs[i]))) .. " ") or "") .. num(sy(ys[i]))
  end
  out[#out + 1] = string.format('<path class="line c1" d="%s" fill="none" stroke="%s" stroke-width="2"/>',
    table.concat(d, " "), PAINT.c1)
  local gap = (sx(l2(xs[#xs])) - sx(l2(xs[1]))) / (#xs - 1)
  for i, row in ipairs(rows) do
    local x = sx(l2(xs[i]))
    local short = xs[i] >= 1024 and (M.fmt(xs[i] / 1024) .. "K") or M.fmt(xs[i])
    local body = hit(x - math.max(24, gap / 2) / 2 - gap / 4, top, math.max(24, gap / 2) + gap / 2, bottom - top)
      .. dot("c1", x, sy(ys[i])) .. text("tick", x, bottom + 18, "middle", short)
    if i == #rows then body = body .. text("val", x, sy(ys[i]) - 12, "middle", M.fmt(ys[i], spec.unit)) end
    out[#out + 1] = mark(M.fmt(ys[i], spec.unit), row[spec.label] .. " tokens", body)
  end
  return out, bottom + 30, {}, nil
end

function DRAW.strip(spec, rows)
  column(spec, rows, spec.label); column(spec, rows, spec.from); column(spec, rows, spec.to)
  local a = values(spec, rows, spec.from, spec["from-mode"])
  local b = values(spec, rows, spec.to, spec["to-mode"])
  local out, PANEL = {}, 72
  local from_name, to_name = spec["from-name"] or spec.from, spec["to-name"] or spec.to
  for i, row in ipairs(rows) do
    local y = 8 + (i - 1) * PANEL
    local cy = y + 18
    local list = { a[i] }
    for _, v in ipairs(type(b[i]) == "table" and b[i] or { b[i] }) do list[#list + 1] = v end
    local maxv = 0
    for _, v in ipairs(list) do maxv = math.max(maxv, v) end
    local ticks = M.nice_ticks(0, maxv, 4)
    local sx = linear(0, ticks[#ticks], GUTTER, W - RIGHT)
    local panel = { row_label(row[spec.label], cy), x_axis(ticks, sx, y + 2, y + 34, nil) }
    for j, v in ipairs(list) do
      local color, who = j == 1 and "c2" or "c1", j == 1 and from_name or to_name
      panel[#panel + 1] = mark(M.fmt(v, spec.unit), row[spec.label] .. " · " .. who,
        hit(sx(v) - 12, cy - 12, 24, 24) .. dot(color, sx(v), cy))
    end
    out[#out + 1] = '<g class="panel">' .. table.concat(panel) .. "</g>"
  end
  return out, 8 + #rows * PANEL, { to_name, from_name }, nil
end

local function summary(spec, rows)
  if spec.summary then return spec.summary end
  local parts = {}
  for _, row in ipairs(rows) do
    local cells = {}
    for _, key in ipairs({ spec.value, spec.from, spec.to }) do
      if key and row[key] then cells[#cells + 1] = row[key] end
    end
    parts[#parts + 1] = row[spec.label] .. " " .. table.concat(cells, " to ")
  end
  return (spec.title or "Chart") .. ": " .. table.concat(parts, "; ") .. ". Full values in the table below."
end

--- Render one chart as an HTML figure holding an inline SVG.
-- @param spec table Div attributes (kind, title, label, value, from, to, series, …).
-- @param rows table List of rows, each mapping header text to cell text.
-- @return string HTML for the figure.
function M.render(spec, rows)
  local draw = DRAW[spec.kind or ""]
  if not draw then fail(spec, "unknown kind '" .. tostring(spec.kind) .. "'") end
  if #rows < 2 then fail(spec, "needs at least two rows") end
  local body, height, legend = draw(spec, rows)
  local keys = { "c1", "c2" }
  if spec.kind == "dumbbell" then keys = { "c1s", "c1" } end
  local legend_html = ""
  if #legend >= 2 then
    local items = {}
    for i, name in ipairs(legend) do
      items[i] = string.format('<li><span class="key %s"></span>%s</li>', keys[i], esc(name))
    end
    legend_html = '<ul class="chart-legend">' .. table.concat(items) .. "</ul>"
  end
  return string.format('<figure class="chart chart-%s"><figcaption class="chart-title">%s</figcaption>%s'
    .. '<div class="chart-body" tabindex="0" role="group" aria-label="%s">'
    .. '<svg viewBox="0 0 %d %s" width="%d" height="%s" role="img" aria-label="%s">%s</svg></div></figure>',
    spec.kind, esc(spec.title or ""), legend_html, esc((spec.title or "Chart") .. ", scrollable"),
    W, num(height), W, num(height), esc(summary(spec, rows)), table.concat(body))
end

-- ------------------------------------------------------------------- filter

local function has_class(el, name)
  for _, c in ipairs(el.classes or {}) do if c == name then return true end end
  return false
end

local function cells_text(row)
  local out = {}
  for i, c in ipairs(row.cells) do out[i] = pandoc.utils.stringify(c.contents) end
  return out
end

--- Replace a `.chart` Div with the chart figure followed by its table.
function Div(el)
  if not has_class(el, "chart") then return nil end
  local spec = {}
  for k, v in pairs(el.attributes) do spec[k] = v end
  spec.file = quarto and quarto.doc and quarto.doc.input_file or nil
  local tbl
  for _, block in ipairs(el.content) do
    if block.t == "Table" or block.tag == "Table" then tbl = block; break end
  end
  if not tbl then fail(spec, "a .chart block needs a table") end
  local headers = cells_text(tbl.head.rows[1])
  local rows = {}
  for _, body in ipairs(tbl.bodies) do
    for _, r in ipairs(body.body) do
      local cells, row = cells_text(r), {}
      for j, h in ipairs(headers) do row[h] = cells[j] end
      rows[#rows + 1] = row
    end
  end
  return { pandoc.RawBlock("html", M.render(spec, rows)), tbl }
end
