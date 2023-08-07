# ~~Fast Scanner (Reverse-engineered Skyscanner API)~~ (OUTDATED)

**EDIT**: The api was changed, so this won't work anymore and I'm too lazy to keep adapting this project to each api change. Feel free to experiment with their latest api which accepts POST requests. `https://www.skyscanner.net/g/radar/api/v2/web-unified-search/``

The payload for Lithuania Anytime-Anywhere:

payload = {"cabinClass":"ECONOMY","childAges":[],"adults":1,"legs":[{"legOrigin":{"@type":"entity","entityId":"29475240"},"legDestination":{"@type":"everywhere"},"dates":{"@type":"anytime"}},{"legOrigin":{"@type":"everywhere"},"legDestination":{"@type":"entity","entityId":"29475240"},"dates":{"@type":"anytime"}}]}

Figure the headers out yourself in your network tab in your browser dev tools.

## What does it do?

This program generates cheapest flights in a standard format, using the dates FROM: `ANYTIME` TO: `ANYTIME`.

Also, it can extensively scan the full Skyscanner calendar (you know where you have to click a day and see the prices) for a specific flight and return the full list of all available flights, sorted by price. To do that, set `calendar_scan` parameter to `True`.

## Install

Just run the file like any other Python main.py

If you want to import it to your project, delete two last lines, change the filename and import it with `from filename import FastScanner`