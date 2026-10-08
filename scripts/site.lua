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
