-- Run from the repository root: lua tests/test_site.lua
-- Minimal Pandoc/Quarto doubles exercise the real filter without rendering pages.
pandoc = {
  RawBlock = function(format, text)
    return { format = format, text = text }
  end,
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
  contains(header.text, '<button type="button" class="theme-toggle" aria-label="Switch theme">')
  contains(header.text, 'class="site-title" href="' .. case.prefix .. 'index.html"')
  contains(footer.text, '</main>')
  contains(footer.text, '<footer class="site-footer">')
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
