# denkbeleg-bilder

Slide-Bilder fuer den Instagram-Account [@denkbeleg](https://www.instagram.com/denkbeleg/).

Das Repository ist oeffentlich, weil Instagram die Karussell-Bilder ueber eine
oeffentliche HTTPS-Adresse abholt. Es enthaelt keine Zugangsdaten.

## Ablauf

1. Ein Beitrag wird als JSON unter `posts/` abgelegt.
2. Der Push startet die Action `Slides rendern`.
3. Die Action laedt die Schriften, rendert sieben Slides und legt sie unter
   `out/<slug>/01.jpg` bis `07.jpg` ab.
4. Instagram zieht die Bilder von `raw.githubusercontent.com`.

Die Bilder werden also auf GitHub erzeugt, nicht lokal hochgeladen.
