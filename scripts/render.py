#!/usr/bin/env python3
"""
denkbeleg - Slide-Renderer
Erzeugt aus einer Post-JSON sieben Slides im Format 1080x1350.

Aufruf:  python3 scripts/render.py posts/2026-09-10-ovsiankina.json
Ausgabe: out/<slug>/01.jpg ... 07.jpg  (plus PNG-Vorschau und caption.txt)
"""
import json, sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright

WURZEL = Path(__file__).resolve().parent.parent
VORLAGE = (WURZEL / "template" / "slide.html").read_text(encoding="utf-8")

BREITE, HOEHE = 1080, 1350


def absaetze(text):
    """Mehrzeiligen Text in <p>-Bloecke wandeln. Leerzeile trennt Absaetze."""
    teile = [t.strip() for t in re.split(r"\n\s*\n", text.strip()) if t.strip()]
    return "".join(f"<p>{t}</p>" for t in teile)


def baue_slide(slide, nummer, gesamt, stempel_an):
    typ = slide.get("typ", "inhalt")
    zaehler = f'<div class="zaehler">{nummer:02d} / {gesamt:02d}</div>'
    stempel = ""

    if typ == "haken":
        klasse = "haken"
        unter = slide.get("unterzeile", "")
        inhalt = f'<h1>{slide["titel"]}</h1>'
        if unter:
            inhalt += f'<div class="unterzeile">{unter}</div>'
        if stempel_an:
            stempel = '<div class="stempel">WIDERLEGT</div>'

    elif typ == "ende":
        klasse = "ende"
        inhalt = (
            f'<div class="merksatz">{slide["merksatz"]}</div>'
            f'<div class="handle">{slide.get("abbinder", "")}</div>'
        )
        zaehler = ""

    else:
        klasse = "inhalt"
        inhalt = f'<div class="kopf">{slide["kopf"]}</div>'
        inhalt += f'<div class="fliess">{absaetze(slide["text"])}</div>'
        if slide.get("quelle"):
            inhalt += f'<div class="quelle">{slide["quelle"]}</div>'

    return (VORLAGE
            .replace("__KLASSE__", klasse)
            .replace("__ZAEHLER__", zaehler)
            .replace("__STEMPEL__", stempel)
            .replace("__INHALT__", inhalt))


def rendern(pfad_json):
    daten = json.loads(Path(pfad_json).read_text(encoding="utf-8"))
    slug = daten["slug"]
    slides = daten["slides"]
    stempel_an = daten.get("rubrik") == "widerlegt"
    ziel = WURZEL / "out" / slug
    ziel.mkdir(parents=True, exist_ok=True)

    tmp = WURZEL / "template" / "_arbeit.html"
    erzeugt = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        seite = browser.new_page(viewport={"width": BREITE, "height": HOEHE},
                                 device_scale_factor=1)
        for i, slide in enumerate(slides, start=1):
            html = baue_slide(slide, i, len(slides), stempel_an and i == 1)
            tmp.write_text(html, encoding="utf-8")
            seite.goto(tmp.as_uri())
            seite.wait_for_timeout(400)          # Schriften laden lassen
            seite.screenshot(path=str(ziel / f"{i:02d}.png"))
            # Instagram verlangt JPEG fuer Karussell-Slides
            seite.screenshot(path=str(ziel / f"{i:02d}.jpg"),
                             type="jpeg", quality=62)
            erzeugt.append(i)
        browser.close()

    tmp.unlink(missing_ok=True)
    (ziel / "caption.txt").write_text(daten["caption"].strip() + "\n", encoding="utf-8")
    print(f"{len(erzeugt)} Slides -> {ziel}")
    return ziel


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Aufruf: render.py <post.json>")
    rendern(sys.argv[1])
