# lahbz: Labcorp lab-ordering reference

Reference data for clinicians ordering labs in Cerner after Labcorp took over the former RML (Regional Medical Laboratory, Tulsa) and Ascension's Oklahoma lab outreach.

- `cerner_to_labcorp.md`: Cerner order names (from search screenshots) mapped to the old RML / Labcorp Oklahoma catalog name and order code, plus the Labcorp national test name and 6-digit code.
- `data/rml_labcorp_oklahoma_catalog_2026-10-02.json`: snapshot of the full RML / Labcorp Oklahoma test directory (rml.labcatalog.net, 2,783 test pages). Cerner's "Reference Information" links point to this site, and the site posted a shutdown notice for Oct 1, 2026.
- `data/labcorp_national_menu_2026-10-02.json`: snapshot of Labcorp's public national test menu (labcorp.com/tests, 3,667 tests).
- `tool/`: the Lab Order Finder page (`index.html`) and its data (`data.json`, built by `scripts/build_tool_data.py`). Published at https://claude.ai/artifact/WVj1fg4yfuvkUjc4qH9j18
- `scripts/`: the scrapers and parsers used to build the above.

To finish "where to draw": set `CLINIC_CAN` in `scripts/build_tool_data.py` from the lab tech's answers (centrifuge, freezer, ice, 37°C warming, courier times) and rebuild. Cerner names are confirmed only for orders seen in screenshots; an IT order-catalog export would fill in the rest.
