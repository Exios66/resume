-- Run from the repository root: lua tests/test_charts.lua
-- Unit tests for scripts/charts.lua: number parsing, ticks, formatting and the SVG renderers.
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
dofile("scripts/charts.lua")

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

local MAPRED = rows_of({ "Job", "Speedup" }, { { "word count", "3.8×" }, { "sort", "2.9×" }, { "grep", "2.3×" } })
local mr = CHARTS.render({ kind = "bars", title = "Speedup", label = "Job", value = "Speedup",
  unit = "×", min = "0", max = "4", ref = "4", ["ref-label"] = "ideal 4×" }, MAPRED)
assert_eq(count(mr, '<line class="ref"'), 1, "reference line")
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
local tbl = { t = "Table",
  head = { rows = { { cells = { cell("Job"), cell("Speedup") } } } },
  bodies = { { body = { { cells = { cell("sort"), cell("2.9×") } }, { cells = { cell("grep"), cell("2.3×") } } } } } }
local out = Div({ classes = { "chart" }, attributes = { kind = "bars", title = "S", label = "Job", value = "Speedup" },
  content = { { t = "Para" }, tbl } })
assert(out[1].format == "html" and out[1].text:find('class="chart chart-bars"', 1, true), "filter emits the chart")
assert(out[2] == tbl, "filter keeps the table after the chart")
assert_eq(Div({ classes = { "note" }, attributes = {}, content = {} }), nil, "other divs untouched")

print("chart unit tests passed")
