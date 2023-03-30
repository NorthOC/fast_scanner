# Fast Scanner (Reverse-engineered Skyscanner API)

Skyscanner has removed my favorite feature - searching by cheapest month. With a little bit of API reverse-engineering, I bring it back and... ADD SOME BADASS FUNCTIONALITY!

## What does it do?

This program generates cheapest flights in a standard format, using the dates FROM: `ANYTIME` TO: `ANYTIME`.

Also, it can extensively scan the full Skyscanner calendar (you know where you have to click a day and see the prices) for a specific flight and return the full list of all available flights, sorted by price. To do that, set `calendar_scan` parameter to `True`.

## Install

Just run the file like any other Python main.py

If you want to import it to your project, delete two last lines, change the filename and import it with `from filename import FastScanner`