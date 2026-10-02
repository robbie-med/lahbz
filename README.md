# lahbz: Labcorp lab-ordering reference

Reference data for clinicians ordering labs in Cerner after Labcorp took over the former RML (Regional Medical Laboratory, Tulsa) and Ascension's Oklahoma lab outreach.

- `cerner_to_labcorp.md`: Cerner order names (from search screenshots) mapped to the old RML / Labcorp Oklahoma catalog name and order code, plus the Labcorp national test name and 6-digit code.
- `data/rml_labcorp_oklahoma_catalog_2026-10-02.json`: snapshot of the full RML / Labcorp Oklahoma test directory (rml.labcatalog.net, 2,783 test pages). Cerner's "Reference Information" links point to this site, and the site posted a shutdown notice for Oct 1, 2026.
- `data/labcorp_national_menu_2026-10-02.json`: snapshot of Labcorp's public national test menu (labcorp.com/tests, 3,667 tests).
- `scripts/`: the scrapers and parsers used to build the above.

Not yet included: the clinic's "cannot be drawn here" list, and confirmed Cerner names for every orderable.
