# Sources for E.H. Jennings Research

Replaces the old `sources_urls.md` and `problematic_urls.md`, which had drifted
out of sync with each other (most notably on the Jan 22, 1910 Spokane Press
article — one file called it confirmed, the other flagged it as having OCR
problems). Every source now lives in one table with an explicit tier and
status, so confidence level is visible at a glance instead of split across
files.

**Tier key:**
- **Primary** — direct scan of a historical record (loc.gov/Chronicling America, court filing, NRHP nomination)
- **Genealogy aggregator** — Ancestry/FamilySearch/Find a Grave; usually a transcription or index entry, not the record image itself
- **Secondary** — modern third-party account (local history blogs, county library posts) not itself a primary record

**Status key:**
- **Confirmed** — primary text directly verified, matches the fact as stated
- **Confirmed (caveat)** — verified, but with a known reading/OCR problem noted
- **Unconfirmed** — could not verify E.H. Jennings-specific text on the cited page; treat the fact as unestablished until re-checked
- **Uncitable** — link points at a homepage/search page, not the specific record; needs replacing with a permalink

| # | Fact | Source | Tier | Status | Confirm. count | Notes |
|---|------|--------|------|--------|----------------|-------|
| 1 | Birth 1852, death 1923, burial Homewood Cemetery; parent/sibling/child/spouse links | [Find a Grave memorial](https://www.findagrave.com/memorial/90963809/edward-henry-jennings) (accessed Jul 11, 2025) | Genealogy aggregator | Confirmed | 1 | Specific record page, not homepage — good citation practice, keep as model for others below |
| 2 | 1910 sentencing postponed; cited family illness | [Palestine Daily Herald, May 14, 1910](https://chroniclingamerica.loc.gov/lccn/sn86088268/1910-05-14/ed-1/seq-1/) | Primary | Confirmed | 1 | |
| 3 | Oil leases, Tyler County WV, 1,065 acres (Lemasters/Hough/Parks/Hardman) | [Sistersville Oil Review, Oct 19, 1898](https://chroniclingamerica.loc.gov/lccn/sn86092351/1898-10-19/ed-1/seq-1/) | Primary | Confirmed | 1 | |
| 4 | Arrest in Pittsburgh graft scandal; bail $10,000–$15,000; Columbia National Bank/Pure Oil/Colonial Trust/Jennings Bros. titles | [Spokane Press, Jan 22, 1910, p.3](https://www.loc.gov/resource/sn88085947/1910-01-22/ed-1/?sp=3&q=e+h+jennings&r=-0.048,0.022,0.703,0.409,0) | Primary | **Confirmed (caveat)** | 1 | Earlier analysis had OCR/reading trouble on this page before the scandal details were confirmed — re-verify OCR text directly before quoting specifics (dollar figures especially) |
| 5 | Investment in PA refining facilities | [The Daily Notes, Sep 18, 1925](https://chroniclingamerica.loc.gov/lccn/sn86083365/1925-09-18/ed-1/seq-5/) | Primary | **Unconfirmed** | 0 | Downgraded from the old file's "confirmed" — direct review found no E.H. Jennings text on this page. Don't cite as established until re-checked |
| 6 | Gas exploration partnership, Fayette County PA | [The Morning Herald, Apr 3, 1928](https://chroniclingamerica.loc.gov/lccn/sn86083369/1928-04-03/ed-1/seq-7/) | Primary | **Unconfirmed** | 0 | Same issue as #5 — no direct match found on page. Downgraded |
| 7 | McDonald oil field development (Jennings Bros. drilling) | [Pittsburg Dispatch, Dec 31, 1892](https://chroniclingamerica.loc.gov/lccn/sn84024546/1892-12-31/ed-1/seq-12/) | Primary | Confirmed | 1 | |
| 8 | Smathers v. E.H. Jennings, NC civil suit | [Jackson County Journal, Apr 17, 1914](https://chroniclingamerica.loc.gov/lccn/sn91068765/1914-04-17/ed-1/seq-7/) | Primary | Confirmed | 1 | |
| 9 | Son E.H. Jennings Jr.'s obituary; father's legacy in Pure Oil/Federal Oil/Transylvania Syndicate | [Evening Star, Sep 4, 1931](https://chroniclingamerica.loc.gov/lccn/sn83045462/1931-09-04/ed-1/seq-4/) | Primary | Confirmed — **verify wording before any reuse** | 1 | This is the page a prior AI session fabricated details on ("age 61," "brief illness"). Only cite what you can re-read directly on the page; do not carry forward any prior transcription of this article without re-verifying it character-for-character |
| 10 | Marriages/births incl. Richard Gundry Jennings (1880) | [Ancestry.com](https://www.ancestry.com/) (accessed Jul 11, 2025) | Genealogy aggregator | **Uncitable** | — | Points at homepage, not the record. Replace with the actual record URL, or note explicitly "record behind paywall, described from memory, needs re-check" |
| 11 | Richard Gundry's education (Shadyside Academy, Yale 1903), descendants | [FamilySearch](https://www.familysearch.org/) (accessed Jul 11, 2025) | Genealogy aggregator | **Uncitable** | — | Same fix needed as #10 |
| 12 | 1911 purchase of Toxaway Co. for $100,000; NC lumber/resort context | [NRHP Nomination, Toxaway](https://npgallery.nps.gov/AssetDetail/NRIS/88000032) (accessed Jul 11, 2025) | Primary (federal nomination document) | Confirmed | 1 | |
| 13 | 1916 dam failure details | [greetingsfromthepast.com](https://www.greetingsfromthepast.com/2019/10/toxaway-falls-and-the-toxaway-dam-break/) | Secondary | Unverified against primary record | — | Not loc.gov; useful for narrative context only, don't treat as a primary-source fact until cross-checked against a contemporary newspaper account |
| 14 | 1916 flood context/legacy | [thelaurelofasheville.com](https://thelaurelofasheville.com/lifestyle/history-feature-a-legacy-washed-away-lake-toxaways-1916-flood/) | Secondary | Unverified against primary record | — | Same caveat as #13 |
| 15 | Post-1916 aftermath | [library.transylvaniacounty.org](https://library.transylvaniacounty.org/the-toxaway-inn-part-two-aftermath/) | Secondary | Unverified against primary record | — | Same caveat as #13 |
| 16 | Dam burst historical account | [historictoxaway.org](https://historictoxaway.org/lake-toxaway-dam-burst/) | Secondary | Unverified against primary record | — | Same caveat as #13 |
| 17 | 1916 flood local records | [library.transylvaniacounty.org/1916-flood](https://library.transylvaniacounty.org/1916-flood/) | Secondary | Unverified against primary record | — | Same caveat as #13 |

## Adding new sources

Append a new row with all six columns filled in — don't add a fact without a
tier and status, since that's exactly what let #4 through #6 above go out of
sync in the old two-file system. If you can't determine tier/status yet, use
`Primary` / `Unconfirmed` as the safe default rather than leaving it blank.

Future additions go below this line:
