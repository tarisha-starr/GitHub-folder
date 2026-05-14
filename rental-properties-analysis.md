# Rental Properties Analysis — Titirangi & Green Bay (4+ bedrooms)

## Source
TradeMe NZ — direct filtered search URLs:
- Titirangi 4+ bed: https://www.trademe.co.nz/a/property/residential/rent/auckland/waitakere-city/titirangi/search?bedrooms_min=4
- Green Bay 4+ bed: https://www.trademe.co.nz/a/property/residential/rent/auckland/waitakere-city/green-bay/search?bedrooms_min=4

## Important note on data
TradeMe blocks automated scraping (HTTP 403), so the spreadsheet (`rental-properties-analysis.csv`) contains **real listing URLs and addresses** discovered via web search, but the per-listing details (bedrooms, weekly rent, bond, bathrooms, available date, pets, etc.) **could not be auto-extracted**. Each row is marked "Needs manual check" in the Verification Status column.

To finish the analysis you have two options:
1. Open each URL in a browser and fill the row in.
2. Paste the HTML (or screenshots) of each listing page back to me — I'll extract the fields and update the CSV.

## Columns captured
| Column | Why it matters |
|---|---|
| Suburb | Titirangi vs Green Bay |
| Address | Specific street — useful for commute / school zoning |
| Listing URL | Direct link to TradeMe listing |
| Bedrooms | Must be 4+ |
| Bathrooms | Comfort / household size |
| Parking | Off-street/garage spaces |
| Property Type | House / townhouse / unit |
| Weekly Rent (NZD) | Primary cost |
| Bond (NZD) | Usually 4 weeks rent — upfront cost |
| Available From | Move-in date |
| Pets Allowed | Filter if relevant |
| Heating | Heat pump / fireplace / none — matters in Auckland winters |
| Garden/Section | Yard size |
| Furnished | Yes / Partial / No |
| Listing Agent | Property manager contact |
| Features/Notes | Views, decks, schools, etc. |
| Verification Status | Whether the row data has been confirmed |

## Listings to verify
See `rental-properties-analysis.csv`. Eight candidate URLs are seeded (6 Titirangi, 2 Green Bay). One (Golf Road, Titirangi) is flagged as likely NOT 4+ bed based on the search snippet — verify before discarding.
