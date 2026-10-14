-- Pandoc/Quarto filter: wraps every page in the site header, <main> landmark and footer.
-- Needed because `theme: none` disables Quarto's own navbar and footer.
-- Links are computed relative to the page, so the site works under any base path.

local NAV = {
  { label = "Home",     href = "index.html",          section = "index.html" },
  { label = "About",    href = "about.html",          section = "about.html" },
  { label = "Projects", href = "projects/index.html", section = "projects/" },
  { label = "Research", href = "research.html",       section = "research.html" },
  { label = "Writing",  href = "writing/index.html",  section = "writing/" },
  { label = "Résumé",   href = "resume.html",         section = "resume.html" },
}

--- Compute the current page's HTML path relative to the Quarto project root.
-- @return string Input path with the project prefix removed and .qmd replaced by .html.
local function page_path()
  local input = quarto.doc.input_file or ""
  local root = quarto.project.directory or ""
  local rel = input
  if root ~= "" and input:sub(1, #root) == root then
    rel = input:sub(#root + 2)
  end
  return (rel:gsub("%.qmd$", ".html"))
end

--- Check whether a page belongs to a navigation item's section.
-- @param item table Navigation entry whose section is a page or directory path.
-- @param path string Project-relative HTML page path.
-- @return boolean Whether the path matches the page or starts with the directory.
local function is_current(item, path)
  if item.section:sub(-1) == "/" then
    return path:sub(1, #item.section) == item.section
  end
  return path == item.section
end

local PROTECTED = { "script", "style", "pre" }

--- Find the next protected open tag (<script>, <style>, <pre>) at or after pos.
-- @param lower string Lowercased element text.
-- @param pos integer Search start.
-- @return integer|nil, string|nil Start of the tag and its name.
local function next_protected(lower, pos)
  local best, name
  for _, tag in ipairs(PROTECTED) do
    local s = pos
    while true do
      local found = lower:find("<" .. tag, s, true)
      if not found then break end
      local after = lower:sub(found + #tag + 1, found + #tag + 1)
      if after == "" or after:match("[%s>/]") then
        if not best or found < best then best, name = found, tag end
        break
      end
      s = found + 1
    end
  end
  return best, name
end

--- Remove HTML comments from raw HTML; comments are authoring notes, not page content.
-- Each <!-- ... --> span is removed on its own, so markup between two comments is kept.
-- Text inside <script>, <style> and <pre> is copied unchanged, since comment-like text
-- there is content; comments outside those elements are still removed.
-- @param el Pandoc raw element.
-- @return table|nil Empty list when only whitespace remains, the element with its comments
-- removed, or nil to leave the element unchanged.
local function strip_comments(el)
  if el.format ~= "html" then return nil end
  local src, lower = el.text, el.text:lower()
  local out, pos, count = {}, 1, 0
  while pos <= #src do
    local c = src:find("<!--", pos, true)
    local p, tag = next_protected(lower, pos)
    if p and (not c or p < c) then
      local close = lower:find("</" .. tag, p, true)
      local stop = close and (lower:find(">", close, true) or #src) or #src
      out[#out + 1] = src:sub(pos, stop)
      pos = stop + 1
    elseif c then
      local e = src:find("-->", c + 4, true)
      if not e then break end
      out[#out + 1] = src:sub(pos, c - 1)
      count = count + 1
      pos = e + 3
    else
      break
    end
  end
  if count == 0 then return nil end
  out[#out + 1] = src:sub(pos)
  local text = table.concat(out)
  if text:match("^%s*$") then return {} end
  el.text = text
  return el
end

--- Remove HTML comments from a raw HTML inline.
-- @param el Pandoc RawInline element.
-- @return table|nil See strip_comments.
function RawInline(el)
  return strip_comments(el)
end

--- Remove HTML comments from a raw HTML block.
-- @param el Pandoc RawBlock element.
-- @return table|nil See strip_comments.
function RawBlock(el)
  return strip_comments(el)
end

--- Wrap the document in the site header, main landmark, and footer.
-- Navigation links are relative to the page; the current section gets aria-current.
-- @param doc Pandoc Document whose blocks will be modified in place.
-- @return Pandoc The modified document.
function Pandoc(doc)
  local path = page_path()
  local _, depth = path:gsub("/", "")
  local prefix = string.rep("../", depth)

  local links = {}
  for _, item in ipairs(NAV) do
    local current = is_current(item, path) and ' aria-current="page"' or ""
    links[#links + 1] = string.format(
      '<li><a class="nav-link" href="%s%s"%s>%s</a></li>', prefix, item.href, current, item.label)
  end

  local header = string.format([[
<header class="site-header">
  <nav class="site-nav" aria-label="Main">
    <a class="site-title" href="%sindex.html">Jack J. Burleson</a>
    <ul class="nav-list">
      %s
      <li><button type="button" class="theme-toggle" aria-label="Switch theme"></button></li>
    </ul>
  </nav>
</header>
<main id="main">]], prefix, table.concat(links, "\n      "))

  local footer = [[
</main>
<footer class="site-footer">
  <p>© 2026 Jack J. Burleson · Built with <a href="https://quarto.org">Quarto</a></p>
</footer>]]

  table.insert(doc.blocks, 1, pandoc.RawBlock("html", header))
  table.insert(doc.blocks, pandoc.RawBlock("html", footer))
  return doc
end
