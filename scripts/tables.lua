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

--- Give long inline code in a table cell break opportunities after path and name
--- separators ("/", "_", "-", "."), so a narrow column breaks at those points
-- instead of clipping the code or crushing it into mid-word lines. Inbox wrapping:
-- the browser only breaks when the code would otherwise overflow. Only code of
-- 14+ characters gets this; short tokens like "R1" or "x" stay one piece.
-- @param contents pandoc.Inlines
-- @return pandoc.Inlines
local function split_long_code(contents)
  return contents:walk {
    Code = function(code)
      local text, attr = code.text, code.attr
      if #text < 14 then return nil end
      -- Collect positions just after separators, skipping runs so each break
      -- lands on the end of the longest separator run.
      local parts = {}
      local from = 1
      for i = 2, #text - 1 do
        local c = text:sub(i, i)
        local next_c = text:sub(i + 1, i + 1)
        if (c == "/" or c == "-" or c == "_" or c == ".") and next_c ~= c
          and next_c ~= "/" and next_c ~= "-" and next_c ~= "_" and next_c ~= "." then
          parts[#parts + 1] = text:sub(from, i)
          from = i + 1
        end
      end
      parts[#parts + 1] = text:sub(from)
      if #parts < 2 then return nil end
      local out = {}
      for j, part in ipairs(parts) do
        if j > 1 then out[#out + 1] = pandoc.RawInline("html", "<wbr>") end
        out[#out + 1] = pandoc.Code(part, attr)
      end
      return out
    end,
  }
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
  for _, cell in ipairs(head_rows[#head_rows].cells) do
    cell.contents = split_long_code(cell.contents)
  end
  local cells, numeric, longest, total, has_code = 0, 0, 0, 0, false
  local col_max, col_numeric, col_cells = {}, {}, {}
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      for i, cell in ipairs(row.cells) do
        cell.contents = split_long_code(cell.contents)
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
  -- 45+ characters is already two or more wrapped lines inside a grid column on a
  -- phone, so the column stops being a figure-comparison cell there.
  local prose_column = false
  for i, n in pairs(col_cells) do
    if col_numeric[i] / n < 0.5 and col_max[i] >= 45 then prose_column = true end
  end
  -- The same for the row-label column, which the loop above skips: a row label of
  -- 20+ characters (a model name, "Deceitful (Alan, Enigma, Scarlet)") cannot be
  -- read inside one narrow cell of a four-plus-column grid on a phone, so the
  -- table stacks and the label gets the full width.
  local first_max = 0
  for _, body in ipairs(tbl.bodies) do
    for _, row in ipairs(body.body) do
      local cell = row.cells[1]
      if cell then first_max = math.max(first_max, #pandoc.utils.stringify(cell.contents)) end
    end
  end
  local long_row_label = first_max >= 20 and #labels >= 4
  -- Mostly numeric cells (the "wordy" test) that also carry some long entries read
  -- as a grid; anything else compares better stacked.
  local wordy = numeric / cells < 0.5
    and (longest >= 40 or total / cells >= 20 or #labels >= 4 or has_code)
  if not (prose_column or wordy or long_row_label) then return nil end
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
