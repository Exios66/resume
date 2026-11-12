"""Published content images reserve space and defer only later images."""
import test_links as checks
from test_portfolio_additions import ContentParser


def test_every_content_image_has_intrinsic_dimensions_and_loading_policy():
    seen = 0
    for page in checks.DOCS.rglob('*.html'):
        if 'site_libs' in page.parts:
            continue
        elements = ContentParser(page).elements
        first_h2 = next((i for i, (tag, _, _) in enumerate(elements) if tag == 'h2'), None)
        images = [(i, a) for i, (tag, a, ancestors) in enumerate(elements)
                  if tag == 'img' and any(tag == 'main' for tag, _ in ancestors)]
        for n, (i, attrs) in enumerate(images):
            seen += 1
            for key in ('width', 'height'):
                assert int(checks.attr(attrs, key)) > 0, (page, attrs)
            lead = n == 0 and (first_h2 is None or i < first_h2)
            assert checks.attr(attrs, 'loading') == ('eager' if lead else 'lazy'), (page, attrs)
            assert checks.attr(attrs, 'decoding') == 'async', page
    assert seen >= 60


def test_a_first_image_below_the_fold_stays_lazy():
    parser = ContentParser(checks.DOCS / 'projects/mailroom-ml.html')
    elements = parser.elements
    first_h2 = next(i for i, (tag, _, _) in enumerate(elements) if tag == 'h2')
    first_image = next(i for i, (tag, _, _) in enumerate(elements) if tag == 'img')
    assert first_h2 < first_image
    assert checks.attr(elements[first_image][1], 'loading') == 'lazy'


def test_mailroom_ml_chart_alt_text_names_the_collapse_gate():
    parser = ContentParser(checks.DOCS / 'projects/mailroom-ml.html')
    alts = [checks.attr(attrs, 'alt') for tag, attrs, _ in parser.elements
            if tag == 'img' and 'subclass_collapse.svg' in checks.attr(attrs, 'src')]
    assert len(alts) == 1
    assert 'collapse gate at 0.75' in alts[0]
    assert 'accuracy gate' not in alts[0]


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
