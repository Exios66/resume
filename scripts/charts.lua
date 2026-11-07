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
