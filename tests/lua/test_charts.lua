-- Run from the repository root: lua tests/lua/test_charts.lua
-- Unit tests for scripts/filters/charts.lua: number parsing, ticks, formatting and the SVG renderers.
-- A minimal Pandoc double lets the filter file load without rendering pages.
pandoc = {
  RawBlock = function(format, text) return { format = format, text = text } end,
  utils = {
    stringify = function(el)
      if el.text then return el.text end
      local out = {}
      for _, item in ipairs(el) do out[#out + 1] = pandoc.utils.stringify(item) end
      return table.concat(out)
    end,
  },
}
dofile("scripts/filters/charts.lua")

-- Wide charts carry a second drawing for phones in a <template>. The existing
-- assertions describe the wide drawing; the phone drawings are checked at the end.
local PHONE = {}
do
  local render = CHARTS.render
  CHARTS.render = function(spec, rows)
    local html = render(spec, rows)
    local phone = html:match('<template class="chart%-narrow">(.-)</template>')
    if phone then PHONE[#PHONE + 1] = { kind = spec.kind, wide = html:gsub('<template.-</template>', ''), svg = phone } end
    return (html:gsub('<template.-</template>', ''))
  end
end

local function show(v)
  if type(v) == "number" then return string.format("%.10g", v) end
  if type(v) ~= "table" then return tostring(v) end
  local out = {}
  for i, x in ipairs(v) do out[i] = show(x) end
  return "{" .. table.concat(out, ", ") .. "}"
end

local function assert_eq(actual, expected, what)
  local ok = show(actual) == show(expected)
  assert(ok, (what or "value") .. ": expected " .. show(expected) .. ", got " .. show(actual))
end

-- parse_numbers
local P = CHARTS.parse_numbers
assert_eq(P("−2.3"), { -2.3 }, "unicode minus")
assert_eq(P("+14.5"), { 14.5 }, "leading plus")
assert_eq(P("4,096"), { 4096 }, "thousands comma")
assert_eq(P("83.1% (665/800)"), { 83.1, 665, 800 }, "percent with counts")
assert_eq(P("0.19, 0.29 and 0.31 million in three re-runs"), { 0.19, 0.29, 0.31 }, "list separated by comma-space")
assert_eq(P("3.8×"), { 3.8 }, "times sign")
assert_eq(P("—"), {}, "dash only")
assert_eq(P("$0.4937"), { 0.4937 }, "dollar")

-- nice_ticks
assert_eq(CHARTS.nice_ticks(0, 1, 5), { 0, 0.2, 0.4, 0.6, 0.8, 1 }, "unit ticks")
assert_eq(CHARTS.nice_ticks(-3.6, 14.5, 5), { -5, 0, 5, 10, 15 }, "signed ticks")
assert_eq(CHARTS.nice_ticks(0, 4, 4), { 0, 1, 2, 3, 4 }, "speedup ticks")

-- fmt
assert_eq(CHARTS.fmt(-3.6, "pts", true), "−3.6 pts", "negative signed")
assert_eq(CHARTS.fmt(14.5, "pts", true), "+14.5 pts", "positive signed")
assert_eq(CHARTS.fmt(0.9505), "0.9505", "plain decimal")
assert_eq(CHARTS.fmt(4.0, "×"), "4×", "integer with unit")
assert_eq(CHARTS.fmt(0, nil, true), "0", "zero carries no sign")

-- ---------------------------------------------------------------- renderers
local function count(s, needle)
  local n, at = 0, 1
  while true do
    local a, b = s:find(needle, at, true)
    if not a then return n end
    n, at = n + 1, b + 1
  end
end

local function rows_of(headers, list)
  local rows = {}
  for i, cells in ipairs(list) do
    rows[i] = {}
    for j, h in ipairs(headers) do rows[i][h] = cells[j] end
  end
  return rows
end

-- Each mark's markup, keyed by its tooltip label.
local function marks(svg)
  local out = {}
  for g in svg:gmatch('<g class="mark".-</g>') do
    out[g:match('data%-tip%-label="([^"]*)"')] = g
  end
  return out
end

local NATD = rows_of({ "Persona", "Type", "Sessions", "Mean exam change (points)" }, {
  { "Athena", "Helpful", "4", "+14.5" }, { "Milgrim", "Helpful", "3", "+9.3" },
  { "Enigma", "Deceitful", "3", "+4.7" }, { "Alan", "Deceitful", "3", "−2.3" },
  { "Scarlet", "Deceitful", "5", "−3.6" },
})
local natd = CHARTS.render({ kind = "bars", title = "Exam change by persona", label = "Persona",
  value = "Mean exam change (points)", series = "Type", unit = "pts", signed = "true" }, NATD)
assert_eq(count(natd, '<g class="mark"'), 5, "NATD mark count")
assert(natd:find('<figure class="chart chart-bars">', 1, true), "figure wrapper")
assert(natd:find('<div class="chart-body" tabindex="0"', 1, true), "scrollable body")
assert(natd:find('<svg viewBox="0 0 640 ', 1, true) and natd:find('role="group" aria-label="Exam change by persona: ', 1, true),
  "svg is a labelled group with a summary")
assert(natd:find('role="img" aria-label="Scarlet · Deceitful: −3.6 pts"', 1, true), "each mark has an accessible name")
assert(natd:find("<li><span class=\"key c1\"></span>Helpful</li>", 1, true), "legend: Helpful")
assert(natd:find("<li><span class=\"key c2\"></span>Deceitful</li>", 1, true), "legend: Deceitful")
assert(natd:find('data-tip-value="−3.6 pts"', 1, true), "signed tip value")
local zero = tonumber(natd:match('<line class="zero" x1="([%d%.]+)"'))
local function bar_x(mark)
  local x0, x1 = mark:match('<path class="bar c%d" d="M([%d%.]+) [%d%.]+ H([%d%.]+)')
  return tonumber(x0), tonumber(x1)
end
local m = marks(natd)
local a0, a1 = bar_x(m["Athena · Helpful"])
local s0, s1 = bar_x(m["Scarlet · Deceitful"])
assert(zero and a0 == zero and a1 > zero, "positive bar grows right from zero")
assert(s0 == zero and s1 < zero, "negative bar grows left from zero")
assert(m["Scarlet · Deceitful"]:find('class="bar c2"', 1, true), "deceitful uses chart-2")
for _, who in ipairs({ "Scarlet · Deceitful", "Alan · Deceitful" }) do
  local vx, body = m[who]:match('<text class="val" x="([%d%.]+)" y="[%d%.]+" text%-anchor="end">([^<]*)</text>')
  assert(vx, who .. ": negative value label is end-anchored")
  assert(tonumber(vx) - utf8.len(body) * 7.5 >= tonumber(m[who]:match('<text class="cat" x="([%d%.]+)"')) + 12, who .. ": negative value label clears the row labels")
end

local MAPRED = rows_of({ "Job", "Speedup" }, { { "word count", "3.8×" }, { "sort", "2.9×" }, { "grep", "2.3×" } })
local mr = CHARTS.render({ kind = "bars", title = "Speedup", label = "Job", value = "Speedup",
  unit = "×", min = "0", max = "4", ref = "4", ["ref-label"] = "ideal 4×" }, MAPRED)
assert(count(mr, '<line class="ref"') >= 1, "reference line")
-- The ref line must not run through a value label: "3.8×" sits right where the 4× line is.
do
  local wx, wy, wbody = mr:match('<text class="val" x="([%d%.]+)" y="([%d%.]+)" text%-anchor="start">(3%.8×)</text>')
  assert(wx, "word count value label")
  wx, wy = tonumber(wx), tonumber(wy)
  local wend = wx + utf8.len(wbody) * 7.5
  for x1, y1, y2 in mr:gmatch('<line class="ref" x1="([%d%.]+)" y1="([%d%.]+)" x2="[%d%.]+" y2="([%d%.]+)"') do
    x1, y1, y2 = tonumber(x1), tonumber(y1), tonumber(y2)
    local crosses_x = x1 >= wx - 2 and x1 <= wend + 2
    local crosses_y = y1 <= wy and y2 >= wy - 10
    assert(not (crosses_x and crosses_y), "ref line crosses the 3.8× label")
  end
end
assert(not mr:find("chart-legend", 1, true), "single series has no legend")

local HEADS = rows_of({ "Head", "Arm B", "Final" }, {
  { "contract", "0.0195", "0.162" }, { "corporate_record", "0.2485", "0.904" },
  { "correspondence", "0.1289", "0.351" }, { "insurance_claim", "0.9889", "1.000" },
  { "merger_agreement", "0.2381", "0.000" },
})
local db = CHARTS.render({ kind = "dumbbell", title = "Per-head macro-F1", label = "Head",
  from = "Arm B", to = "Final", min = "0", max = "1" }, HEADS)
assert_eq(count(db, '<g class="mark"'), 5, "dumbbell marks")
local merger = marks(db)["merger_agreement"]
local from_x = tonumber(merger:match('<circle class="dot c1s" cx="([%d%.]+)"'))
local to_x = tonumber(merger:match('<circle class="dot c1" cx="([%d%.]+)"'))
assert(from_x and to_x and to_x < from_x, "merger_agreement falls from Arm B to Final")
assert(merger:find('data-tip-value="0.2381 → 0"', 1, true), "dumbbell tip shows both values")
local mlabel_x = tonumber(merger:match('<text class="val" x="([%d%.]+)" y="[%d%.]+" text%-anchor="end"'))
assert(mlabel_x and mlabel_x < to_x and mlabel_x - 2 * 7.5 >= 190, "a fall is labelled left of the final dot, clear of row labels")
local contract = marks(db)["contract"]
local cto = tonumber(contract:match('<circle class="dot c1" cx="([%d%.]+)"'))
local clabel_x = tonumber(contract:match('<text class="val" x="([%d%.]+)" y="[%d%.]+" text%-anchor="start"'))
assert(clabel_x and clabel_x > cto, "a rise is labelled right of the final dot")

local WINDOWS = rows_of({ "Context window", "Documents that fit" }, {
  { "4,096", "76.6%" }, { "16,384", "89.6%" }, { "32,768", "93.2%" }, { "65,536", "95.0%" }, { "131,072", "99.8%" },
})
local st = CHARTS.render({ kind = "step", title = "Documents that fit", label = "Context window",
  value = "Documents that fit", unit = "%", min = "70", max = "100" }, WINDOWS)
assert_eq(count(st, '<g class="mark"'), 5, "step marks")
assert_eq(count(st, '<path class="line c1"'), 1, "one step line")
local xs = {}
for x in st:gmatch('<circle class="dot c1" cx="([%d%.]+)"') do xs[#xs + 1] = tonumber(x) end
assert(math.abs((xs[2] - xs[1]) / 2 - (xs[3] - xs[2])) < 0.01, "log2 x: 4K→16K is two doublings, 16K→32K one")
assert(st:find("starts at 70%", 1, true), "axis note says where the y-axis starts")

local BENCH = rows_of({ "Benchmark", "README", "Re-runs" }, {
  { "Classic RL ant, one ant", "19.65 million steps per second", "4.28, 10.63 and 13.18 million in three re-runs" },
  { "Colony of 25 ants", "0.54 million steps per second, 13.39 million cell updates per second", "0.19, 0.29 and 0.31 million in three re-runs" },
})
local sp = CHARTS.render({ kind = "strip", title = "Steps per second", label = "Benchmark", from = "README",
  to = "Re-runs", ["from-mode"] = "first", ["to-mode"] = "all", ["from-name"] = "README (Apple M2)",
  ["to-name"] = "Re-runs", unit = "M steps/s" }, BENCH)
assert_eq(count(sp, '<g class="panel"'), 2, "one panel per row")
assert_eq(count(sp, '<circle class="dot c2"'), 2, "README markers")
assert_eq(count(sp, '<circle class="dot c1"'), 6, "re-run markers")
assert(not sp:find("13.39", 1, true), "from-mode first ignores later numbers")

-- labels
local lines = CHARTS.wrap_label("Escalation to a stronger model, 48-image low-confidence slice", 26)
assert_eq(#lines, 2, "long label wraps to two lines")
assert(#lines[1] <= 26 and utf8.len(lines[2]) <= 26, "wrapped lines fit")
local esc = CHARTS.render({ kind = "bars", title = "A <b>", label = "L", value = "V" },
  rows_of({ "L", "V" }, { { "x < y & z", "1" }, { "w", "2" } }))
assert(esc:find("x &lt; y &amp; z", 1, true) and not esc:find("<b>", 1, true), "text is escaped")

-- errors
local function fails(pattern, spec, rows)
  local ok, err = pcall(CHARTS.render, spec, rows)
  assert(not ok and tostring(err):find(pattern, 1, true), "expected error '" .. pattern .. "', got " .. tostring(err))
end
fails("column 'Nope' not found", { kind = "bars", label = "Job", value = "Nope" }, MAPRED)
fails("needs at least two rows", { kind = "bars", label = "Job", value = "Speedup" }, { MAPRED[1] })
fails("no number in column 'V', row 2", { kind = "bars", label = "L", value = "V" },
  rows_of({ "L", "V" }, { { "a", "1" }, { "b", "—" } }))
fails("unknown kind 'pie'", { kind = "pie", label = "Job", value = "Speedup" }, MAPRED)

-- filter
local function cell(text) return { contents = { { text = text } } } end
local tbl = { t = "Table", attr = { identifier = "", classes = { insert = table.insert }, attributes = {} },
  head = { rows = { { cells = { cell("Job"), cell("Speedup") } } } },
  bodies = { { body = { { cells = { cell("sort"), cell("2.9×") } }, { cells = { cell("grep"), cell("2.3×") } } } } } }
local out = Div({ classes = { "chart" }, attributes = { kind = "bars", title = "S", label = "Job", value = "Speedup" },
  content = { { t = "Para" }, tbl } })
assert_eq(out[1].t, "Para", "filter keeps other blocks in the wrapper")
assert(out[2].format == "html" and out[2].text:find('class="chart chart-bars"', 1, true), "filter emits the chart before the table")
assert(out[3] == tbl, "filter keeps the table after the chart")

-- review fixes
assert_eq(CHARTS.parse_numbers(".5"), { 0.5 }, "leading-dot decimal")
assert_eq(CHARTS.parse_numbers("−.5 and -.25"), { -0.5, -0.25 }, "signed leading-dot decimals")
assert_eq(CHARTS.parse_numbers("v1.5"), { 1.5 }, "ordinary decimal unchanged")
local capped = CHARTS.render({ kind = "dumbbell", title = "T", label = "L", from = "A", to = "B", min = "60", max = "98" },
  rows_of({ "L", "A", "B" }, { { "x", "61", "98" }, { "y", "70", "80" } }))
assert(capped:find('>98</text>', 1, true) and not capped:find('>100</text>', 1, true), "configured max ends the axis")
fails('must start at zero', { kind = "bars", label = "Job", value = "Speedup", min = "2" }, MAPRED)
assert(db:find('aria%-label="Per%-head macro%-F1: contract 0%.0195 to 0%.162'), "dumbbell summary names its values")
assert(sp:find("Classic RL ant, one ant 19.65M steps/s to 4.28M steps/s, 10.63M steps/s, 13.18M steps/s", 1, true)
  or sp:find("Classic RL ant, one ant 19.65 M steps/s to 4.28 M steps/s, 10.63 M steps/s, 13.18 M steps/s", 1, true),
  "strip summary names every plotted value and honours from-mode")
-- No two hit areas in a chart may overlap (strip points 0.29 and 0.31 sit 13px apart).
local function spans(svg)
  local out = {}
  for x, y, w, h in svg:gmatch('<rect class="hit" x="([%d%.%-]+)" y="([%d%.%-]+)" width="([%d%.]+)" height="([%d%.]+)"') do
    out[#out + 1] = { tonumber(x), tonumber(y), tonumber(x) + tonumber(w), tonumber(y) + tonumber(h) }
  end
  return out
end
for name, svg in pairs({ strip = sp, step = st }) do
  local s = spans(svg)
  for i = 1, #s do for j = i + 1, #s do
    local A, B = s[i], s[j]
    local overlap = math.min(A[3], B[3]) - math.max(A[1], B[1]) > 0.11 and math.min(A[4], B[4]) - math.max(A[2], B[2]) > 0.11
    assert(not overlap, name .. ": hit areas " .. i .. " and " .. j .. " overlap")
  end end
end
local multi = CHARTS.render({ kind = "strip", title = "T", label = "L", from = "A", to = "B", ["from-mode"] = "all", ["to-mode"] = "all" },
  rows_of({ "L", "A", "B" }, { { "x", "1, 2", "3" }, { "y", "4", "5 and 6" } }))
assert_eq(count(multi, '<circle class="dot c2"'), 3, "from-mode all plots every from value")
assert_eq(Div({ classes = { "note" }, attributes = {}, content = {} }), nil, "other divs untouched")

local compact = CHARTS.render({ kind = "bars", label = "Job", value = "Speedup", ["plot-width"] = "320" }, MAPRED)
assert(compact:find('<svg viewBox="0 0 320 ', 1, true), "compact bar geometry uses the requested width")
for _, hitbox in ipairs(spans(compact)) do assert(hitbox[3] <= 320, "compact hit box stays inside its viewBox") end
fails("plot-width requires bars", { kind = "bars", label = "Job", value = "Speedup", ["plot-width"] = "200" }, MAPRED)

-- An estimate and its confidence interval are different from two endpoints.
local interval_rows = rows_of({ "Comparison", "Mean", "Low", "High" }, {
  { "Backups on minus off", "−0.11", "−0.38", "+0.16" },
})
local interval_spec = { kind = "interval", title = "Paired effect", label = "Comparison", value = "Mean",
  lower = "Low", upper = "High", unit = "s", min = "-0.5", max = "0.5", ["interval-label"] = "95% paired interval" }
local ci = CHARTS.render(interval_spec, interval_rows)
assert_eq(count(ci, '<g class="mark"'), 1, "single interval estimate is valid")
assert(ci:find('data-source-row="1"', 1, true), "interval mark retains source-row identity")
assert(ci:find('data-tip-value="−0.11 s; −0.38 s to +0.16 s"', 1, true), "interval tip preserves all three values")
assert(ci:find('95% paired interval', 1, true), "confidence level is named")
local lx, hx = ci:match('<line class="interval%-range c1" x1="([%d%.]+)" y1="[%d%.]+" x2="([%d%.]+)"')
local mx = ci:match('<circle class="dot c1" cx="([%d%.]+)"')
local zx = ci:match('<line class="ref" x1="([%d%.]+)"')
lx, hx, mx, zx = tonumber(lx), tonumber(hx), tonumber(mx), tonumber(zx)
assert(lx < mx and mx < zx and zx < hx, "signed mean and zero lie correctly inside the interval")
assert(math.abs((mx - lx) / (hx - lx) - .5) < .002, "mean placement follows source values")
assert(math.abs((zx - lx) / (hx - lx) - .38 / .54) < .002, "zero placement follows source bounds")
fails("interval bounds must contain the estimate", interval_spec,
  rows_of({ "Comparison", "Mean", "Low", "High" }, { { "bad", "0.2", "0.3", "0.4" } }))
fails("interval axis must include zero and all bounds",
  { kind = "interval", label = "Comparison", value = "Mean", lower = "Low", upper = "High", min = "0" }, interval_rows)
fails("needs at least one row", interval_spec, {})

-- Explicit non-round domains remain authored; automatic ends may use nice ticks.
for _, bounds in ipairs({ { min = "-0.38", max = "0.16" }, { min = "-0.38" }, { max = "0.16" } }) do
  local spec = { kind = "interval", label = "Comparison", value = "Mean", lower = "Low", upper = "High",
    min = bounds.min, max = bounds.max }
  local svg = CHARTS.render(spec, interval_rows)
  local left, right = svg:match('<line class="interval%-range c1" x1="([%d%.]+)" y1="[%d%.]+" x2="([%d%.]+)"')
  if bounds.min then assert(math.abs(tonumber(left) - 44) < .01, "explicit lower bound is the axis start") end
  if bounds.max then assert(math.abs(tonumber(right) - 296) < .01, "explicit upper bound is the axis end") end
  if bounds.min and bounds.max then
    local zero = tonumber(svg:match('<line class="ref" x1="([%d%.]+)"'))
    assert(math.abs(zero - (44 + 252 * .38 / .54)) < .051, "zero follows the authored non-round domain")
  end
end


local zero_interval = rows_of({ "Comparison", "Mean", "Low", "High" }, { { "No difference", "0", "0", "0" } })
assert(CHARTS.render({ kind = "interval", label = "Comparison", value = "Mean", lower = "Low", upper = "High" }, zero_interval),
  "automatic domain expands a collapsed interval")
for _, bounds in ipairs({ { min = "0", max = "0" }, { max = "0" } }) do
  fails("interval axis needs a positive span",
    { kind = "interval", label = "Comparison", value = "Mean", lower = "Low", upper = "High", min = bounds.min, max = bounds.max }, zero_interval)
end

fails("integer width", { kind = "bars", label = "Job", value = "Speedup", ["plot-width"] = "320.5" }, MAPRED)

-- Phone drawings: same marks and source rows as the wide drawing, on a 256-unit grid,
-- with no overlapping hit areas and no row label left in a side gutter.
assert(#PHONE >= 5, "wide charts carry a phone drawing")
for _, chart in ipairs(PHONE) do
  assert(chart.svg:find('viewBox="0 0 256 ', 1, true), chart.kind .. ": phone drawing is 256 units wide")
  assert_eq(count(chart.svg, '<g class="mark"'), count(chart.wide, '<g class="mark"'), chart.kind .. ": phone marks")
  local rows_wide, rows_phone = {}, {}
  for row in chart.wide:gmatch('data%-source%-row="(%d+)"') do rows_wide[#rows_wide + 1] = row end
  for row in chart.svg:gmatch('data%-source%-row="(%d+)"') do rows_phone[#rows_phone + 1] = row end
  assert_eq(rows_phone, rows_wide, chart.kind .. ": phone source rows")
  for x in chart.svg:gmatch('<text class="cat" x="([%d%.%-]+)"') do
    assert_eq(tonumber(x), 0, chart.kind .. ": phone row label starts at the left edge")
  end
  local s = spans(chart.svg)
  for i = 1, #s do for j = i + 1, #s do
    local A, B = s[i], s[j]
    assert(A[1] >= -0.01 and A[3] <= 256.01, chart.kind .. ": phone hit area inside the drawing")
    local overlap = math.min(A[3], B[3]) - math.max(A[1], B[1]) > 0.11 and math.min(A[4], B[4]) - math.max(A[2], B[2]) > 0.11
    assert(not overlap, chart.kind .. ": phone hit areas " .. i .. " and " .. j .. " overlap")
  end end
end

print("chart unit tests passed")
