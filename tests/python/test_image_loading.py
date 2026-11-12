"""Published content images reserve space and defer only later images."""
import test_links as checks
from test_portfolio_additions import ContentParser


def test_every_content_image_has_intrinsic_dimensions_and_loading_policy():
    seen = 0
    for page in checks.DOCS.rglob('*.html'):
        if 'site_libs' in page.parts:
            continue
        images = [a for tag, a, ancestors in ContentParser(page).elements
                  if tag == 'img' and any(tag == 'main' for tag, _ in ancestors)]
        for i, attrs in enumerate(images):
            seen += 1
            for key in ('width', 'height'):
                assert int(checks.attr(attrs, key)) > 0, (page, attrs)
            assert checks.attr(attrs, 'loading') == ('eager' if i == 0 else 'lazy'), page
            assert checks.attr(attrs, 'decoding') == 'async', page
    assert seen >= 60


def test_visual_case_studies_lead_with_existing_real_capture():
    for slug, filename in [('wave-laboratory', 'overview-light.jpg'),
                           ('neuron-atlas', 'steering-studio.jpg')]:
        parser = ContentParser(checks.DOCS / f'projects/{slug}.html')
        elements = parser.elements
        h1 = next(i for i, (tag, _, _) in enumerate(elements) if tag == 'h1')
        image = next(i for i, (tag, _, _) in enumerate(elements) if tag == 'img')
        h2 = next(i for i, (tag, _, _) in enumerate(elements) if tag == 'h2')
        assert h1 < image < h2
        attrs = elements[image][1]
        assert checks.attr(attrs, 'src').endswith(filename)
        assert len(checks.attr(attrs, 'alt').split()) >= 20
