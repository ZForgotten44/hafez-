# Section M: numbering v2 (route order) and what is still open

## 1. The six lots: M 56, 57, 62, 63, 68, 69

**Evidence they are real.** Burial workbook (`Section M.xlsx`): each has 4 graves, like their neighbours 55, 61 and 67. The 2022 drawing: outlined cells with these labels at x 1235-1254, y 329-341, a second row directly south of the columns 52-55, 58-61 and 64-67. The old Section M sheet draws no lots there (six empty boxes of the old parking layout stand in that corner), so these lots were added after the old sheet and never numbered. Annotated side by side: `jon_questions/M_six_lots.png`.

**Physical row and direction.** M is a curved strip of columns; the route walks each column north to south (y increasing) and the columns run east to west (x decreasing). The six lots extend three columns by two lots each at the south end:

| Column (x) | Lots in route order (v2) | New lots |
|---|---|---|
| 1255 | 52, 53, 54, 55, **56, 57** | 56, 57 |
| 1246 | 61, **62, 63**, then 58, 59, 60 | 62, 63 |
| 1236 | 66, 67, **68, 69**, then 64, 65 | 68, 69 |

**Why those positions (neighbouring lots, measured in drawing units).**
- 55 to 56: 11; 56 to 57: 11; 57 to 61: 26 (was 55 to 61: 9). The verified lots around the insertion are 55 before and 61 after.
- 61 to 62: 12; 62 to 63: 11; 63 to 58: 62 (was 61 to 58: 40, a column wrap like the other wraps of 62 to 65 in this strip). Verified: 61 before, 58 after.
- 67 to 68: 12; 68 to 69: 11; 69 to 64: 63 (was 67 to 64: 40). Verified: 67 before, 64 after.
Each new lot continues straight south from the lot it stands below, with a step of 11-12 units, the same as the 11-14 units between lots inside the columns. The alternative of putting 62, 63 after 60 costs a longer step and was rejected.

**The stored list.** The old stored list for M's first 51 lots goes 52, 53, 54, 55, 61, 58, 59, 60, 66, 67, 64, 65. Its quirk (the south lot of the next column is visited first) is unchanged, because the lots after it were numbered that way in v1 and nothing contradicts it. Only the six lots are inserted.

**Result (v2).**

| Lot | H-number | Lot | H-number |
|---|---|---|---|
| 56 | H002618 | 62 | H002621 |
| 57 | H002619 | 63 | H002622 |
| 61 | H002620 | 68 | H002628 |
| 58 | H002623 | 69 | H002629 |
| 64 | H002630 | 279 | H002841 |

Everything up to H002617 (M 55) is unchanged. M 61 and later move by +2, +4 and +6. M ends at H002841 (was H002835). Sections K, J, I and L start six numbers later: K H002842 to H002956, J H002957 to H003088, I H003089 to H003152, L H003153 to H003191.

## 2. M 11, 12, 16 (H002587, H002588, H002591): still open

Sources checked: the numbering table; `Section M.xlsx` (lot IDs, owner and reserved-for columns: no lot 11, 12 or 16, no mention of them); the 2022 drawing; the old Section M sheet; every file in the repository for the H-IDs `H002587`, `H002588`, `H002591` (they occur only in our own generated lists). No plat, revision note or ownership or reservation record for them is in the repository. The old sheet draws them at the east tip (11 and 12 side by side east of 14 and 15, 16 under 15); in 2022 a Saint Joseph hexagon marker stands in the 11/12 spot and parking stripes and a hatched building fill the 12/16 area (`jon_questions/M_east_tip.png`).

The sources are inconclusive, so **no number was removed**: M 11, 12 and 16 keep H002587, H002588 and H002591 (`M_EASTTIP_STATUS = 'active'` in `s4/s4decoder1.py`), which are listed as numbers with no lot drawn. The question for Jon is in `jon_questions/QUESTIONS.md`. If he confirms they were withdrawn, set `M_EASTTIP_STATUS = 'withdrawn'` and rebuild; K starts at H002839 and L ends at H003188 (net +3). `crosswalk/crosswalk_v1_to_v2_if_east_tip_withdrawn.csv` is already generated for that case, with the three lots listed as retired and their old IDs kept. If an east-tip lot was renumbered, the same switch is extended with an alias.

| Jon's answer | Active M lots | K, J, I, L start |
|---|---|---|
| All three still recognized (default shipped) | 255 | six later (H002842) |
| All three withdrawn | 252 | three later (H002839) |

## 3. Burial records

`Section M.xlsx` keys every grave by section, lot and grave (`CEDARGROVE-M-56-3-`), not by H-number. The new H-ID is derived from that key by the decoder, so a person recorded in M lot 56, grave 3 resolves to H0026183 and stays in the same grave. No evidence was found (and none exists in the repository for sections A to I and L) that any name was assigned one grave too early, so no placement was corrected. `crosswalk/records_h_ids_v2.csv` lists every workbook grave of J, K and M with its old and new H-ID and no names. Sections J and K match their numbering tables lot for lot; the workbook grave counts per lot exceed the six grave columns of the published tables in a few lots (M 270 has 7 graves, K 5 has 9): the decoder accepts graves 1 to 9, so those IDs resolve.
