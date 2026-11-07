-- Run from the repository root: lua tests/test_charts.lua
-- Unit tests for scripts/charts.lua: number parsing, ticks, formatting and the SVG renderers.
-- A minimal Pandoc double lets the filter file load without rendering pages.
pandoc = {
  RawBlock = function(format, text) return { format = format, text = text } end,
  utils = { stringify = function(el) return el.text or "" end },
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
assert_eq(CHARTS.fmt(-3.6, " pts", true), "−3.6 pts", "negative signed")
assert_eq(CHARTS.fmt(14.5, " pts", true), "+14.5 pts", "positive signed")
assert_eq(CHARTS.fmt(0.9505), "0.9505", "plain decimal")
assert_eq(CHARTS.fmt(4.0, "×"), "4×", "integer with unit")
assert_eq(CHARTS.fmt(0, nil, true), "0", "zero carries no sign")

print("chart unit tests passed")
