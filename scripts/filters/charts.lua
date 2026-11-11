-- Pandoc/Quarto filter: draws a chart from the table inside a `::: {.chart}` Div.
-- The table stays on the page after the chart as its accessible, printable source.
-- Design: .github/specs/2026-11-07-interactive-charts-design.md
-- Pure helpers live on the global CHARTS table so tests/lua/test_charts.lua can load
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
    -- A decimal point with no digit before it (".5", "−.5") belongs to the number.
    if a > 1 and s:sub(a - 1, a - 1) == "." and not (a > 2 and s:sub(a - 2, a - 2):match("%d")) then
      local frac = s:match("^%d+", a)
      local before = a > 2 and s:sub(a - 2, a - 2) or ""
      local before2 = a > 3 and s:sub(a - 3, a - 3) or ""
      local n = tonumber("0." .. frac)
      if before == "-" and not before2:match("[%w]") then n = -n end
      out[#out + 1] = n
      pos = a + #frac
      goto continue
    end
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
    ::continue::
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
-- @param unit string|nil Suffix such as "pts", "%" or "×".
-- @param signed boolean|nil Prefix positive values with "+".
-- @return string Text using a typographic minus for negatives.
function M.fmt(n, unit, signed)
  local body = string.format("%.10g", math.abs(n))
  local int, frac = body:match("^(%d+)(%.?%d*)$")
  if int then body = group_thousands(int) .. frac end
  local sign = ""
  if n < 0 then sign = MINUS elseif signed and n > 0 then sign = "+" end
  unit = unit or ""
  -- Word units ("pts", "M") get a space; symbols ("%", "×") stay attached. Pandoc
  -- cannot parse a fenced-div attribute that starts with a space, so pages write "pts".
  if unit:match("^%a") then unit = " " .. unit end
  return sign .. body .. unit
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
local LABEL_ROOM = 64  -- plot inset that keeps a value label left of the data clear of row labels

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

-- One datum: focusable, named for screen readers, and carrying its tooltip text.
local function mark(tip_value, tip_label, body, row_index)
  return string.format('<g class="mark" tabindex="0" role="img" aria-label="%s" data-tip-value="%s" data-tip-label="%s" data-source-row="%d">%s</g>',
    esc(tip_label .. ": " .. tip_value), esc(tip_value), esc(tip_label), row_index, body)
end

--- Return SVG text for a row label, right-aligned in the gutter and centered on cy.
-- Labels wrap to at most two lines. The gutter defaults to GUTTER when omitted;
-- cy and gutter are in SVG viewBox units.
local function row_label(label, cy, gutter)
  gutter = gutter or GUTTER
  local lines = M.wrap_label(label, 26)
  if #lines == 1 then return text("cat", gutter - 12, cy + 4.5, "end", lines[1]) end
  return text("cat", gutter - 12, cy - 3, "end", lines[1]) .. text("cat", gutter - 12, cy + 12, "end", lines[2])
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
  if spec.max then
    while #ticks > 1 and ticks[#ticks] > hi + 1e-9 do ticks[#ticks] = nil end
    if ticks[#ticks] < hi - 1e-9 then ticks[#ticks + 1] = hi end
  end
  return ticks[1], ticks[#ticks], ticks
end

local DRAW = {}

--- Draw horizontal bars and their labels from the selected table columns.
-- @param spec table Chart attributes, including label and value column names;
--   optional series, min, max, ref, ref-label, unit and signed control the display.
-- @param rows table Rows mapping column names to cell text.
-- @return table, number, table, function SVG fragments, height in viewBox units,
--   legend names in series order, and an identity function for row indices.
-- Raises an error for missing columns or numeric values, more than two series,
-- or a positive minimum. Other errors from invalid attributes propagate.
function DRAW.bars(spec, rows)
  local width = tonumber(spec["plot-width"]) or W
  column(spec, rows, spec.label); column(spec, rows, spec.value)
  local vals = values(spec, rows, spec.value)
  local color_of, legend = series_colors(spec, rows)
  if tonumber(spec.min) and tonumber(spec.min) > 0 then
    fail(spec, "a bar chart must start at zero (min=\"" .. spec.min .. "\")")
  end
  local lo, hi, ticks = domain(spec, vals, true)
  local top = spec.ref and 26 or 10
  local bottom = top + #rows * BAND
  -- Short category names should not spend 190px on an empty label gutter.
  -- Keep the wider default for long labels; give short ones room without pushing
  -- the zero line and every positive bar off the initial phone viewport.
  local longest = 0
  for _, row in ipairs(rows) do longest = math.max(longest, utf8.len(row[spec.label])) end
  local gutter = math.min(GUTTER, math.max(100, longest * 9 + 32))
  local sx = linear(lo, hi, gutter + (lo < 0 and LABEL_ROOM or 0), width - RIGHT)
  local out = { x_axis(ticks, sx, top, bottom, spec.unit) }
  if lo < 0 then out[#out + 1] = line("zero", sx(0), top, sx(0), bottom, PAINT.muted) end
  local signed = spec.signed == "true"
  if spec.ref then
    -- Draw the reference line in segments, leaving a gap at any row whose value
    -- label it would cross (the label's halo is too thin to hide a line).
    local rx = sx(tonumber(spec.ref))
    local y0 = top - 6
    for i, v in ipairs(vals) do
      local width = utf8.len(M.fmt(v, spec.unit, signed)) * 7.5
      local vx = sx(v)
      local l0, l1 = v >= 0 and vx + 6 or vx - 6 - width, v >= 0 and vx + 6 + width or vx - 6
      if rx >= l0 - 3 and rx <= l1 + 3 then
        local y = top + (i - 1) * BAND
        if y + 8 > y0 then out[#out + 1] = line("ref", rx, y0, rx, y + 8, PAINT.muted) end
        y0 = y + BAND - 8
      end
    end
    out[#out + 1] = line("ref", rx, y0, rx, bottom, PAINT.muted)
    out[#out + 1] = text("ref-label", rx, top - 12, "end", spec["ref-label"] or M.fmt(tonumber(spec.ref), spec.unit))
  end
  for i, row in ipairs(rows) do
    local y = top + (i - 1) * BAND
    local v, color = vals[i], color_of(row)
    local label = row[spec.label] .. (spec.series and (" · " .. row[spec.series]) or "")
    local value_text = M.fmt(v, spec.unit, signed)
    local vx = sx(v)
    local tip = v >= 0 and text("val", vx + 6, y + BAND / 2 + 4.5, "start", value_text)
      or text("val", vx - 6, y + BAND / 2 + 4.5, "end", value_text)
    out[#out + 1] = mark(value_text, label, hit(0, y, width, BAND) .. row_label(row[spec.label], y + BAND / 2, gutter)
      .. bar_path(color, sx(math.max(lo, 0)), vx, y + (BAND - BAR) / 2) .. tip, i)
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
  local sx = linear(lo, hi, GUTTER + LABEL_ROOM, W - RIGHT)
  local out = { x_axis(ticks, sx, top, bottom, spec.unit) }
  for i, row in ipairs(rows) do
    local y = top + (i - 1) * BAND
    local cy = y + BAND / 2
    local fx, tx = sx(a[i]), sx(b[i])
    out[#out + 1] = mark(M.fmt(a[i], spec.unit) .. " → " .. M.fmt(b[i], spec.unit), row[spec.label],
      hit(0, y, W, BAND) .. row_label(row[spec.label], cy)
      .. line("link", fx, cy, tx, cy, PAINT.muted) .. dot("c1s", fx, cy) .. dot("c1", tx, cy)
      .. (tx >= fx and text("val", tx + 10, cy + 4.5, "start", M.fmt(b[i], spec.unit))
        or text("val", tx - 10, cy + 4.5, "end", M.fmt(b[i], spec.unit))), i)
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
  local px = {}
  for i = 1, #xs do px[i] = sx(l2(xs[i])) end
  for i, row in ipairs(rows) do
    local x = px[i]
    local short = xs[i] >= 1024 and (M.fmt(xs[i] / 1024) .. "K") or M.fmt(xs[i])
    -- Each hit column runs to the midpoints with its neighbours, so the readout
    -- always snaps to the nearest window and the columns never overlap.
    local x0 = i > 1 and (px[i - 1] + x) / 2 or x - (px[2] - x) / 2
    local x1 = i < #px and (x + px[i + 1]) / 2 or x + (x - px[i - 1]) / 2
    local body = hit(x0, top, x1 - x0, bottom - top)
      .. dot("c1", x, sy(ys[i])) .. text("tick", x, bottom + 18, "middle", short)
    if i == #rows then body = body .. text("val", x, sy(ys[i]) - 12, "middle", M.fmt(ys[i], spec.unit)) end
    out[#out + 1] = mark(M.fmt(ys[i], spec.unit), row[spec.label] .. " tokens", body, i)
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
    local list, from_count = {}, 0
    for _, v in ipairs(type(a[i]) == "table" and a[i] or { a[i] }) do list[#list + 1] = v; from_count = from_count + 1 end
    for _, v in ipairs(type(b[i]) == "table" and b[i] or { b[i] }) do list[#list + 1] = v end
    local maxv = 0
    for _, v in ipairs(list) do maxv = math.max(maxv, v) end
    local ticks = M.nice_ticks(0, maxv, 4)
    local sx = linear(0, ticks[#ticks], GUTTER, W - RIGHT)
    local panel = { row_label(row[spec.label], cy), x_axis(ticks, sx, y + 2, y + 34, nil) }
    -- Hit areas are 24px wide but stop at the midpoint with the nearest other
    -- point, so close values never steal each other's tooltip.
    local xs = {}
    for j, v in ipairs(list) do xs[j] = sx(v) end
    for j, v in ipairs(list) do
      local color, who = j <= from_count and "c2" or "c1", j <= from_count and from_name or to_name
      local x0, x1 = xs[j] - 12, xs[j] + 12
      for k, other in ipairs(xs) do
        if k ~= j and other < xs[j] then x0 = math.max(x0, (other + xs[j]) / 2) end
        if k ~= j and other > xs[j] then x1 = math.min(x1, (other + xs[j]) / 2) end
      end
      panel[#panel + 1] = mark(M.fmt(v, spec.unit), row[spec.label] .. " · " .. who,
        hit(x0, cy - 12, x1 - x0, 24) .. dot(color, xs[j], cy), i)
    end
    out[#out + 1] = '<g class="panel">' .. table.concat(panel) .. "</g>"
  end
  return out, 8 + #rows * PANEL, { to_name, from_name }, nil
end

--- Draw signed estimates and intervals from the same source-table row.
-- Bounds must contain the estimate; the axis must contain every bound and zero.
function DRAW.interval(spec, rows)
  column(spec, rows, spec.label); column(spec, rows, spec.value)
  column(spec, rows, spec.lower); column(spec, rows, spec.upper)
  local means, lows, highs = values(spec, rows, spec.value), values(spec, rows, spec.lower), values(spec, rows, spec.upper)
  local lo, hi = 0, 0
  for i = 1, #rows do
    if lows[i] > means[i] or means[i] > highs[i] then fail(spec, "interval bounds must contain the estimate") end
    lo, hi = math.min(lo, lows[i]), math.max(hi, highs[i])
  end
  local requested_lo, requested_hi = tonumber(spec.min) or lo, tonumber(spec.max) or hi
  if requested_lo > lo or requested_hi < hi then fail(spec, "interval axis must include zero and all bounds") end
  if spec.max and requested_hi == requested_lo then fail(spec, "interval axis needs a positive span") end
  local ticks = M.nice_ticks(requested_lo, requested_hi, 4)
  -- Nice ticks may expand inferred ends, but authored bounds define the axis.
  if spec.min then ticks[1] = requested_lo end
  if spec.max then
    while #ticks > 1 and ticks[#ticks] > requested_hi + 1e-9 do ticks[#ticks] = nil end
    if ticks[#ticks] < requested_hi - 1e-9 then ticks[#ticks + 1] = requested_hi end
  end
  lo, hi = ticks[1], ticks[#ticks]
  local top, band, width = 70, 120, 320
  local bottom = top + (#rows - 1) * band + 80
  local sx = linear(lo, hi, 44, width - 24)
  local out = { x_axis(ticks, sx, top, bottom, spec.unit),
    line("ref", sx(0), top - 8, sx(0), bottom, PAINT.muted),
    text("ref-label", sx(0), top - 12, "middle", "no change") }
  for i, row in ipairs(rows) do
    local cy = top + (i - 1) * band + 32
    local lx, mx, hx = sx(lows[i]), sx(means[i]), sx(highs[i])
    local labels = M.wrap_label(row[spec.label], 26)
    local category = text("cat", 0, top + (i - 1) * band - 48, "start", labels[1])
    if labels[2] then category = category .. text("cat", 0, top + (i - 1) * band - 32, "start", labels[2]) end
    -- Confidence level belongs in the accessible name; tip numbers follow
    -- the source cells in column order without an extra numeric confidence label.
    local tip = M.fmt(means[i], spec.unit, true) .. "; " .. M.fmt(lows[i], spec.unit, true) .. " to " .. M.fmt(highs[i], spec.unit, true)
    out[#out + 1] = mark(tip, row[spec.label] .. " (mean and " .. (spec["interval-label"] or "interval") .. ")",
      hit(0, top + (i - 1) * band, width, i == #rows and 80 or band) .. category
      .. line("interval-range c1", lx, cy, hx, cy, PAINT.c1)
      .. line("interval-cap c1", lx, cy - 7, lx, cy + 7, PAINT.c1)
      .. line("interval-cap c1", hx, cy - 7, hx, cy + 7, PAINT.c1)
      .. dot("c1", mx, cy)
      .. text("val", lx, cy - 14, "middle", M.fmt(lows[i], spec.unit, true))
      .. text("val", hx, cy - 14, "middle", M.fmt(highs[i], spec.unit, true))
      .. text("val", mx, cy + 24, "middle", M.fmt(means[i], spec.unit, true)), i)
  end
  return out, bottom + 34, {}, nil
end

local function summary(spec, rows)
  if spec.summary then return spec.summary end
  if spec.kind == "interval" then
    local parts = {}
    for _, row in ipairs(rows) do
      parts[#parts + 1] = row[spec.label] .. " mean " .. row[spec.value] .. ", "
        .. (spec["interval-label"] or "interval") .. " " .. row[spec.lower] .. " to " .. row[spec.upper]
    end
    return (spec.title or "Chart") .. ": " .. table.concat(parts, "; ") .. ". Zero is no change. Full values in the table below."
  end
  local parts = {}
  for _, row in ipairs(rows) do
    local cells = {}
    -- Plotted values only, formatted as on the chart, honouring from-mode / to-mode.
    local cols = { { spec.value, "first" }, { spec.from, spec["from-mode"] }, { spec.to, spec["to-mode"] } }
    for k = 1, 3 do
      local key, mode = cols[k][1], cols[k][2]
      if key and row[key] then
        local nums, shown = M.parse_numbers(row[key]), {}
        for n, v in ipairs(nums) do
          if mode == "all" or n == 1 then shown[#shown + 1] = M.fmt(v, spec.unit) end
        end
        cells[#cells + 1] = table.concat(shown, ", ")
      end
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
  if spec.kind == "interval" then
    if #rows == 0 then fail(spec, "needs at least one row") end
  elseif #rows < 2 then fail(spec, "needs at least two rows") end
  local width = spec.kind == "interval" and 320 or (tonumber(spec["plot-width"]) or W)
  if spec["plot-width"] and (spec.kind ~= "bars" or not tonumber(spec["plot-width"]) or width < 320 or width > W or width % 1 ~= 0) then
    fail(spec, "plot-width requires bars and an integer width from 320 to 640")
  end
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
  local title_attr = spec.evidence_id and (' id="' .. esc(spec.evidence_id .. '-title') .. '" tabindex="-1"') or ""
  local tools = spec.source_id and ('<p class="chart-tools"><a href="#' .. esc(spec.source_id)
    .. '" aria-label="View exact values for ' .. esc(spec.title or "Chart") .. '">View exact values</a></p>') or ""
  return string.format('<figure class="chart chart-%s"><figcaption class="chart-title"%s>%s</figcaption>%s'
    .. '<div class="chart-body" tabindex="0" role="group" aria-label="%s">'
    .. '<svg viewBox="0 0 %d %s" width="%d" height="%s" role="group" aria-label="%s">%s</svg></div>%s</figure>',
    spec.kind, title_attr, esc(spec.title or ""), legend_html, esc((spec.title or "Chart") .. ", scrollable"),
    width, num(height), width, num(height), esc(summary(spec, rows)), table.concat(body), tools)
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

local chart_count = 0

--- Replace a `.chart` Div with the chart figure followed by its table.
function Div(el)
  if not has_class(el, "chart") then return nil end
  local spec = {}
  for k, v in pairs(el.attributes) do spec[k] = v end
  spec.file = quarto and quarto.doc and quarto.doc.input_file or nil
  local tbl, at
  for i, block in ipairs(el.content) do
    if block.t == "Table" or block.tag == "Table" then tbl, at = block, i; break end
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
  chart_count = chart_count + 1
  spec.evidence_id = "chart-evidence-" .. chart_count
  spec.source_id = tbl.attr.identifier ~= "" and tbl.attr.identifier or (spec.evidence_id .. "-data")
  tbl.attr.identifier = spec.source_id
  tbl.attr.classes:insert("chart-source")
  tbl.attr.attributes["tabindex"] = "-1"
  tbl.attr.attributes["aria-labelledby"] = spec.evidence_id .. "-title"
  -- Keep every authored block; the figure goes directly before the charted table.
  local out = {}
  for i, block in ipairs(el.content) do
    if i == at then out[#out + 1] = pandoc.RawBlock("html", M.render(spec, rows)) end
    out[#out + 1] = block
    if i == at then
      out[#out + 1] = pandoc.RawBlock("html", '<p class="chart-return"><a href="#' .. esc(spec.evidence_id .. '-title')
        .. '" aria-label="Return to chart: ' .. esc(spec.title or "Chart") .. '">Return to chart</a></p>')
    end
  end
  return out
end
