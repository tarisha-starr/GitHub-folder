from playwright.sync_api import sync_playwright
import pathlib
src = pathlib.Path("piha.html").resolve()
out = pathlib.Path("Piha-shot-list.pdf").resolve()
chrome = "/opt/pw-browsers/chromium"
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=chrome if pathlib.Path(chrome).exists() else None)
    pg = b.new_page()
    pg.goto(src.as_uri(), wait_until="networkidle")
    pg.wait_for_timeout(3000)
    # confirm the display face actually loaded before committing to a PDF
    loaded = pg.evaluate("document.fonts.check('16px Marcellus') && document.fonts.check('16px Lora')")
    print("fonts loaded:", loaded)
    pg.emulate_media(media="print")
    pg.pdf(
        path=str(out), format="A4", print_background=True,
        display_header_footer=True,
        header_template="<div></div>",
        footer_template=(
            "<div style='width:100%;font-family:Georgia,serif;font-size:7pt;color:#6B6255;"
            "padding:0 11mm;display:flex;justify-content:space-between;'>"
            "<span>Piha shot list &middot; 26 August</span>"
            "<span class='pageNumber'></span></div>"
        ),
        margin={"top":"13mm","bottom":"13mm","left":"11mm","right":"11mm"},
    )
    b.close()
print("wrote", out)
