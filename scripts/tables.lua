-- Table layout for small screens. Registered in _quarto.yml at post-render: earlier,
-- Quarto's project link resolver rebuilds any table whose cells hold a link and
-- drops the classes and attributes added here, so those tables never stacked.

--- Is a cell's text a number, a measurement or a dash rather than prose?
local function looks_numeric(text)
  local t = text:gsub("^%s+", ""):gsub("%s+$", "")
  if t == "" or t == "—" or t == "–" or t == "-" then return true end
  -- Lua patterns match bytes, so compare multi-byte prefixes as whole strings.
  for _, prefix in ipairs({ "≥", "≤", "≈", "−", "±", "~", "<", ">", "+", "-" }) do
    if t:sub(1, #prefix) == prefix then t = t:sub(#prefix + 1):gsub("^%s+", ""); break end
  end
  t = t:gsub("%s*%(.*%)$", ""):gsub("%s*±.*$", "")
  return t:match("^%d[%d.,]*%%?%s*%S*$") ~= nil and #t <= 24
end

--- Mark text-heavy tables with class "stack" and give every body cell a data-label
-- naming its column. On small screens styles.css shows each row as a labelled block
-- instead of squeezing prose into narrow columns. Number tables keep their grid and
-- scroll sideways, which is how people compare figures. Explicit roles keep the table
-- semantics that some browsers drop once table parts are restyled as blocks.
-- @param tbl pandoc.Table
-- @return pandoc.Table|nil
local function stack_table(tbl)
  local head_rows = tbl.head and tbl.head.rows or {}
  if #head_rows == 0 then return nil end
  local labels = {}
  for i, cell in ipairs(head_rows[#head_rows].cells) do
    labels[i] = pandoc.utils.stringify(cell.contents)
  end
  local cells, numeric, longest, total, has_code = 0, 0, 0, 0, false
  local col_max, col_numeric, col_cells = {}, {}, {}
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      for i, cell in ipairs(row.cells) do
        local text = pandoc.utils.stringify(cell.contents)
        longest = math.max(longest, #text)
        pandoc.walk_block(pandoc.Div(cell.contents), { Code = function() has_code = true end })
        if i > 1 then
          local is_num = looks_numeric(text)
          cells = cells + 1
          total = total + #text
          if is_num then numeric = numeric + 1 end
          col_max[i] = math.max(col_max[i] or 0, #text)
          col_cells[i] = (col_cells[i] or 0) + 1
          col_numeric[i] = (col_numeric[i] or 0) + (is_num and 1 or 0)
        end
      end
    end
  end
  if cells == 0 then return nil end
  -- A prose column (mostly words, some long entries) needs the full width on a phone.
  local prose_column = false
  for i, n in pairs(col_cells) do
    if col_numeric[i] / n < 0.5 and col_max[i] >= 60 then prose_column = true end
  end
  local wordy = numeric / cells < 0.5
    and (longest >= 40 or total / cells >= 20 or #labels >= 4 or has_code)
  if not (prose_column or wordy) then return nil end
  tbl.attr.classes:insert("stack")
  tbl.attr.attributes["role"] = "table"
  for _, row in ipairs(head_rows) do
    row.attr.attributes["role"] = "row"
    for _, cell in ipairs(row.cells) do cell.attr.attributes["role"] = "columnheader" end
  end
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      row.attr.attributes["role"] = "row"
      for i, cell in ipairs(row.cells) do
        cell.attr.attributes["role"] = "cell"
        if labels[i] and labels[i] ~= "" then cell.attr.attributes["data-label"] = labels[i] end
        -- Figures read best on one line: label on the left, value on the right.
        if i > 1 and looks_numeric(pandoc.utils.stringify(cell.contents)) then cell.attr.classes:insert("num") end
      end
    end
  end
  return tbl
end

return { { Table = stack_table } }
