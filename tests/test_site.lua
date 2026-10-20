-- Run from the repository root: lua tests/test_site.lua
-- Minimal Pandoc/Quarto doubles exercise the real filter without rendering pages.
pandoc = {
  RawBlock = function(format, text)
    return { format = format, text = text }
  end,
  RawInline = function(format, text)
    return { tag = "RawInline", format = format, text = text }
  end,
  Str = function(text) return { tag = "Str", text = text } end,
  utils = {
    stringify = function(el)
      local out = {}
      for _, item in ipairs(el.content or {}) do
        out[#out + 1] = item.text or (item.tag == "Space" and " ")
          or pandoc.utils.stringify(item)
      end
      return table.concat(out)
    end,
  },
}
dofile("scripts/site.lua")

local function contains(text, fragment)
  assert(text:find(fragment, 1, true), "Missing HTML fragment: " .. fragment)
end

local destinations = {
  "index.html", "about.html", "projects/index.html",
  "research.html", "writing/index.html", "resume.html",
}

local cases = {
  { input = "index.qmd", prefix = "", current = "index.html" },
  { input = "about.qmd", prefix = "", current = "about.html" },
  { input = "research.qmd", prefix = "", current = "research.html" },
  { input = "resume.qmd", prefix = "", current = "resume.html" },
  { input = "projects/index.qmd", prefix = "../", current = "projects/index.html" },
  { input = "projects/mailroom-ml.qmd", prefix = "../", current = "projects/index.html" },
  { input = "projects/nested/study.qmd", prefix = "../../", current = "projects/index.html" },
  { input = "writing/index.qmd", prefix = "../", current = "writing/index.html" },
  { input = "writing/post.qmd", prefix = "../", current = "writing/index.html" },
  -- A similarly named directory or page must not activate a navigation item.
  { input = "projects-archive/study.qmd", prefix = "../" },
  { input = "writing-old/index.qmd", prefix = "../" },
  { input = "about-extra.qmd", prefix = "" },
  { input = "nested/about.qmd", prefix = "../" },
  { input = "resume.qmd.bak", prefix = "" },
  { input = "", prefix = "" },
}

local function check(case, root, absolute, empty)
  local input = case.input
  if absolute then input = root .. "/" .. input end
  quarto = { doc = { input_file = input }, project = { directory = root } }
  local first = { text = "Original heading" }
  local second = { text = "Original paragraph" }
  local meta = { title = "Preserved metadata" }
  local doc = { blocks = empty and {} or { first, second }, meta = meta }
  local result = Pandoc(doc)
  assert(result == doc, "Filter must return the document")
  assert(result.meta == meta, "Metadata must be preserved")
  assert(#result.blocks == (empty and 2 or 4), "Exactly two wrapper blocks expected")
  if not empty then
    assert(result.blocks[2] == first and result.blocks[3] == second,
           "Original content must remain between the wrappers, in order")
  end
  local header = result.blocks[1]
  local footer = result.blocks[#result.blocks]
  assert(header.format == "html" and footer.format == "html")
  contains(header.text, '<nav class="site-nav" aria-label="Main">')
  contains(header.text, '<main id="main">')
  contains(header.text, '<button type="button" class="theme-toggle" aria-label="Switch theme" hidden>')
  contains(header.text, '<use href="#i-sun"/>')
  contains(header.text, '<use href="#i-moon"/>')
  contains(header.text, '<span class="i-sun" hidden><svg class="icon" width="1em" height="1em"')
  contains(header.text, '<span class="i-moon"><svg class="icon" width="1em" height="1em"')
  assert(not header.text:find("<symbol", 1, true), "The sprite is not between the header and <main>")
  contains(footer.text, '<symbol id="i-github"')
  local _, sprites = (header.text .. footer.text):gsub('<svg width="0" height="0"', "")
  assert(sprites == 1, "Exactly one icon sprite per page")
  assert(not header.text:find("<!--", 1, true), "No HTML comments in output")
  assert(footer.text:find("</footer>", 1, true) < footer.text:find('id="i-github"', 1, true),
         "Sprite follows the footer")

  contains(header.text, 'class="site-title" href="' .. case.prefix .. 'index.html"')
  contains(footer.text, '</main>')
  contains(footer.text, '<footer class="site-footer">')
  contains(footer.text, '<script src="' .. case.prefix .. 'assets/js/site.js" defer></script>')
  contains(footer.text, 'href="https://quarto.org"')
  for _, destination in ipairs(destinations) do
    contains(header.text, 'class="nav-link" href="' .. case.prefix .. destination .. '"')
  end
  local _, active_count = header.text:gsub('aria%-current="page"', "")
  assert(active_count == (case.current and 1 or 0), "Unexpected active navigation count for " .. tostring(input))
  if case.current then
    contains(header.text, 'href="' .. case.prefix .. case.current .. '" aria-current="page"')
  end
end

for _, case in ipairs(cases) do
  check(case, "", false, false)
  check(case, "/project with spaces", false, false)
  check(case, "/project with spaces", true, false)
end
check({ input = "index.qmd", prefix = "", current = "index.html" }, "", false, true)
-- Missing Quarto path values are treated as an unknown root-level page.
check({ prefix = "" }, nil, false, true)
print("Site filter unit tests passed")

assert(#RawBlock({ format = "html", text = "<!-- src: notes.md -->" }) == 0, "Comment block should be removed")
assert(#RawInline({ format = "html", text = " <!-- a\nb --> " }) == 0, "Comment inline should be removed")
assert(RawBlock({ format = "html", text = "<div></div>" }) == nil, "Markup should be kept")
local mixed = RawBlock({ format = "html", text = "<!-- a --><div></div>" })
assert(mixed.text == "<div></div>", "Markup after a comment should be kept")
local between = RawBlock({ format = "html", text = "<!-- before --><div>Content</div><!-- after -->" })
assert(between.text == "<div>Content</div>", "Markup between comments should be kept")
assert(#RawBlock({ format = "html", text = "<!-- a -->\n<!-- b -->" }) == 0, "Only comments should be removed")
assert(RawBlock({ format = "latex", text = "<!-- a -->" }) == nil, "Non-HTML raw should be kept")
assert(RawBlock({ format = "html", text = '<script>var s = "<!-- x -->";</script>' }) == nil, "Script content should be kept")
local inline = RawInline({ format = "html", text = "<!-- a --><span>b</span>" })
assert(inline.text == "<span>b</span>", "Inline markup after a comment should be kept")
local before_pre = RawBlock({ format = "html", text = "<!-- note --><pre>code</pre>" })
assert(before_pre.text == "<pre>code</pre>", "Comment outside pre should be removed")
local around = RawBlock({ format = "html", text = "<PRE><!-- kept --></PRE><!-- gone --><p>x</p>" })
assert(around.text == "<PRE><!-- kept --></PRE><p>x</p>", "Comment inside pre should be kept")
local scripted = RawBlock({ format = "html", text = '<script>a("<!-- k -->")</script>\n<!-- n -->' })
assert(scripted.text == '<script>a("<!-- k -->")</script>\n', "Comment after script should be removed")
local prefix = RawBlock({ format = "html", text = "<prefix-el><!-- n --></prefix-el>" })
assert(prefix.text == "<prefix-el></prefix-el>", "Tags that only start with pre are not protected")
assert(RawBlock({ format = "html", text = "<!-- open" }) == nil, "Unclosed comment should be left alone")
print("comment stripping ok")

-- Both callbacks share the comment policy. Exercise identical cases so an inline
-- regression cannot hide behind coverage of blocks (or vice versa).
local comment_cases = {
  { label = "source note", text = "<!-- src: notes.md -->", remove = true },
  { label = "empty comment", text = "<!---->", remove = true },
  { label = "blank comment", text = "<!-- -->", remove = true },
  { label = "multiline note", text = "<!-- a\nb -->", remove = true },
  { label = "surrounding whitespace", text = "\t\r\n <!-- a\r\nb --> \n\t", remove = true },
  { label = "markup inside a note", text = "<!-- <div>not published</div> -->", remove = true },
  { label = "punctuation and Unicode", text = "<!-- Résumé: 100% [a-b] -->", remove = true },
  { label = "consecutive notes", text = "<!-- a -->\n<!-- b -->", remove = true },
  { label = "empty raw element", text = "" },
  { label = "whitespace only", text = " \t\n" },
  { label = "ordinary text", text = "Published text" },
  { label = "HTML block", text = "<div>Published text</div>" },
  { label = "HTML inline", text = "<span>Published text</span>" },
  { label = "SVG diagram", text = '<svg><text>Pipeline</text></svg>' },
  { label = "escaped comment", text = "&lt;!-- example --&gt;" },
  { label = "unclosed comment", text = "<!-- unfinished" },
  { label = "closing delimiter only", text = "notes -->" },
  { label = "invalid opening delimiter", text = "<!- notes -->" },
  { label = "invalid closing delimiter", text = "<!-- notes ->" },
  { label = "text before a note", text = "Published <!-- note -->", expect = "Published " },
  { label = "text after a note", text = "<!-- note --> Published", expect = " Published" },
  { label = "markup before a note", text = "<div>Published</div><!-- note -->", expect = "<div>Published</div>" },
  { label = "markup after a note", text = "<!-- note --><div>Published</div>", expect = "<div>Published</div>" },
  -- A raw HTML element can contain both comments and visible content. Only the
  -- comment spans are removed; the rest of the element is published.
  { label = "markup between notes", text = "<!-- before --><div>Published</div><!-- after -->", expect = "<div>Published</div>" },
  { label = "text between notes", text = "<!-- before -->Published<!-- after -->", expect = "Published" },
}

local comment_failures = {}
local comment_checks = 0
for _, handler in ipairs({ { name = "RawBlock", callback = RawBlock },
                           { name = "RawInline", callback = RawInline } }) do
  local function check_comment(format, case)
    local element = { format = format, text = case.text }
    local result = handler.callback(element)
    comment_checks = comment_checks + 1
    local removed = type(result) == "table" and next(result) == nil
    local correct
    if case.expect then
      correct = result == element and element.text == case.expect
    else
      correct = case.remove and removed or (not case.remove and result == nil)
      assert(element.format == format and element.text == case.text,
             handler.name .. " must not change an element it removes or keeps")
    end
    if not correct then
      comment_failures[#comment_failures + 1] = handler.name .. ": " .. case.label
        .. (case.expect and " should keep only its content"
            or case.remove and " should be removed" or " should be preserved")
    end
  end
  for _, case in ipairs(comment_cases) do check_comment("html", case) end
  for _, format in ipairs({ "latex", "markdown", "org", "HTML", "html5", "" }) do
    check_comment(format, { label = "comment syntax in " .. format, text = "<!-- keep literally -->" })
  end
end
assert(#comment_failures == 0, "Comment filter failures:\n" .. table.concat(comment_failures, "\n"))
print("Comment filter unit tests passed (" .. comment_checks .. " cases)")

-- ---------------------------------------------------------------- icon decoration
local function str(t) return { tag = "Str", text = t } end
local SPACE = { tag = "Space" }
local function link(target, classes, ...)
  return { tag = "Link", target = target, classes = classes or {}, content = { ... } }
end
local function html_of(content)
  local out = {}
  for _, item in ipairs(content) do out[#out + 1] = item.text or (item.tag == "Space" and " " or "?") end
  return table.concat(out)
end
local function uses(content, name)
  return html_of(content):find('<use href="#i-' .. name .. '"/>', 1, true) ~= nil
end

-- Every icon name used by the filter has a symbol in the sprite, and ids are i-prefixed.
local sprite_html = Pandoc({ blocks = {} }).blocks[2].text
local used = {}
for _, name in ipairs({ "book-open", "file-text", "code", "play", "arrow-left", "arrow-right",
                        "arrow-up-right", "download", "map-pin", "sun", "moon", "layers", "brain",
                        "scale", "waves", "database", "clock", "github", "linkedin", "mail" }) do
  contains(sprite_html, '<symbol id="i-' .. name .. '"')
  used[name] = true
end
local _, symbols = sprite_html:gsub("<symbol ", "")
assert(symbols == 20, "Unexpected icon count: " .. symbols)

-- The new database symbol must render a shape, not just resolve to an empty id.
local database_symbol = sprite_html:match('(<symbol id="i%-database".-</symbol>)')
assert(database_symbol, "Missing database symbol")
local _, database_symbols = sprite_html:gsub('<symbol id="i%-database"', "")
assert(database_symbols == 1, "Database symbol must be defined exactly once")
contains(database_symbol, 'viewBox="0 0 24 24"')
contains(database_symbol, 'fill="none" stroke="currentColor"')
assert(database_symbol:find("<ellipse ", 1, true) and database_symbol:find("<path ", 1, true),
       "Database icon must contain its cylinder geometry")

-- project-nav labels
for label, icon in pairs({ ["Case study"] = "book-open", ["Technical report"] = "file-text",
                           ["Code"] = "code", ["Live demo"] = "play" }) do
  assert(nav_icon_name(label) == icon, label)
  assert(nav_icon_name("  " .. label:lower() .. " ") == icon, label .. " is case and space tolerant")
end
assert(nav_icon_name("Something else") == nil and nav_icon_name(nil) == nil and nav_icon_name("") == nil)
local tab = decorate_nav_link(link("x.html", {}, str("Case"), SPACE, str("study")))
assert(uses(tab.content, "book-open") and html_of(tab.content):find("Case study", 1, true))
local plain_tab = decorate_nav_link(link("x.html", {}, str("Other")))
assert(#plain_tab.content == 1, "Unknown tab labels are left alone")

-- back links
local back = decorate_link(link("index.qmd", { "back" }, str("\u{2190}"), SPACE, str("All"), SPACE, str("projects")))
assert(uses(back.content, "arrow-left") and html_of(back.content):find("All projects", 1, true))
assert(not html_of(back.content):find("\u{2190}", 1, true), "Leading arrow is replaced")
local glued = decorate_link(link("index.qmd", { "back" }, str("\u{2190}All")))
assert(uses(glued.content, "arrow-left") and html_of(glued.content):find("All", 1, true))
local no_arrow = decorate_link(link("index.qmd", { "back" }, str("Back")))
assert(#no_arrow.content == 1, "Back links without an arrow are unchanged")
local empty_back = decorate_link(link("index.qmd", { "back" }))
assert(#empty_back.content == 0, "Empty back links do not fail")
local more = decorate_link(link("p.qmd", { "more" }, str("All"), SPACE, str("projects"), SPACE, str("\u{2192}")))
assert(uses(more.content, "arrow-right") and not html_of(more.content):find("\u{2192}", 1, true))

-- external links
local ext = decorate_link(link("https://example.com/x", {}, str("Example")))
assert(uses(ext.content, "arrow-up-right") and html_of(ext.content):find("icon-ext", 1, true))
for _, skip in ipairs({ "https://exios66.github.io/resume/about.html", "https://exios66.github.io/resume",
                        "index.qmd", "#top", "mailto:a@b.co", "" }) do
  local l = decorate_link(link(skip, {}, str("Text")))
  assert(#l.content == 1, "No icon for " .. skip)
end
assert(is_external_href("https://exios66.github.io/degen-llms/"), "Sibling Pages sites are external")
assert(not is_external_href(nil))
local with_image = decorate_link(link("https://example.com", {}, { tag = "Image", text = "img" }))
assert(#with_image.content == 1, "Links around images are left alone")
for _, class in ipairs({ "btn", "chip" }) do
  local l = decorate_link(link("https://example.com/", { class }, str("Go")))
  assert(#l.content == 1, class .. " links get no external icon")
end
assert(decorate_link(nil) == nil, "nil link")
local no_target = { tag = "Link", classes = {}, content = { str("x") } }
assert(decorate_link(no_target) == no_target and #no_target.content == 1, "Link without target")
local lookalike = decorate_link(link("https://exios66.github.io/resumes/", {}, str("x")))
assert(uses(lookalike.content, "arrow-up-right"), "A sibling path that only starts like /resume is external")

-- contact links
local cases_contact = {
  { "https://www.linkedin.com/in/jackjburleson", "linkedin" },
  { "https://github.com/Exios66", "github" },
  { "https://github.com/Exios66/", "github" },
  { "mailto:jackjburleson@proton.me", "mail" },
  { "assets/Jack_Burleson_Resume.pdf", "download" },
  { "https://github.com/Exios66/degen-llms", nil },
  { "https://github.com/Exios66x", nil },
  { "resume.qmd", nil },
}
for _, c in ipairs(cases_contact) do
  assert(contact_icon_name(c[1]) == c[2], "contact icon for " .. c[1])
end
assert(contact_icon_name(nil) == nil)
local chip = decorate_link(link("https://github.com/Exios66", { "chip" }, str("github.com/Exios66")))
assert(uses(chip.content, "github"))

-- headings
local group = decorate_header({ tag = "Header", classes = { "group-title" },
  content = { str("Document"), SPACE, str("intelligence") } })
assert(uses(group.content, "layers"))
for text, icon in pairs({ ["Behavioral machine learning"] = "brain", ["LLM agent design"] = "scale",
                          ["Side projects & interests"] = "waves", ["Data engineering & visualization"] = "database" }) do
  local h = decorate_header({ tag = "Header", classes = { "group-title" }, content = { str(text) } })
  assert(uses(h.content, icon), text)
end
local unmatched = decorate_header({ tag = "Header", classes = { "group-title" }, content = { str("Other") } })
assert(#unmatched.content == 1)
local card_head = decorate_header({ tag = "Header", classes = {},
  content = { link("p.qmd", {}, str("Project")) } })
assert(uses(card_head.content[1].content, "arrow-right"), "Single-link headings get a nudging arrow")
local ext_head = decorate_header({ tag = "Header", classes = {}, content = { link("https://example.com", {}, str("X")) } })
assert(#ext_head.content[1].content == 1, "External single-link headings are left alone")
local text_head = decorate_header({ tag = "Header", classes = {}, content = { str("Plain") } })
assert(#text_head.content == 1)

-- Data-engineering group names match case-insensitively from the start of the label.
for _, label in ipairs({ "Data engineering", "DATA ENGINEERING & VISUALIZATION",
                         "dAtA eNgInEeRiNg & visualization", "Data engineering projects" }) do
  assert(group_icon_name(label) == "database", "Database icon for " .. label)
end
for _, label in ipairs({ "", "Data", "Data engineer", "Data visualization",
                         "Metadata engineering", "Applied data engineering", "Other" }) do
  assert(group_icon_name(label) == nil, "No group icon for " .. label)
end
assert(group_icon_name(nil) == nil, "Missing group label has no icon")

-- Pandoc splits the real heading into inlines. Preserve their order and the heading's attributes.
local data_content = { str("Data"), SPACE, str("engineering"), SPACE, str("&"), SPACE, str("visualization") }
local data_classes = { "wide", "group-title" }
local data_attributes = { ["data-section"] = "projects" }
local data_heading = { tag = "Header", level = 2, identifier = "data-engineering-visualization",
  classes = data_classes, attributes = data_attributes, content = data_content }
assert(decorate_header(data_heading) == data_heading, "Decoration returns the original heading")
assert(data_heading.level == 2 and data_heading.identifier == "data-engineering-visualization")
assert(data_heading.classes == data_classes and data_heading.attributes == data_attributes)
assert(#data_heading.content == #data_content + 1, "Exactly one icon is prepended")
assert(data_heading.content[1].tag == "RawInline" and data_heading.content[1].format == "html")
assert(uses({ data_heading.content[1] }, "database"), "Database icon precedes the label")
contains(data_heading.content[1].text, 'width="1em" height="1em"')
contains(data_heading.content[1].text, 'aria-hidden="true" focusable="false"')
for i, inline in ipairs(data_content) do
  assert(data_heading.content[i + 1] == inline, "Heading inline preserved at " .. i)
end

-- Matching words alone must not decorate ordinary headings or partial class names.
for _, heading_classes in ipairs({ {}, { "group-title-extra" }, { "page-title" } }) do
  local content = { str("Data engineering & visualization") }
  local h = { tag = "Header", classes = heading_classes, content = content }
  assert(decorate_header(h) == h and h.content == content and #h.content == 1,
         "Only group-title headings get the database icon")
end
for _, content in ipairs({ {}, { str("Applied data engineering") } }) do
  local h = { tag = "Header", classes = { "group-title" }, content = content }
  assert(decorate_header(h) == h and h.content == content, "Unmatched group headings are unchanged")
end

-- Formatting inside a label must not hide the new group from the filter.
local emphasis = { tag = "Emph", content = { str("Data") } }
local strong = { tag = "Strong", content = { str("engineering") } }
local formatted_content = { emphasis, SPACE, strong, SPACE, str("& visualization") }
local formatted = { tag = "Header", classes = { "group-title" }, content = formatted_content }
decorate_header(formatted)
assert(#formatted.content == #formatted_content + 1 and uses(formatted.content, "database"),
       "Formatted data-engineering headings get exactly one database icon")
for i, item in ipairs(formatted_content) do
  assert(formatted.content[i + 1] == item, "Inline formatting is preserved")
end

-- A linked group label takes precedence over the ordinary single-link heading arrow.
for _, target in ipairs({ "index.qmd#data", "https://example.org/data" }) do
  local group_link = link(target, {}, str("Data engineering"))
  local original_content = group_link.content
  local heading = { tag = "Header", classes = { "group-title" }, content = { group_link } }
  decorate_header(heading)
  assert(#heading.content == 2 and uses({ heading.content[1] }, "database"))
  assert(heading.content[2] == group_link and group_link.target == target,
         "Linked group label and destination are preserved")
  assert(group_link.content == original_content and #group_link.content == 1,
         "Group label must not gain a navigation arrow")
end

-- If Pandoc cannot stringify a heading, leave the new group untouched.
local saved_utils = pandoc.utils
for _, unavailable in ipairs({ {}, false }) do
  pandoc.utils = unavailable
  local content = { str("Data engineering") }
  local heading = { tag = "Header", classes = { "group-title" }, content = content }
  assert(decorate_header(heading) == heading and heading.content == content,
         "Missing stringify support must not add an icon or lose the heading")
end
pandoc.utils = saved_utils

-- location chip
local place = decorate_span({ tag = "Span", classes = { "chip" }, content = { str("Madison, WI") } })
assert(uses(place.content, "map-pin"))
local other_chip = decorate_span({ tag = "Span", classes = { "chip" }, content = { str("Remote") } })
assert(#other_chip.content == 1)
-- every icon self-sizes, so a missing stylesheet cannot blow it up to the 300x150 SVG default
assert(icon_html("code") == '<svg class="icon" width="1em" height="1em" aria-hidden="true" focusable="false">'
  .. '<use href="#i-code"/></svg>', icon_html("code"))
assert(icon_html("arrow-up-right", "icon-ext"):find('class="icon icon-ext" width="1em" height="1em"', 1, true))
print("icon decoration ok")
