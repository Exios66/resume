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

-- Hand-picked icon set (24x24, stroke-based; shapes follow Lucide, ISC license).
-- Delivered once per page as an inline sprite; used via <svg class="icon"><use href="#i-NAME"/></svg>.
local ICONS = {
  { "github", [=[<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.4 5.4 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>]=] },
  { "linkedin", [=[<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>]=] },
  { "mail", [=[<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>]=] },
  { "file-text", [=[<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>]=] },
  { "book-open", [=[<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>]=] },
  { "code", [=[<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>]=] },
  { "play", [=[<polygon points="6 3 20 12 6 21 6 3"/>]=] },
  { "arrow-left", [=[<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>]=] },
  { "arrow-right", [=[<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>]=] },
  { "arrow-up-right", [=[<path d="M7 7h10v10"/><path d="M7 17 17 7"/>]=] },
  { "download", [=[<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/>]=] },
  { "map-pin", [=[<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>]=] },
  { "sun", [=[<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>]=] },
  { "moon", [=[<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9z"/>]=] },
  { "layers", [=[<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>]=] },
  { "brain", [=[<path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18z"/><path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18z"/><path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/><path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/><path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/><path d="M3.477 10.896a4 4 0 0 1 .585-.396"/><path d="M19.938 10.5a4 4 0 0 1 .585.396"/><path d="M6 18a4 4 0 0 1-1.967-.516"/><path d="M19.967 17.484A4 4 0 0 1 18 18"/>]=] },
  { "scale", [=[<path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>]=] },
  { "waves", [=[<path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/><path d="M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>]=] },
  { "clock", [=[<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>]=] },
}

--- Build the inline SVG sprite holding every icon as a <symbol id="i-NAME">.
-- @return string HTML for a zero-size, hidden <svg>.
local function sprite()
  local parts = { '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">' }
  for _, icon in ipairs(ICONS) do
    parts[#parts + 1] = string.format(
      '<symbol id="i-%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
        .. 'stroke-linecap="round" stroke-linejoin="round">%s</symbol>', icon[1], icon[2])
  end
  parts[#parts + 1] = "</svg>"
  return table.concat(parts)
end

--- Markup that references one sprite icon.
-- @param name string Icon name, without the i- prefix.
-- @param extra string|nil Extra class names.
-- @return string HTML for an decorative, aria-hidden <svg>.
-- width/height keep the icon at 1em even if styles.css fails to load (an SVG's default is 300x150).
function icon_html(name, extra)
  return string.format('<svg class="icon%s" width="1em" height="1em" aria-hidden="true" focusable="false">'
    .. '<use href="#i-%s"/></svg>', extra and (" " .. extra) or "", name)
end

local function icon_inline(name, extra, lead)
  return pandoc.RawInline("html", (lead or "") .. icon_html(name, extra))
end

local function has_class(el, name)
  for _, c in ipairs(el.classes or {}) do
    if c == name then return true end
  end
  return false
end

local function text_of(el)
  if pandoc.utils and pandoc.utils.stringify then return pandoc.utils.stringify(el) end
  return ""
end

local NAV_ICONS = {
  ["case study"] = "book-open", ["technical report"] = "file-text", ["code"] = "code", ["live demo"] = "play",
}
local GROUP_ICONS = {
  { "document intelligence", "layers" }, { "behavioral machine learning", "brain" },
  { "llm agent design", "scale" }, { "side projects", "waves" },
}

--- Icon for a project-nav tab, chosen from its label.
-- @param label string Link text.
-- @return string|nil Icon name.
function nav_icon_name(label)
  return NAV_ICONS[(label or ""):lower():gsub("^%s+", ""):gsub("%s+$", "")]
end

--- Icon for a group heading on the projects index.
-- @param label string Heading text.
-- @return string|nil Icon name.
function group_icon_name(label)
  local lower = (label or ""):lower()
  for _, g in ipairs(GROUP_ICONS) do
    if lower:sub(1, #g[1]) == g[1] then return g[2] end
  end
  return nil
end

--- Icon for a contact or action link, chosen from its destination.
-- @param href string|nil Link target.
-- @return string|nil Icon name.
function contact_icon_name(href)
  href = href or ""
  local lower = href:lower()
  if lower:match("^mailto:") then return "mail" end
  if lower:match("^https?://[%w%.]*linkedin%.com") then return "linkedin" end
  if lower:match("^https?://github%.com/exios66/?$") then return "github" end
  if lower:match("%.pdf$") or lower:match("%.pdf[?#]") then return "download" end
  return nil
end

--- Whether a link points off this site.
-- @param href string|nil Link target.
-- @return boolean
function is_external_href(href)
  href = (href or ""):lower()
  if not href:match("^https?://") then return false end
  local rest = href:match("^https?://exios66%.github%.io/resume(.*)$")
  if rest == nil then return true end
  return not (rest == "" or rest:match("^[/%?#]"))
end

local function contains_image(content)
  for _, inline in ipairs(content or {}) do
    if inline.tag == "Image" then return true end
  end
  return false
end

local function prepend(el, inline)
  local new = { inline }
  for _, item in ipairs(el.content or {}) do new[#new + 1] = item end
  el.content = new
end

local function append(el, inline)
  local new = {}
  for _, item in ipairs(el.content or {}) do new[#new + 1] = item end
  new[#new + 1] = inline
  el.content = new
end

--- Add the matching icon before a project-nav tab's label.
-- @param link Pandoc Link inside .project-nav.
-- @return Pandoc The link, changed when its label has an icon.
function decorate_nav_link(link)
  local name = nav_icon_name(text_of(link))
  if name then prepend(link, icon_inline(name)) end
  return link
end

--- Replace a leading arrow in a .back link with an icon (or a trailing one in .more).
-- @param link Pandoc Link with the back or more class.
-- @return Pandoc The link.
local function decorate_arrow_link(link)
  local content = link.content or {}
  if has_class(link, "back") then
    local first = content[1]
    if first and first.tag == "Str" and first.text:sub(1, 3) == "\u{2190}" then
      local rest, skip = {}, 1
      local remainder = first.text:sub(4)
      if remainder ~= "" then rest[1] = pandoc.Str(remainder) end
      if remainder == "" and content[2] and content[2].tag == "Space" then skip = 2 end
      for i = skip + 1, #content do rest[#rest + 1] = content[i] end
      table.insert(rest, 1, icon_inline("arrow-left"))
      link.content = rest
    end
  elseif has_class(link, "more") then
    local last = content[#content]
    if last and last.tag == "Str" and last.text == "\u{2192}" then
      local rest = {}
      for i = 1, #content - 1 do rest[#rest + 1] = content[i] end
      -- Drop the space that separated the text from the arrow.
      if rest[#rest] and rest[#rest].tag == "Space" then rest[#rest] = nil end
      rest[#rest + 1] = icon_inline("arrow-right", "icon-go")
      link.content = rest
    end
  end
  return link
end

--- Decorate one link in page body text.
-- Back and more links swap their arrow for an icon; chips and buttons get a contact icon;
-- other external links get a small arrow-up-right. Links around images are left alone.
-- @param link Pandoc Link.
-- @return Pandoc The link.
function decorate_link(link)
  if not link or not link.target then return link end
  if has_class(link, "back") or has_class(link, "more") then return decorate_arrow_link(link) end
  if has_class(link, "chip") or has_class(link, "btn") then
    local name = contact_icon_name(link.target)
    if name then prepend(link, icon_inline(name)) end
    return link
  end
  if is_external_href(link.target) and not contains_image(link.content) then
    -- A word joiner keeps the icon on the line of the last word.
    append(link, icon_inline("arrow-up-right", "icon-ext", "\u{2060}"))
  end
  return link
end

--- Decorate a heading: group icons on .group-title, a nudging arrow on a heading that is one link.
-- @param header Pandoc Header.
-- @return Pandoc The header.
function decorate_header(header)
  if has_class(header, "group-title") then
    local name = group_icon_name(text_of(header))
    if name then prepend(header, icon_inline(name)) end
  elseif #(header.content or {}) == 1 and header.content[1].tag == "Link"
      and not is_external_href(header.content[1].target) then
    append(header.content[1], icon_inline("arrow-right", "icon-go"))
  end
  return header
end

--- Decorate the location chip with a map pin.
-- @param span Pandoc Span.
-- @return Pandoc The span.
function decorate_span(span)
  if has_class(span, "chip") and text_of(span):match("^Madison") then
    prepend(span, icon_inline("map-pin"))
  end
  return span
end

local DECORATE = {
  traverse = "topdown",
  Div = function(div)
    if has_class(div, "project-nav") then
      return pandoc.walk_block(div, { Link = decorate_nav_link }), false
    end
    return nil
  end,
  Header = function(h) return decorate_header(h), false end,
  Span = decorate_span,
  Link = function(l) return decorate_link(l), false end,
}

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
  if doc.walk then doc = doc:walk(DECORATE) end
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
      <li><button type="button" class="theme-toggle" aria-label="Switch theme"><span class="i-sun" hidden>%s</span><span class="i-moon">%s</span></button></li>
    </ul>
  </nav>
</header>
<main id="main">]], prefix, table.concat(links, "\n      "), icon_html("sun"), icon_html("moon"))

  -- The sprite goes after the footer so it never sits between the header and <main> in the layout.
  local footer = [[
</main>
<footer class="site-footer">
  <p>© 2026 Jack J. Burleson · Built with <a href="https://quarto.org">Quarto</a></p>
</footer>
]] .. sprite()

  table.insert(doc.blocks, 1, pandoc.RawBlock("html", header))
  table.insert(doc.blocks, pandoc.RawBlock("html", footer))
  return doc
end
