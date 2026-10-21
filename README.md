# Globaler Min-Cut: Stoer–Wagner und Karger – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-globaler-schnitt-demo.streamlit.app/)**

Zweites Stück der Reihe **Schnitte und Zusammenhang** (Arbeitstitel der Linie `schnitte-zusammenhang`) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“, Bereich Graphentheorie. Vehikel: ein **Verbindungsnetz zwischen Standorten** (Depots, Umschlagpunkte, Werke), synthetisch und mit festem Zufalls-Seed, die Leitungen mit ganzzahligen Gewichten (Kapazität oder Stärke). Die Demo fragt: **Was ist der kleinste Schnitt des ganzen Netzes, und wie oft muss man würfeln?** Ein Schnitt teilt die Standorte in zwei Seiten, sein Wert ist die Summe der Gewichte der Leitungen dazwischen. Das Verfahren von Stoer und Wagner findet den kleinsten Schnitt exakt; das Verfahren von Karger würfelt (zufällige Kontraktion) und trifft einen bestimmten kleinsten Schnitt in einem Lauf nur mit Wahrscheinlichkeit mindestens 2 / (n (n − 1)).

Nachbarn: den Zusammenhang über disjunkte Wege zeigt `menger-demo`; Max-Flow gleich Min-Cut für ein Standortpaar `edmonds-karp-demo`, `dinic-demo` und `push-relabel-demo`; den kleinsten Schnitt für alle Paare als Baum `gomory-hu-demo`.

## Warum dieses Problem

Der kleinste Schnitt sagt, wie viel man mindestens kappen muss, damit ein Netz zerfällt, und er ist die Schwachstelle des Netzes. Die naheliegende Rechnung (ein Fluss je Paar, n − 1 Flüsse) ist für das ganze Netz nicht nötig: Stoer–Wagner braucht keinen Fluss, und Karger kommt mit Würfeln aus. Die Demo zeigt, **wo die Garantie des Würfelns sehr pessimistisch ist** (ein Lauf trifft einen kleinsten Schnitt auf den Modellnetzen mit 16 Standorten, ohne Kreis und Baum, im Mittel mit 25 bis 74 %; die Schranke für einen bestimmten Schnitt ist 0,83 %), **wo sie scharf ist** (der Kreis, exakt gerechnet) und dass der **kleinste Schnitt auf den dünnen Modellnetzen (Zufallsnetz, Gitter, Ring, skalenfreies Netz) fast immer nur den am schwächsten angebundenen Standort abtrennt**, nicht aber auf Kreis, Baum und Verbundnetz.

## Befunde und Korrekturen gegenüber dem Plan

- **Kreis und Baum als Netztypen:** Der Plan nannte sie als Handbeispiele; die Demo nimmt sie als Netztypen (Extremfälle) auf, weil an ihnen die Schranke exakt gerechnet werden kann (Kreis: C(n, 2) kleinste Schnitte) und jeder Lauf trifft (Baum: jede Leitung ein kleinster Schnitt).
- **Die Vormessungszahlen gelten nicht:** „In 80 von 96 Modellnetzen sind alle kleinsten Schnitte trivial“ stammt aus Wegwerfskripten mit anderen Netzen und ohne Kreis und Baum; die Demo misst neu (Tabelle unten): bei gleichen Gewichten in **58 von 96** Netzen, aber in **58 von 60** auf den fünf Netztypen Zufallsnetz (Grad 3 und 5), Gitter, Ring und skalenfreies Netz, und in **0 von 36** bei Kreis, Baum und Verbundnetz.
- **Schranke für 99 %:** 551 Läufe bei 16 Standorten (genau ln 0,01 / ln (1 − 2 / (n (n − 1)))); der Plan nannte etwa 553 nach der Näherung C(n, 2) · ln 100.
- **Gewichte aufgenommen:** Der Plan sah „Gewicht 0“ nur als Randfall vor; die Demo rechnet mit ganzzahligen Gewichten 1 bis 5 (Regler „Gewichte“), Karger zieht Leitungen mit Wahrscheinlichkeit proportional zum Gewicht.
- **Cactus nicht gebaut:** Die Zahl aller kleinsten Schnitte wird durch Aufzählung (bis 16 Standorte) gezeigt, die Cactus-Darstellung nur als Begriff in der Einordnung (Plan: Einordnung).
- **Zitate:** Genannt sind Stoer und Wagner (JACM 1997), Karger (SODA 1993) und Karger und Stein (JACM 1996) mit geprüfter Fundstelle; der Stand der Technik (deterministische Verfahren in nahezu linearer Zeit) steht nur als Einordnung ohne Zahlen der Originale in der App.

## Modell

Ein einfaches, **zusammenhängendes** Netz mit n Standorten und ganzzahligen Leitungsgewichten (Zufallsnetz: Zufallsbaum plus Leitungen bis zum mittleren Grad; Gitter, Ring mit Abkürzungen, skalenfreies Netz nach bevorzugter Anbindung, Verbundnetz mit drei Regionen und einstellbar vielen Leitungen dazwischen, Kreis, Baum) und das handgebaute **Lehrbeispiel mit zwei Werken**: Werk 1 (A, B, C, D) und Werk 2 (E, F, G, H) sind je ein vollständiges Netz, dazu die Leitungen A–E und A–F. Von Hand: der kleinste Schnitt ist **2** (A–E und A–F) und der einzige, der kleinste Schnitt an einem einzelnen Standort ist **3**. Der Zufall kommt nur aus `random.Random(seed)` mit `random()` (plattformstabil). Details und Formeln: Expander „📐 Mathematische Formulierung“ in der App.

## Methodik

- **Stoer–Wagner** (Gewichtsmatrix): n − 1 Phasen; jede ordnet die aktiven Vertreter nach der stärksten Bindung an die schon gewählten (bei Gleichstand der kleinste Vertreter), der **Schnitt der Phase** trennt den letzten Vertreter vom Rest, dann werden die letzten beiden verschmolzen. Der kleinste Schnitt der Phasen ist der kleinste Schnitt des Netzes (bei Gleichstand die erste Phase). Aufwand in **Matrixzugriffen** (jede Aktualisierung einer Bindung): (n + 1) n (n − 1) / 6 insgesamt.
- **Karger:** Leitungen in zufälliger Reihenfolge zusammenziehen (Schlüssel −ln(1 − r) / Gewicht, kleinster zuerst; Leitungen innerhalb einer Gruppe werden übersprungen, Union-Find), bis zwei Gruppen übrig sind. Aufwand in **Kantenprüfungen** (jede angesehene Leitung).
- **Aufzählung:** alle 2^(n−1) − 1 Zweiteilungen mit schrittweise berechnetem Schnittwert (bis 16 Standorte): kleinster Wert, Zahl und Gestalt aller kleinsten Schnitte.
- **Exakte Gegenprobe für Karger:** alle m! Kantenreihenfolgen kleiner Netze (m ≤ 8, ungewichtet): Verteilung der Ausgänge.
- **Unabhängige Prüfer:** Die App prüft jedes Ergebnis vor der Anzeige (der Schnitt hat den gemeldeten Wert, n − 1 Phasen, kleinster Wert nicht größer als der kleinste einzelne Standort, jeder Lauf von Karger ist ein echter Schnitt und nie kleiner als der kleinste, bei höchstens 16 Standorten gleich der Aufzählung).

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py`; Zähler über feste Netze (je Netztyp zwölf Netze mit 16 Standorten, feste Zufalls-Seeds), je Netz 400 Läufe von Karger, nie ein einzelner Zufalls-Seed. Netztypen: Kreis, Baum, Zufallsnetz mit mittlerem Grad 3 und 5, Gitter, Ring mit Abkürzungen, skalenfreies Netz, Verbundnetz (mittlerer Grad 5, eine Leitung zwischen je zwei Regionen).

| Frage | Befund |
|---|---|
| Stimmen alle Verfahren mit der Aufzählung aller Schnitte überein? | Auf **96** Netzen (acht Netztypen, je zwölf) stimmen **77.280** Prüfungen überein: Stoer–Wagner trifft den kleinsten Wert, und jeder der je 400 Läufe von Karger meldet einen echten Schnitt, nie einen kleineren als den kleinsten, und trifft er einen kleinsten, steht er in der Aufzählung. Abweichungen: **0**. |
| Wie oft ist der kleinste Schnitt ein einzelner Standort? (gleiche Gewichte) | In **58 von 96** Netzen (60 %) sind alle kleinsten Schnitte einzelne Standorte: Zufallsnetz Grad 3 in 10, Grad 5, Gitter, Ring und skalenfreies Netz in je **12 von 12**; Kreis, Baum und Verbundnetz in **0 von 12**. Der Wert des kleinsten Schnitts ist gleich dem des kleinsten einzelnen Standorts in **84 von 96** Netzen (im Verbundnetz in 0 von 12). |
| Und mit zufälligen Gewichten 1 bis 5? | Alle kleinsten Schnitte sind einzelne Standorte in **57 von 96** Netzen, der Wert ist gleich dem des kleinsten Standorts in **75 von 96** (auf dem Kreis in 5 von 12, bei gleichen Gewichten in 12 von 12). |
| Wie viele kleinste Schnitte gibt es? | Zahl je Netz bei 16 Standorten (gleiche Gewichte): Kreis **120** = C(16, 2), Baum **15** = n − 1, sonst höchstens **10** (skalenfrei), **6** (Ring), **5** (Zufallsnetz Grad 3), **4** (Zufallsnetz Grad 5, Gitter), **3** (Verbundnetz). |
| Wie oft trifft ein Lauf von Karger einen kleinsten Schnitt? | Mittel über 12 Netze: **100 %** (Kreis und Baum), **74 %** (skalenfrei), **50 %** (Zufallsnetz Grad 3), **45 %** (Verbundnetz), **36 %** (Gitter), **33 %** (Zufallsnetz Grad 5), **25 %** (Ring); die Schranke für einen bestimmten Schnitt ist **0,83 %**. Die gemessene Rate zählt jeden kleinsten Schnitt als Treffer, sie ist also das **31- bis 89-Fache** der Schranke; für einen bestimmten kleinsten Schnitt (den von Stoer–Wagner gefundenen, ohne den Kreis) ist sie das **7- bis 31-Fache**. Im einzelnen Netz (ohne Kreis und Baum) zwischen 10,5 % (Zufallsnetz Grad 5) und 89 % (skalenfreies Netz). |
| Ist die Schranke irgendwo scharf? | Ja, auf dem Kreis: Jeder der C(n, 2) kleinsten Schnitte wird bei genau **2 (n − 2)!** von n! Kantenreihenfolgen getroffen, exakt gerechnet für n = 5, 6, 7 (12 von 120, 48 von 720, 240 von 5.040), also mit **1 / C(n, 2)**; bei 16 Standorten gemessen **167 von 20.000** = 0,0084 gegen 0,0083. |
| Wie viele Läufe für 99 % Sicherheit? | Aus der gemessenen Rate je Netz: Median der Netze **1** (Kreis, Baum), **4** (skalenfrei), **8** (Zufallsnetz Grad 3, Verbundnetz), **11** (Gitter), **16** (Zufallsnetz Grad 5), **17** (Ring); im schlechtesten Netz geschätzt **42** (Zufallsnetz Grad 5; hochgerechnet aus 400 Läufen je Netz, jeder kleinste Schnitt zählt als Treffer); die Schranke für einen bestimmten Schnitt verlangt **551**. |
| Was kostet Stoer–Wagner gegen Karger? (Zufallsnetz Grad 5, vier Netze je Größe) | Bei 20 / 40 / 80 Standorten **19 / 39 / 79** Phasen und **1.330 / 10.660 / 85.320** Matrixzugriffe (genau (n + 1) n (n − 1) / 6); ein Lauf von Karger **25,5 / 61,1 / 142,9** Kantenprüfungen. Bis 99 % Sicherheit rechnet die Schranke mit **873 / 3.590 / 14.551** Läufen, gemessen genügen im Mittel über vier Netze je Größe **10 / 8,5 / 14** (Streuung zwischen den Netzen nicht angegeben). Matrixzugriffe und Kantenprüfungen sind verschiedene Einheiten: verglichen werden die Läufe. |
| Das Lehrbeispiel von Hand? | Zwei Werke, 8 Standorte, 14 Leitungen: kleinster Schnitt **2** (A–E, A–F, einziger), kleinster Standort **3**, sieben Phasen mit **84** Matrixzugriffen; ein Lauf von Karger trifft ihn in 227 von 1.000 Läufen (Schranke 0,036), für 99 % genügen gemessen 18 Läufe, die Schranke verlangt 127. |
| Ist die Rechnung korrekt? | Der Wert von Stoer–Wagner gleich `networkx.stoer_wagner` auf **60** festen Netzen (acht Netztypen, gleiche und zufällige Gewichte) und gleich `networkx.edge_connectivity` bei gleichen Gewichten; kleinster Wert und Zahl aller kleinsten Schnitte gleich der Aufzählung aller Zweiteilungen (`tests/test_oracle_globaler_schnitt.py`); jede Karger-Verteilung auf kleinen Netzen exakt über alle Kantenreihenfolgen, jeder kleinste Schnitt mit Wahrscheinlichkeit mindestens 2 / (n (n − 1)); Skalieren der Gewichte, Umnummerieren und eine zusätzliche Leitung ändern nichts Unerwartetes. |

## Ehrliche Grenzen

- **Kleiner Schnitt heißt nicht ausgewogen.** Der kleinste Schnitt trennt auf den dünnen Modellnetzen (Zufallsnetz, Gitter, Ring, skalenfreies Netz) fast immer nur einen Standort ab, auf Kreis, Baum und Verbundnetz nicht; wer ein Netz in große Teile teilen will, braucht eine Bedingung an die Größe der Seiten (nicht Thema dieses Stücks).
- **Die Modellnetze sind dünn.** Zufallsbaum plus Zusatzleitungen hat einen kleinen Mindestgrad; wie oft der kleinste Schnitt auf dichten, regelmäßigen Netzen eine echte Teilung ist, zeigt nur das Verbundnetz (nicht auf anderen Netzen gemessen), und auch dort nur bei dieser Größe und diesem Regionsgrad (16 Standorte, Grad 5, eine Leitung zwischen den Regionen).
- **Karger in der einfachen Form.** Verbesserte Varianten (rekursive Kontraktion) und die schnellsten Verfahren der Theorie sind nicht gebaut; sie stehen nur als Einordnung in der Formulierung.
- **Aufzählung nur bis 16 Standorte** (2^(n−1) Zweiteilungen); darüber zeigt die App Stoer–Wagner und Karger ohne die Zahl aller kleinsten Schnitte.
- **Ein globaler Schnitt, nicht alle Paare.** Alle Paare als Baum zeigt `gomory-hu-demo`; Zusammenhang über disjunkte Wege `menger-demo`.
- **Ungerichtetes Netz.** Für gerichtete Netze ist der kleinste Schnitt ein anderes Problem.
- **Aufwand gezählt, nicht gemessen.** Matrixzugriffe und Kantenprüfungen sind verschiedene Einheiten; ein Vergleich in Sekunden fehlt bewusst.
- **Größe:** bis 80 Standorte (das Gitter bis 81), bis 3.000 Läufe.

## Tests

Das Verzeichnis `tests/` enthält zurzeit 165 Tests (Laufzeit etwa eine Minute auf dem Entwicklungsrechner):

- **Kern** (`test_algorithm.py`): jede Einheit an von Hand gerechneten Mini-Netzen (Pfad, Kreis, vollständiges Netz, Stern, zwei Werke, gewichtetes Dreieck): Stoer–Wagner Phase für Phase (Ordnung, Bindungen, Schnitt der Phase, Matrixzugriffe), Karger mit fester Zufallsquelle (Kontraktionen, Gewichte, übersprungene Leitungen), exakte Verteilung auf Pfad und Kreis, Aufzählung aller kleinsten Schnitte.
- **Szenarien** (`test_scenario.py`): einfach, zusammenhängend, deterministisch für jeden Netztyp und jede Gewichtung; Größen (Gitter, skalenfreies Netz, Regionen, Kreis, Baum, Lehrbeispiel).
- **Orakel** (`test_oracle_globaler_schnitt.py`): `networkx.stoer_wagner` und `edge_connectivity`, die Aufzählung, die exakte Verteilung von Karger (jeder kleinste Schnitt mindestens 2 / (n (n − 1)), der Kreis genau), eine Stichprobe auf dem Kreis gegen die Formel (vier Standardfehler); Eigenschaften (Gewichte skalieren, Umnummerieren, Leitung hinzufügen, kleinster Schnitt höchstens der kleinste Standort).
- **Randfälle** (`test_edge_cases.py`): ein Standort, zwei Standorte mit und ohne Leitung, Gewicht 0, zwei und drei Komponenten, vollständiges Netz, Doppelleitungen, Hantel, kleinste und größte Netzgröße je Netztyp und Gewichtung, Reglerextreme.
- **Zweige** (`test_branches.py`): jedes Preset löst seine Beschreibung ein und jede Abbildung rendert; **Auswertung und Verdikte** (`test_evaluation.py`, `test_verdicts.py`) an handgesetzten Werten; **Befunde** (`test_claims.py`) für jede Zahl dieses README.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), Layout (Schnellstart oben, aktives Preset hervorgehoben), Footer, Laufzeit-Importe.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Stoer–Wagner (Phasen), Karger (Kontraktion, Läufe), alle kleinsten Schnitte, fünf Experimente |
| `requirements-dev.txt` | Laufzeit plus pytest und networkx (Gegenproben) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `gsc_algorithm.py` | Kern: Stoer–Wagner, Karger, Aufzählung, exakte Verteilung |
| `gsc_constants.py` | Regler-Grenzen, Netztypen, Raster der Experimente, Farben, Presets |
| `gsc_evaluation.py` | Analyse, Prüfung vor der Anzeige, Verdikte |
| `gsc_experiments.py` | Experimente über feste Netze |
| `gsc_layout.py` | Fester Kopf (Stylesheet) |
| `gsc_presets.py` | Permalink, Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `gsc_scenario.py` | Netze: Lehrbeispiel, Kreis, Baum, Zufallsnetz, Gitter, Ring, skalenfreies Netz, Verbundnetz, Gewichte, Karte |
| `gsc_visualization.py` | Plotly-Abbildungen (Karten mit Schnitt, Phasen und Kontraktionen, Verteilungen, Experimente; Achsen gesperrt) |
| `tests/` | Mini-Netze, Orakel, Randfälle, Zweige, Verdikte, Befunde, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Cactus-Darstellung aller kleinsten Schnitte, rekursive Kontraktion und die deterministischen Rekordverfahren:** nur als Einordnung in der Formulierung.
- **Gerichtete Netze, kleinster Schnitt für jedes Paar:** siehe `edmonds-karp-demo`, `gomory-hu-demo`.
- **Echte Netze oder Dateiimport:** die Netze sind synthetisch.
- **Messung der Laufzeit:** gezählt werden Matrixzugriffe und Kantenprüfungen.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
