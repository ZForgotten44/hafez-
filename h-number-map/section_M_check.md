# Section M: why the route legend says H002587 and the index said H002589

Checked against three sources: the numbering table (`H-Tables/cedar_grove_section_M_h_table.csv`), the burial-record workbook (`Section M.xlsx`, lot and grave IDs only), the 2022 drawing, and the old Section M sheet (`Cemetery Map - All Sections on Individual Pages`, page 9).

| Source | Section M lots |
|---|---|
| Numbering table | 249 (H002587 to H002835) |
| Burial records | 252 |
| 2022 drawing | 246 outlines carry a table number, plus 6 outlines/labels the table lacks |

**Three numbers have no lot.** M 11 (H002587), M 12 (H002588) and M 16 (H002591) are in the table. The old Section M sheet draws lots 11 and 12 at the east tip and lot 16 under 15. The 2022 drawing has no lots there (a Saint Joseph hexagon marker stands where 11 and 12 were), and the burial records have no lot 11, 12 or 16 at all (the records start at lot 14). So the route legend (H002587) follows the table, and the index (H002589) followed what is drawn.

**Six real lots have no number.** M 56, 57, 62, 63, 68, 69 are in the burial records and in the 2022 drawing (a second row below the columns 52-55, 58-61 and 64-67, around x 1235-1254, y 329-341) but not in the numbering table. They are drawn grey on the maps and show as "6 drawn lots have no H-number yet" in the index.

Sections J (132 lots) and K (115 lots) match their tables exactly in drawing and in records; no discrepancy there.

## What was not changed

No decoder record, H-number or grave ID was changed. The six lots need numbers, and there are two ways to give them, which differ in what else moves:

1. **Append**: H003186 to H003191 for 56, 57, 62, 63, 68, 69. Nothing else moves. The three unused numbers (H002587, H002588, H002591) stay reserved or are retired.
2. **Insert in route order**: 56 and 57 after 55, 62 and 63 after 60, 68 and 69 after 67 (the route order inside M's columns is a stored list, so these points are my reading). Every later number moves, including Sections K, J, I and L (350 lots), and the formula, explainer, atlas and 3D model have to be rebuilt together.

Occupant names are keyed by section, lot and grave (`CEDARGROVE-M-<lot>-<grave>`), not by H-number, so a decoder change moves H-numbers but cannot move a name.
