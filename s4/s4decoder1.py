"""
Cedar Grove Cemetery — H-Number Decoder
========================================
Sections A, B, C, D combined sweep.

TWO PASSES — each pass interleaves two sections column by column:

  PASS 1 — B + A   H000001 … H000836
    col 1-B → col 1-A → col 2-B → col 2-A → … → col 22-B → col 22-A

  PASS 2 — D + C   H000837 … H001672
    col 1-D → col 1-C → col 2-D → col 2-C → … → col 22-D → col 22-C

Within each column:  lots BOTTOM → TOP   (r=1 = bottom row)
Within each lot:     graves TOP → BOTTOM (grave 1 = top of lot)

FORMULA
  PASS 1:  H(B, lot) = SWEEP×(r−1) + c
           H(A, lot) = SWEEP×(r−1) + N_B + c
  PASS 2:  H(D, lot) = OFFSET + SWEEP×(r−1) + c
           H(C, lot) = OFFSET + SWEEP×(r−1) + N_D + c
  GRAVE:   H_grave   = H_lot × 10 + grave_number

CONSTANTS:
  N_B = N_A = N_D = N_C = 22
  SWEEP  = 44   ROWS = 19   OFFSET = 836

KEY ANCHORS:
  B-20H = H000001   A-1 = H000044
  D-1U  = H000837   C-417 = H001672
"""

import csv, os

N_B = N_A = N_D = N_C = 22
SWEEP  = N_B + N_A   # 44
ROWS   = 19
OFFSET = SWEEP * ROWS  # 836

# ── Pass 3 constants: F + E ───────────────────────────────────────
# Sweep: F col 1 → E col 1 → F col 2 → E col 2 → … → F col 18 → E col 22
# N_F=18, N_E=22, SWEEP_EF=40, ROWS_EF=12 (F only has 11 rows)
# OFFSET_EF = OFFSET*2 + 0  (follows immediately after D/C pass)
N_F       = 18
N_E       = 22
SWEEP_EF  = N_F + N_E    # 40
ROWS_EF   = 12            # E has 12 rows, F has 11 (r=12 in F is empty)
# OFFSET_EF is set after _build_dc_tables() below


# ── Section B ────────────────────────────────────────────────
def build_B_decoder():
    d = {}
    for r in range(1, ROWS+1):
        d[f"{20*r}H"] = (1, r)
    d["19A"] = (2, 1)
    for r in range(2, ROWS+1):
        d[str(19 + 20*(r-1))] = (2, r)
    for r in range(1, ROWS+1):
        for c in range(3, 22):
            d[str((r-1)*20 + (22-c))] = (c, r)
    for r in range(1, ROWS+1):
        d[str(12 + 19*(r-1))] = (22, r)
    return d


# ── Section A ────────────────────────────────────────────────
def build_A_decoder():
    d = {}
    for r in range(1, ROWS+1):
        b = 19*(r-1)
        d[str(19+b)]=(1,r);  d[str(18+b)]=(2,r);  d[str(17+b)]=(3,r)
        d[str(16+b)]=(4,r);  d[str(15+b)]=(5,r);  d[str(14+b)]=(6,r)
        d[f"{13+b}H"]=(7,r); d[str(13+b)]=(8,r);  d[str(12+b)]=(9,r)
        d[str(11+b)]=(10,r); d[str(10+b)]=(11,r)
        d[str(9+b)] =(12,r); d[str(8+b)] =(13,r); d[str(7+b)] =(14,r)
        d[str(6+b)] =(15,r); d[f"{5+b}H"]=(16,r); d[str(5+b)] =(17,r)
        d[str(4+b)] =(18,r); d[str(3+b)] =(19,r); d[str(2+b)] =(20,r)
        d[f"{1+b}H"]=(21,r); d[str(1+b)] =(22,r)
    return d



# ── Sections D + C — table-driven from exact map data ────────────────
# Sweep: D row r first, then C row r, for r = 1..24
# Row widths vary — no fixed SWEEP constant for D/C.
OFFSET_DC = OFFSET  # 836

_D_ROWS = {
    1:  ['1U','1T','1S','1R','1Q','1P','1O','1N','1M','1L','1K','1J','1I','1H',
         '20','19','18','17','16','15','14','13','12','11','10','9','8','7','6','5','4','3','2','1',
         '1A','1B','1C','1D','1E','F1','1G','1H_2','1I_2'],
    2:  ['20H','40','39','38','37','36','35','34','33','32','31','30','29H','29','28','27','26','25','24','23','22','21'],
    3:  ['40H','60','59','58','57','56','55','54','53','52','51','50','49H','49','48','47','46','45','44','43','42','41'],
    4:  ['60H','80','79','78','77','76','75','74','73','72','71','70','69H','69','68','67','66','65','64','63','62','61'],
    5:  ['80H','100','99','98','97','96','95','94','93','92','91','90','89H','89','88','87','86','85','84','83','82','81'],
    6:  ['100H','120','119','118','117','116','115','114','113','112','111','110','109H','109','108','107','106','105','104','103','102','101'],
    7:  ['120H','140','139','138','137','136','135','134','133','132','131','130','129H','129','128','127','126','125','124','123','122','121'],
    8:  ['140H','160','159','158','157','156','155','154','153','152','151','150','149H','149','148','147','146','145','144','143','142','141'],
    9:  ['160H','180','179','178','177','176','175','174','173','172','171','170','169H','169','168','167','166','165','164','163','162','161'],
    10: ['180H','200','199','198','197','196','195','194','193','192','191','190','189H','189','188','187','186','185','184','183','182','181'],
    11: ['200H','220','219','218','217','216','215','214','213','212','211','210','209H','209','208','207','206','205','204','203','202','201'],
    12: ['220H','240','239','238','237','236','235','234','233','232','231','230','229H','229','228','227','226','225','224','223','222','221'],
    13: ['240H','260','259','258','257','256','255','254','253','252','251','250','249H','249','248','247','246','245','244','243','242','241'],
    14: ['260H','280','279','278','277','276','275','274','273','272','271','270','269H','269','268','267','266','265','264','263','262','261'],
    15: ['280H','300','299','298','297','296','295','294','274','292','291','290','289H','289','288','287','286','285','284','283','282','281'],
    16: ['311H','310','309','308','307','306','305','304','303','302','301','420','419','418','417','416','415','414','413','412'],
    17: ['322H','321','320','319','318','317','316','315','314','313','312','411','410','409','408','407','406','405','404','403'],
    18: ['333H','332','331','330','329','328','327','326','325','324','323','402','401','400','399','398','397','396','395','394'],
    19: ['344H','344','343','342','341','340','339','338','337','336','335','334','393','392','391','390','389','388','387','386','385'],
    20: ['355H','355','354','353','352','351','350','349','348','347','346','345',
         '384','383','382','381','380','379','378','377','376'],  # double-row pairs
    21: ['366H','366','365','364','363','362','361','360','359','358','357','356',
         '375','374','373','372','371','370','369','368','367'],  # double-row pairs
    22: ['541','540','539','538','537','536','535','534','533','532','531','530',
         '529','528','527','526','525','524','523','522','521'],
    23: ['520','519','518','517','516','515','514','513','512','511','510',
         '509','508','507','506','505','504','503','502','501','500'],
}

_C_ROWS = {
    1:  ['19','18','17','16','15','14','13','12','11','10','9H','9','8','7','6','5H','5','4','3','2','1'],
    2:  ['38','37','36','35','34','33','32H','32','31','30','29','28','27','26','25','24H','24','23','22','21','20'],
    3:  ['57','56','55','54','53','52','51H','51','50','49','48','47H','47','46','45','44','43H','43','42','41','40','39'],
    4:  ['76','75','74','73','72','71','70','69','68','67','66H','66','65','64','63','62H','62','61','60','59','58'],
    5:  ['95','94','93','92','91','90','89','88','87','86','85H','85','84','83','82','81H','81','80','79','78','77'],
    6:  ['114','113','112','111','110','109','108H','108','107','106','105','104H','104','103','102','101','100H','100','99','98','97','96'],
    7:  ['133','132','131','130','129','128','127H','127','126','125','124','123H','123','122','121','120','119H','119','118','117','116','115'],
    8:  ['152','151','150','149','148','147','146H','146','145','144','143','124H','142','141','140','139','138H','138','137','136','135','134'],
    9:  ['171','170','169','168','167','166','165H','165','164','163','162','161','160','159','158','157','156','155','154','153'],
    10: ['190','189','188','187','186','185','184H','184','183','182','181','180H','180','179','178','177','176H','176','175','174','173','172'],
    11: ['209','208','207','206','205','204','203H','203','202','201','200','199H','199','198','197','196','195H','195','194','193','192','191'],
    12: ['228','227','226','225','224','223','222H','222','221','220','219','218','217','216','215','214','213','212','211','210'],
    13: ['247','246','245','244','243','242','241','241H','240','239','238','237','236','235','234','233H','233','232','231','230','229'],
    14: ['263C','263B','263A','263','262','261','260H','260','259','258','257','256H','256','255','254','253','252H','252','251','250','249','248'],
    15: ['279C','279B','279A','279','278','277','276','276H','275','274','273','272H','272','271','270','269','268H','268','267','266','265','264'],
    16: ['295C','295B','295A','295','294','293','292H','292','291','290','289','288H','288','287','286','285','284H','284','283','282','281','280'],
    17: ['311C','311B','311A','311','310','309','308H','308','307','306','305','304H','304','303','302','301','300H','300','299','298','297','296'],
    18: ['330','329','328','327','326','325','324H','324','323','322','321','320H','320','319','318','317','316','316H','315','314','313','312'],
    19: ['349','348','347','346','345','344','343','343H','342','341','340','339H','339','338','337','336','335','335H','334','333','332','331'],
    20: ['368','367','366','365','364','363','362H','362','361','360','359','358H','358','357','356','355','354','354H','353','352','351','350'],
    21: ['384C','384B','384A','384','383','382','381H','381','380','379','378','377H','377','376','375','374','373','373H','372','371','370','369'],
    22: ['400C','400B','400A','400','399','398','397','397H','396','395','394','393H','393','392','391','390','389','389H','388','387','386','385'],
    23: ['416C','416B','416A','416','415','414','413H','413','412','411','410','409H','409','408','407','406','405','405H','404','403','402','401'],
    24: ['432C','432B','432A','432','431','430','429','429H','428','427','426','425H','425','424','423','422','421','421H','420','419','418','417'],
}


def _build_dc_tables():
    D_LOT_H, C_LOT_H, DC_H_LOT = {}, {}, {}
    h = OFFSET_DC
    for r in range(1, max(max(_D_ROWS), max(_C_ROWS)) + 1):
        for lot in _D_ROWS.get(r, []):
            h += 1
            if lot not in D_LOT_H:
                D_LOT_H[lot] = h
            DC_H_LOT[h] = ('D', lot)
        for lot in _C_ROWS.get(r, []):
            h += 1
            if lot not in C_LOT_H:
                C_LOT_H[lot] = h
            DC_H_LOT[h] = ('C', lot)
    return D_LOT_H, C_LOT_H, DC_H_LOT, h


_D_LOT_H, _C_LOT_H, _DC_H_LOT, _DC_MAX_H = _build_dc_tables()
OFFSET_EF = _DC_MAX_H   # F/E pass starts after last C lot

# D double-row pairs (rows 20-21): nA/nB share same H as 'n', with suffix
_D_DR_PAIRS = frozenset([
    '376','377','378','379','380','381','382','383','384',  # row 20
    '367','368','369','370','371','372','373','374','375',  # row 21
])


# ── Sections F + E — table-driven from exact map data ─────────────
# Sweep order: F row r → E row r, for r = 1..12
# F: 18 lots per row, 11 rows, no H-lots, no double-rows
# E: variable lots per row, 12 rows, H-lots + double-row pairs in rows 9-10

_F_ROWS = {
    1:  ['18','17','16','15','14','13','12','11','10','9','8','7','6','5','4','3','2','1'],
    2:  ['36','35','34','33','32','31','30','29','28','27','26','25','24','23','22','21','20','19'],
    3:  ['54','53','52','51','50','49','48','47','46','45','44','43','42','41','40','39','38','37'],
    4:  ['72','71','70','69','68','67','66','65','64','63','62','61','60','59','58','57','56','55'],
    5:  ['90','89','88','87','86','85','84','83','82','81','80','79','78','77','76','75','74','73'],
    6:  ['108','107','106','105','104','103','102','101','100','99','98','97','96','95','94','93','92','91'],
    7:  ['126','125','124','123','122','121','120','119','118','117','116','115','114','113','112','111','110','109'],
    8:  ['144','143','142','141','140','139','138','137','136','135','134','133','132','131','130','129','128','127'],
    9:  ['162','161','160','159','158','157','156','155','154','153','152','151','150','149','148','147','146','145'],
    10: ['180','179','178','177','176','175','174','173','172','171','170','169','168','167','166','165','164','163'],
    11: ['198','197','196','195','194','193','192','191','190','189','188','187','186','185','184','183','182','181'],
}

_E_ROWS = {
    1:  ['19','18','17','16','15','14','13H','13','12','11','10','9H','9','8','7','6','5H','5','4','3','2','1'],
    2:  ['38','37','36','35','34','33','32H','32','31','30','29','28H','28','27','26','25','24H','24','23','22','21','20'],
    3:  ['57','56','55','54','53','52','51H','51','50','49','48','47H','47','46','45','44','43H','43','42','41','40','39'],
    4:  ['76','75','74','73','72','71','70H','70','69','68','67','66H','66','65','64','63','62H','62','61','60','59','58'],
    5:  ['95','94','93','92','91','90','89H','89','88','87','86','85H','85','84','83','82','81H','81','80','79','78','77'],
    6:  ['114','113','112','111','110','109','108H','108','107','106','105','104H','104','103','102','101','100H','100','99','98','97','96'],
    7:  ['133','132','131','130','129','128','127H','127','126','125','124','123H','123','122','121','120','119H','119','118','117','116','115'],
    8:  ['152','151','150','149','148','147','146H','146','145','144','143','142H','142','141','140','139','138H','138','137','136','135','134'],
    9:  ['169','168','167','166','165','164','163H','163','162','161','160','159H','159','158','157','156','155H','155','154','153','152dr'],
    # ↑ '152dr' = double-row pair for lot 152 (B152/A152 share this position's H)
    10: ['177','176','175','174','173','172','171H','171','170','169dr','199BH',
         '199','198','197','196','195','194','193','192','191','190'],
    # ↑ '169dr' = double-row pair for lot 169 (B169/A169 share this H)
    #   '199BH' = single H-lot
    #   '199'–'190' = 10 double-row pairs (A and B sub-lots share the position's H)
    11: ['183','182','181','180','179','178','177H','213','212','211','210','209H',
         '209','208','207','206','205','204','203','202','201','200'],
    12: ['189','188','187','186','185','184','183H','227','226','225','224','223H',
         '223','222','221','220','219','218','217','216','215','214'],
}

# E double-row pairs — 1 sweep position shared by both A and B sub-lots
_E_DR_PAIRS = frozenset([
    '152dr',                                                        # row 9  last pos
    '169dr',                                                        # row 10 pos 10
    '190','191','192','193','194','195','196','197','198','199',    # row 10 pos 12-21
])

# Map user-facing labels → internal base key in _E_DR_PAIRS
# '152A'/'152B' → '152dr',  '169A'/'169B' → '169dr',  '199A'/'199B' → '199', etc.
_E_DR_SUFFIX_MAP = {}
for _base in _E_DR_PAIRS:
    _display = _base.replace('dr', '')
    _E_DR_SUFFIX_MAP[_display + 'A'] = _base
    _E_DR_SUFFIX_MAP[_display + 'B'] = _base


def _build_ef_tables():
    F_LOT_H, E_LOT_H, EF_H_LOT = {}, {}, {}
    h = _DC_MAX_H
    for r in range(1, max(max(_F_ROWS), max(_E_ROWS)) + 1):
        for lot in _F_ROWS.get(r, []):
            h += 1
            if lot not in F_LOT_H:
                F_LOT_H[lot] = h
            EF_H_LOT[h] = ('F', lot)
        for lot in _E_ROWS.get(r, []):
            h += 1
            if lot not in E_LOT_H:
                E_LOT_H[lot] = h
            EF_H_LOT[h] = ('E', lot)
    return F_LOT_H, E_LOT_H, EF_H_LOT, h


_F_LOT_H, _E_LOT_H, _EF_H_LOT, _EF_MAX_H = _build_ef_tables()

# ══════════════════════════════════════════════════════════════════════
# H-NUMBERS SECTION 2
# Continues from _EF_MAX_H (H002331). Sweep order:
#   1. B margin lots (373–394 + sub-lots)     → section 'B'
#   2. D margin lots (542–563H)               → section 'D'
#   3. F margin lots (199–210)                → section 'F'
#   4. Alternating G/H rows (4 rows each)     → sections 'G' and 'H'
# ══════════════════════════════════════════════════════════════════════

_B_MARGIN_ROWS = {
    1: ['373'],    2: ['374'],    3: ['375'],    4: ['376'],    5: ['376H'],
    6: ['377'],    7: ['378'],    8: ['379'],    9: ['380'],    10: ['380H'],
    11: ['381'],   12: ['382'],   13: ['383'],   14: ['384'],
    15: ['384HA','384H'],
    16: ['385A','385'],
    17: ['386A','386'],
    18: ['387B','387A','387'],
    19: ['388B','388A','388'],
    20: ['388HB','388HA','388H'],
    21: ['389B','389A','389'],
    22: ['390C','390B','390A','390'],
    23: ['390H'],
    24: ['391'],   25: ['392'],   26: ['393'],   27: ['394'],
}

_D_MARGIN_ROWS = {
    1:['542'],  2:['543'],  3:['544'],  4:['545'],  5:['545H'],
    6:['546'],  7:['547'],  8:['548'],  9:['549'],  10:['549H'],
    11:['550'], 12:['551'], 13:['552'], 14:['553'], 15:['554'],
    16:['555'], 17:['556'], 18:['556H'],19:['557'], 20:['558'],
    21:['559'], 22:['559H'],23:['560'], 24:['560H'],25:['561'],
    26:['562'], 27:['562H'],28:['563'], 29:['563H'],
}

_F_MARGIN_ROWS = {r:[str(199+r-1)] for r in range(1,13)}  # 199-210

_G_ROWS = {
    1: ['58','19','19','18','17','16','15','14','13','12','11','10','9','8H','8','7','6','5','4','3','2','1'],
    2: ['59','38H','38','37','36','35','34','33','32','31','30','29','28','27H','27','26','25','24','23','22','21','20'],
    3: ['60','57H','57','56','55','54','53','52','51','50','49','48','47','46H','46','45','44','43','42','41','40','39'],
    4: ['61','62','63','64','65','66','67','68','69','70','71','72','73','74','75'],
}

# Section H (labeled "Section E" in the source map — confirmed by lot range 1-92)
_H_ROWS = {
    1: ['23','22','21','20','19','18','17','16','15','14','13','12','11','10','9','8','7','6','5','4','3','2','1'],
    2: ['46','45','44','43','42','41','40','39','38','37','36','35','34','33','32','31','30','29','28','27','26','25','24'],
    3: ['69','68','67','66','65','64','63','62','61','60','59','58','57','56','55','54','53','52','51','50','49','48','47'],
    4: ['92','91','90','89','88','87','86','85','84','83','82','81','80','79','78','77','76','75','74','73','72','71','70'],
}


def _build_s2_tables():
    """Build Section 2 H-number lookup tables, continuing from _EF_MAX_H."""
    B2, D2, F2, G, H2 = {}, {}, {}, {}, {}
    S2_H_LOT = {}
    h = _EF_MAX_H

    def _add(lot_h, lot, sec):
        nonlocal h
        h += 1
        if lot not in lot_h:
            lot_h[lot] = h
        S2_H_LOT[h] = (sec, lot)

    for r in sorted(_B_MARGIN_ROWS):
        for lot in _B_MARGIN_ROWS[r]:
            _add(B2, lot, 'B')

    for r in sorted(_D_MARGIN_ROWS):
        for lot in _D_MARGIN_ROWS[r]:
            _add(D2, lot, 'D')

    for r in sorted(_F_MARGIN_ROWS):
        for lot in _F_MARGIN_ROWS[r]:
            _add(F2, lot, 'F')

    for r in range(1, 5):
        for lot in _G_ROWS.get(r, []):
            _add(G, lot, 'G')
        for lot in _H_ROWS.get(r, []):
            _add(H2, lot, 'H')

    return B2, D2, F2, G, H2, S2_H_LOT, h


_B2_LOT_H, _D2_LOT_H, _F2_LOT_H, _G_LOT_H, _H_LOT_H, _S2_H_LOT, _S2_MAX_H = _build_s2_tables()

# ══════════════════════════════════════════════════════════════════════
# H-NUMBERS SECTION 3 — Section M
# Continues from _S2_MAX_H. Simple sequential sweep, no double-rows.
# ══════════════════════════════════════════════════════════════════════

_M_ROWS = {
    1:  ['11','12'],
    2:  ['14','15','16'],
    3:  ['18','19','20'],
    4:  ['23','24','25'],
    5:  ['28','29','30','31'],
    6:  ['34','35','36','37'],
    7:  ['40','41','42','43'],
    8:  ['46','47','48','49'],
    9:  ['52','53','54','55','61'],
    10: ['58','59','60','66','67'],
    11: ['64','65','71','72','73','74','75'],
    12: ['70','76','77','78','79','80','81'],
    13: ['82','83','84','85','86','87'],
    14: ['88','89','90','91','92','93'],
    15: ['94','95','96','97','98','99'],
    16: ['100','101','102','103','104','105'],
    17: ['106','107','108','109','110','111'],
    18: ['112','113','114','115','116','117'],
    19: ['118','119','120','121','122','123'],
    20: ['124','125','126','127','128','129'],
    21: ['130','131','132','133','134','135'],
    22: ['136','137','138','139','140','141'],
    23: ['142','143','144','145','146','147'],
    24: ['148','149','150','151','152','153'],
    25: ['154','155','156','157','158','159'],
    26: ['160','161','162','163','164'],
    27: ['165','166','167','168','169'],
    28: ['170','171','172','173','174'],
    29: ['175','176','177','178','179'],
    30: ['180','181','182','183','184'],
    31: ['185','186','187','188','189'],
    32: ['190','191','192','193','194'],
    33: ['195','196','197','198','199'],
    34: ['200','201','202','203','204'],
    35: ['205','206','207','208','209'],
    36: ['210','211','212','213','214'],
    37: ['215','216','217','218','219'],
    38: ['220','221','222','223','224'],
    39: ['225','226','227','228','229'],
    40: ['230','231','232','233','234'],
    41: ['235','236','237','238','239'],
    42: ['240','241','242','243','244'],
    43: ['245','246','247','248'],
    44: ['249','250','251','252'],
    45: ['253','254','255','256'],
    46: ['257','258','259','260'],
    47: ['261','262','263'],
    48: ['264','265','266'],
    49: ['267','268','269'],
    50: ['270','271'],
    51: ['272','273'],
    52: ['274','275'],
    53: ['276','277'],
    54: ['278','279'],
}


def _build_m_tables():
    M_LOT_H, M_H_LOT = {}, {}
    h = _S2_MAX_H
    for r in sorted(_M_ROWS):
        for lot in _M_ROWS[r]:
            h += 1
            if lot not in M_LOT_H:
                M_LOT_H[lot] = h
            M_H_LOT[h] = ('M', lot)
    return M_LOT_H, M_H_LOT, h


_M_LOT_H, _M_H_LOT, _S3_MAX_H = _build_m_tables()

# ══════════════════════════════════════════════════════════════════════
# H-NUMBERS SECTION 4  —  K  J  I  L
# Continues from _S3_MAX_H (H002835). Sequential, no double-rows.
# Sweep order: all of K → all of J → all of I → all of L
# ══════════════════════════════════════════════════════════════════════

_K_ROWS = {
    1:  ['1','2','3'],
    2:  ['6','7','8','9'],
    3:  ['13','14','15','16'],
    4:  ['22'],
    5:  ['5'],
    6:  ['11','12'],
    7:  ['18','19'],
    8:  ['25','26'],
    9:  ['31','32'],
    10: ['36','37','38'],
    11: ['42','43','44','45'],
    12: ['50','51','52'],
    13: ['57','58','59'],
    14: ['64','65','66'],
    15: ['72','73'],
    16: ['79','80'],
    17: ['86','87'],
    18: ['93','94'],
    19: ['101','102'],
    20: ['109','110'],
    21: ['117','118'],
    22: ['125','126'],
    23: ['133','134'],
    24: ['141','142'],
    25: ['149','150'],
    26: ['158','159'],
    27: ['167','168'],
    28: ['176','177'],
    29: ['185','186'],
    30: ['195','196'],
    31: ['205','206'],
    32: ['215','216'],
    33: ['225','226'],
    34: ['235','236'],
    35: ['246','247'],
    36: ['256','257','258','259'],
    37: ['268','269','270','271'],
    38: ['280','281','282','283'],
    39: ['293','294','295','296'],
    40: ['306','307','308','309'],
    41: ['319','320','321','322'],
    42: ['332','333','334','335'],
    43: ['345','346','347','348'],
    44: ['358','359','360','361'],
}

_J_ROWS = {
    1:  ['1','2','3','4','5'],
    2:  ['6','7','8','9','10','11','12'],
    3:  ['13','14','15','16','17','18','19'],
    4:  ['20','21','22','23','24','25','26'],
    5:  ['27','28','29','30','31','32','33'],
    6:  ['34','35','36','37','38','39','40'],
    7:  ['41','42','43','44','45','46','47'],
    8:  ['48','49','50','51','52','53'],
    9:  ['54','55','56','57','58','59'],
    10: ['60','61','62','63','64','65'],
    11: ['66','67','68','69','70','71'],
    12: ['72','73','74','75','76','77'],
    13: ['78','79','80','81','82'],
    14: ['83','84','85','86','87'],
    15: ['88','89','90','91','92'],
    16: ['93','94','95','96','97'],
    17: ['98','99','100','101'],
    18: ['102','103','104','105'],
    19: ['106','107','108','109'],
    20: ['110','111','112','113'],
    21: ['114','115','116'],
    22: ['117','118','119'],
    23: ['120','121','122'],
    24: ['123','124','125'],
    25: ['126','127'],
    26: ['128','129'],
    27: ['130','131'],
    28: ['132'],
}

_I_ROWS = {r: [str(r*2-1), str(r*2)] for r in range(1, 33)}

_L_ROWS = {
    1: ['69','70','71','72','73'],
    2: ['74','75','76','77','78','79'],
    3: ['80','81','82','83','84','85'],
    4: ['86','87','88','89','90','91','92'],
    5: ['93','94','95','96','97','98'],
    6: ['99','100','101','102','103'],
    7: ['104','105','106','107'],
}


def _build_s4_tables():
    K, J, I, L = {}, {}, {}, {}
    S4_H_LOT = {}
    h = _S3_MAX_H

    def _add(lot_h, lot, sec):
        nonlocal h
        h += 1
        if lot not in lot_h:
            lot_h[lot] = h
        S4_H_LOT[h] = (sec, lot)

    for r in sorted(_K_ROWS):
        for lot in _K_ROWS[r]: _add(K, lot, 'K')
    for r in sorted(_J_ROWS):
        for lot in _J_ROWS[r]: _add(J, lot, 'J')
    for r in sorted(_I_ROWS):
        for lot in _I_ROWS[r]: _add(I, lot, 'I')
    for r in sorted(_L_ROWS):
        for lot in _L_ROWS[r]: _add(L, lot, 'L')

    return K, J, I, L, S4_H_LOT, h


_K_LOT_H, _J_LOT_H, _I_LOT_H, _L_LOT_H, _S4_H_LOT, _S4_MAX_H = _build_s4_tables()




B_DECODER = build_B_decoder()
A_DECODER = build_A_decoder()

# No H-lots, no double rows.
# c=1 (rightmost): lot 18r   e.g. r=1→18, r=2→36, …, r=11→198
# c=k (k=2..18):   lot (r-1)*18 + (19-k)
# Sweep: F is FIRST in each EF level (c=1..18), then E follows.
def build_F_decoder():
    d = {}
    for r in range(1, 12):          # rows 1..11 only
        for c in range(1, N_F + 1):
            lot = (r - 1) * 18 + (19 - c)
            d[str(lot)] = (c, r)
    return d


# ── Section E  (22 cols × 12 rows, row-increment 19) ─────────────
# Mirrors Section A exactly in column/row structure.
# Row 12 of E extends past F's 11 rows (F has no lots at r=12).
# Double-row lots (190A/B … 199A/B) share base H + A/B suffix.
def build_E_decoder():
    d = {}
    for r in range(1, ROWS_EF + 1):    # rows 1..12
        b = 19 * (r - 1)
        d[str(19+b)] = (1,  r)
        d[str(18+b)] = (2,  r)
        d[str(17+b)] = (3,  r)
        d[str(16+b)] = (4,  r)
        d[str(15+b)] = (5,  r)
        d[str(14+b)] = (6,  r)
        d[f"{13+b}H"]= (7,  r)   # H-lot
        d[str(13+b)] = (8,  r)
        d[str(12+b)] = (9,  r)
        d[str(11+b)] = (10, r)
        d[str(10+b)] = (11, r)
        d[str(9+b)]  = (12, r)
        d[str(8+b)]  = (13, r)
        d[str(7+b)]  = (14, r)
        d[str(6+b)]  = (15, r)
        d[f"{5+b}H"] = (16, r)   # H-lot
        d[str(5+b)]  = (17, r)
        d[str(4+b)]  = (18, r)
        d[str(3+b)]  = (19, r)
        d[str(2+b)]  = (20, r)
        d[f"{1+b}H"] = (21, r)   # H-lot
        d[str(1+b)]  = (22, r)
    return d



F_DECODER = build_F_decoder()
E_DECODER = build_E_decoder()
_DECODERS = {'A':A_DECODER,'B':B_DECODER,'E':E_DECODER,'F':F_DECODER}


# ── Hash functions ────────────────────────────────────────────
# ── Double-row lots in Section D ─────────────────────────────────────
# Lots that exist in TWO physical rows at the same sweep column.
# They share the base H number but get an A or B suffix appended.
# Format: label → (c, r, suffix)
# c and r are the sweep column/row for that position in D's strip.
# Zone 1 (near sweep level of 355H): lots 376–384 A/B
# Zone 2 (near sweep level of 366H): to be confirmed
#
# NOTE: c values here are the actual D sweep column positions for these
# strip lots. They will be refined when D's full strip is catalogued.
# For now they are assigned based on their offset from the 355H anchor.
# 355H is D's strip — at whatever (c, r) it occupies in the D decoder,
# the lots to its left (going west = higher c) are at c+1, c+2 etc.
# Zone 1 double-row lots occupy c positions AFTER 355H in the strip.
# We assign them relative to D's main grid rows for now.

# Each entry: lot_label → (c, r, 'A' or 'B')
# c and r match the single base lot they share H_lot with.



def h_lot(section, lot_label):
    """
    Return (h_number, 'H000837') for a section + lot label.

    Section D and C are table-driven from the exact map sweep order.
    Section E double-row lots return H{n}A or H{n}B suffix.
    All other sections use formula-based decoding.
    """
    sec = section.upper().strip()
    lot = str(lot_label).strip()

    # ── Pass 2: D and C (table-driven, Section 1 + Section 2) ──────
    if sec == 'D':
        # Double-row pair: '384A'/'376B' → same H as base lot, + suffix
        if len(lot) > 1 and lot[-1] in ('A','B') and lot[:-1] in _D_DR_PAIRS:
            base, suffix = lot[:-1], lot[-1]
            h = _D_LOT_H.get(base)
            if h is None:
                return None, f"Base lot '{base}' not found in Section D."
            return h, f"H{h:06d}{suffix}"
        # Section 1 main table first, then Section 2 margin table
        h = _D_LOT_H.get(lot) or _D2_LOT_H.get(lot)
        if h is None:
            return None, f"Lot '{lot}' not found in Section D."
        return h, f"H{h:06d}"

    if sec == 'C':
        h = _C_LOT_H.get(lot)
        if h is None:
            return None, f"Lot '{lot}' not found in Section C."
        return h, f"H{h:06d}"

    # ── Section 4: K  J  I  L ───────────────────────────────────────────
    _S4_MAP = {'K':_K_LOT_H,'J':_J_LOT_H,'I':_I_LOT_H,'L':_L_LOT_H}
    if sec in _S4_MAP:
        h = _S4_MAP[sec].get(lot)
        if h is None:
            return None, f"Lot '{lot}' not found in Section {sec}."
        return h, f"H{h:06d}"

    # ── Section 3: M ──────────────────────────────────────────────────
    if sec == 'M':
        h = _M_LOT_H.get(lot)
        if h is None:
            return None, f"Lot '{lot}' not found in Section M."
        return h, f"H{h:06d}"

    # ── Section 2: B margins + G/H ──────────────────────────────────
    # B margin lots (373-394) and G/H sections are checked here.
    # D margin lots are handled in the D block below.
    # F margin lots are handled in the F block below.
    if sec == 'B':
        # Check Section 2 margin lots first (373-394 etc.)
        h2 = _B2_LOT_H.get(lot)
        if h2 is not None:
            return h2, f"H{h2:06d}"
        # Fall through to formula-based Section 1 B lookup below
    elif sec in ('G', 'H'):
        _gh = _G_LOT_H if sec == 'G' else _H_LOT_H
        h = _gh.get(lot)
        if h is not None:
            return h, f"H{h:06d}"
        return None, f"Lot '{lot}' not found in Section {sec}."

    # ── Pass 3: F (table-driven, Section 1 + Section 2 margins) ──
    if sec == 'F':
        # Check Section 2 margins (199-210) first, then Section 1 table
        h = _F2_LOT_H.get(lot) or _F_LOT_H.get(lot)
        if h is None:
            return None, f"Lot '{lot}' not found in Section F."
        return h, f"H{h:06d}"

    # ── Pass 3: E (table-driven, A/B suffix for double-row pairs) ──
    if sec == 'E':
        if lot in _E_DR_SUFFIX_MAP:
            base = _E_DR_SUFFIX_MAP[lot]; suffix = lot[-1]
            h = _E_LOT_H.get(base)
            if h is None:
                return None, f"Double-row base '{base}' not found in Section E."
            return h, f"H{h:06d}{suffix}"
        h = _E_LOT_H.get(lot)
        if h is None:
            return None, f"Lot '{lot}' not found in Section E."
        return h, f"H{h:06d}"

    # ── Pass 1: B, A (formula-based) ────────────────────────────
    dec = _DECODERS.get(sec)
    if dec is None:
        return None, f"Unknown section '{section}'. Use A, B, C, D, E, or F."
    if lot not in dec:
        return None, f"Lot '{lot}' not found in Section {sec}."
    c, r = dec[lot]
    if sec == 'B':   h = SWEEP*(r-1) + c
    elif sec == 'A': h = SWEEP*(r-1) + N_B + c
    else: return None, f"Section '{sec}' has no formula."
    return h, f"H{h:06d}"



def h_grave(section, lot_label, grave_number):
    """
    Return grave H number. For double-row lots, the suffix sits BETWEEN
    the lot number and the grave digit.
    e.g. h_grave('D', '376H', 3) → (1634, 'H001634A3')
         h_grave('D', '376B', 3) → (1634, 'H001634B3')
         h_grave('B', '20H',  1) → (1,    'H0000011')
    """
    h, hfmt = h_lot(section, lot_label)
    if h is None: return None, hfmt
    g = int(grave_number)
    if not (1 <= g <= 9): return None, f"Grave {g} out of range."
    # Detect A/B suffix from lot H string (e.g. 'H001634A')
    suffix = ''
    if hfmt and hfmt[0] == 'H' and hfmt[-1] in ('A', 'B'):
        suffix = hfmt[-1]
    hg = h * 10 + g
    if suffix:
        # Format: H{lot_base:06d}{suffix}{grave}  e.g. H001634A3
        return hg, f"H{h:06d}{suffix}{g}"
    return hg, f"H{hg:07d}"


def decode_h(h_number):
    """Reverse lookup: H number → {section, lot_label, h_number, h_formatted}"""
    n = int(h_number)
    max_h = _S4_MAX_H
    if n < 1 or n > max_h:
        return None

    if n <= OFFSET:                          # Pass 1 — B / A
        level = (n-1)//SWEEP; pos=(n-1)%SWEEP+1; r=level+1
        if pos<=N_B: c,sec,dec=pos,'B',B_DECODER
        else: c,sec,dec=pos-N_B,'A',A_DECODER
        tgt=(c,r)
        lot=next((k for k,v in dec.items() if v==tgt),None)
        return {"section":sec,"lot_label":lot,"c":c,"r":r,
                "h_number":n,"h_formatted":f"H{n:06d}"}

    elif n <= _DC_MAX_H:                     # Pass 2 — D / C (table-driven)
        entry=_DC_H_LOT.get(n)
        if entry is None: return None
        sec,lot=entry
        return {"section":sec,"lot_label":lot,
                "h_number":n,"h_formatted":f"H{n:06d}"}

    elif n > _S3_MAX_H and n <= _S4_MAX_H:  # Section 4 — K J I L
        entry = _S4_H_LOT.get(n)
        if entry is None: return None
        sec2, lot2 = entry
        return {'section':sec2,'lot_label':lot2,'h_number':n,'h_formatted':f'H{n:06d}'}

    elif n > _S2_MAX_H and n <= _S3_MAX_H:  # Section 3 — M
        entry = _M_H_LOT.get(n)
        if entry is None: return None
        sec2, lot2 = entry
        return {'section':sec2,'lot_label':lot2,'h_number':n,'h_formatted':f'H{n:06d}'}

    elif n > _EF_MAX_H and n <= _S2_MAX_H:  # Section 2 — margins + G/H
        entry = _S2_H_LOT.get(n)
        if entry is None: return None
        sec2, lot2 = entry
        return {'section':sec2,'lot_label':lot2,'h_number':n,'h_formatted':f'H{n:06d}'}

    else:                                    # Pass 3 — F / E (table-driven)
        entry = _EF_H_LOT.get(n)
        if entry is None: return None
        sec2, lot2 = entry
        return {'section':sec2,'lot_label':lot2,'h_number':n,'h_formatted':f'H{n:06d}'}


# ── Export ────────────────────────────────────────────────────
def full_table(section):
    """Return list of dicts (sorted by H number) for a section — all sub-sections combined."""
    sec = section.upper()
    rows = []

    def _add_rows(lot_h_dict):
        for lot_label, h in lot_h_dict.items():
            hfmt = f"H{h:06d}"
            row = {"section": sec, "lot_label": lot_label,
                   "h_lot_number": h, "h_lot": hfmt}
            for g in range(1, 7):
                hg, hgfmt = h_grave(sec, lot_label, g)
                row[f"h_grave_{g}"] = hgfmt if hg else "—"
            rows.append(row)

    if sec == 'D':
        _add_rows({**_D_LOT_H, **_D2_LOT_H})
    elif sec == 'C':
        _add_rows(_C_LOT_H)
    elif sec == 'F':
        _add_rows({**_F_LOT_H, **_F2_LOT_H})
    elif sec == 'E':
        _add_rows(_E_LOT_H)
    elif sec == 'G':
        _add_rows(_G_LOT_H)
    elif sec == 'H':
        _add_rows(_H_LOT_H)
    elif sec == 'M':
        _add_rows(_M_LOT_H)
    elif sec == 'K':
        _add_rows(_K_LOT_H)
    elif sec == 'J':
        _add_rows(_J_LOT_H)
    elif sec == 'I':
        _add_rows(_I_LOT_H)
    elif sec == 'L':
        _add_rows(_L_LOT_H)
    elif sec == 'B':
        # Section 1: formula-based; Section 2: margin table
        dec = _DECODERS.get('B')
        if dec:
            for lot_label, (c, r) in dec.items():
                if r == 0: continue
                h, hfmt = h_lot('B', lot_label)
                if h is None: continue
                row = {"section": "B", "lot_label": lot_label, "col_c": c, "row_r": r,
                       "h_lot_number": h, "h_lot": hfmt}
                for g in range(1, 7):
                    hg, hgfmt = h_grave('B', lot_label, g)
                    row[f"h_grave_{g}"] = hgfmt if hg else "—"
                rows.append(row)
        _add_rows(_B2_LOT_H)
    elif sec == 'A':
        dec = _DECODERS.get('A')
        if dec:
            for lot_label, (c, r) in dec.items():
                if r == 0: continue
                h, hfmt = h_lot('A', lot_label)
                if h is None: continue
                row = {"section": "A", "lot_label": lot_label, "col_c": c, "row_r": r,
                       "h_lot_number": h, "h_lot": hfmt}
                for g in range(1, 7):
                    hg, hgfmt = h_grave('A', lot_label, g)
                    row[f"h_grave_{g}"] = hgfmt if hg else "—"
                rows.append(row)

    rows.sort(key=lambda x: (x["h_lot_number"], x.get("lot_label", "")))
    return rows


def export_csv(section, filepath):
    rows = full_table(section)
    if not rows: return 0
    with open(filepath,"w",newline="",encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    return len(rows)


def export_all_csv(out_dir="."):
    os.makedirs(out_dir, exist_ok=True)
    for sec in ("B","A","D","C","F","E","G","H","M","K","J","I","L"):
        path = os.path.join(out_dir,f"cedar_grove_section_{sec}_h_table.csv")
        n = export_csv(sec, path)
        print(f"  Section {sec}: {n:4d} lots  →  {path}")



# ── Self-test & accuracy report ───────────────────────────────────────────
def self_test():
    W = 76

    def box_top():    print(f"  ╔{'═'*(W-4)}╗")
    def box_mid():    print(f"  ╠{'═'*(W-4)}╣")
    def box_bot():    print(f"  ╚{'═'*(W-4)}╝")
    def box_row(txt): inner=W-6; print(f"  ║ {txt:<{inner}} ║")
    def rule(label=""):
        if label:
            dash = W-len(label)-8
            print(f"  ┌── {label} {'─'*dash}┐")
        else:
            print(f"  {'─'*(W-4)}")
    def close(): print(f"  └{'─'*(W-4)}┘")

    # ─── Header ──────────────────────────────────────────────────────────
    print()
    box_top()
    box_row("CEDAR GROVE CEMETERY  ·  H-Number Decoder")
    box_row("University of Notre Dame  ·  Notre Dame, Indiana")
    box_mid()
    box_row(f"Sections:  A  B  C  D  E  F         Passes: 3")
    box_row(f"H range:   H000001 – H{_EF_MAX_H:06d}          "
            f"Double-row support: D, E")
    box_bot()
    print()

    # ─── System constants ─────────────────────────────────────────────────
    rule("SYSTEM CONSTANTS")
    fmt = "  │  {:<14}  SWEEP={:>3}  ROWS={:>2}  OFFSET={:>6}  {:}"
    print(fmt.format("Pass 1  B + A", SWEEP,    ROWS,    0,          f"H000001 – H{OFFSET:06d}"))
    print(fmt.format("Pass 2  D + C", "var",     "var",   OFFSET,     f"H{OFFSET+1:06d} – H{_DC_MAX_H:06d}"))
    print(fmt.format("Pass 3  F + E", "var",    "var",   OFFSET_EF, f"H{OFFSET_EF+1:06d} – H{_EF_MAX_H:06d}"))
    close()
    print()

    # ─── Section inventory ────────────────────────────────────────────────
    rule("SECTION INVENTORY")
    print(f"  │  {'Sec':<5} {'Pass':<8} {'Cols':>5} {'Rows':>5} "
          f"{'Inc':>5} {'Lots':>6} {'H-lots':>7} {'Double rows':>13}")
    print(f"  │  {'─'*5} {'─'*8} {'─'*5} {'─'*5} {'─'*5} {'─'*6} {'─'*7} {'─'*13}")
    # Note: only D and E have double-row lots
    # Section inventory — D and C are table-driven (variable rows/cols)
    d_lots = len(_D_LOT_H); c_lots = len(_C_LOT_H)
    d_hlots = sum(1 for k in _D_LOT_H if k.endswith('H'))
    c_hlots = sum(1 for k in _C_LOT_H if k.endswith('H'))
    d_doubles = len(_D_DR_PAIRS)  # 18 confirmed pairs in D rows 20-21

    section_meta = [
        ('B','1 · B+A', N_B, ROWS, 20, B_DECODER),
        ('A','1 · B+A', N_A, ROWS, 19, A_DECODER),
    ]
    f_lots = len(_F_LOT_H); e_lots = len(_E_LOT_H)
    e_hlots = sum(1 for k in _E_LOT_H if k.endswith('H'))
    for sec, pair, cols, rows, inc, dec in section_meta:
        n    = sum(1 for v in dec.values() if v[1] > 0)
        hlot = sum(1 for k, v in dec.items() if k.endswith('H') and v[1] > 0)
        print(f"  │  {sec:<5} {pair:<8} {cols:>5} {rows:>5} {inc:>5} {n:>6} {hlot:>7} {'—':>13}")
    print(f"  │  {'D':<5} {'2 · D+C':<8} {'var':>5} {'23':>5} {'var':>5} {d_lots:>6} {d_hlots:>7} {f'{d_doubles} pairs':>13}")
    print(f"  │  {'C':<5} {'2 · D+C':<8} {'var':>5} {'24':>5} {'var':>5} {c_lots:>6} {c_hlots:>7} {'—':>13}")
    print(f"  │  {'F':<5} {'3 · F+E':<8} {'18':>5} {'11':>5} {'18':>5} {f_lots:>6} {'0':>7} {'—':>13}")
    print(f"  │  {'E':<5} {'3 · F+E':<8} {'22':>5} {'12':>5} {'19':>5} {e_lots:>6} {e_hlots:>7} {f'{len(_E_DR_PAIRS)} pairs':>13}")
    total_lots = sum(sum(1 for v in dec.values() if v[1]>0) for _,_,_,_,_,dec in section_meta) + d_lots + c_lots + f_lots + e_lots
    print(f"  │")
    print(f"  │  Total lots catalogued: {total_lots:,}")
    close()
    print()

    # ─── Test runner ──────────────────────────────────────────────────────
    grand_pass = grand_total = 0

    def run_block(title, rows, fn):
        nonlocal grand_pass, grand_total
        rule(title)
        block_pass = 0
        for row in rows:
            ok, line = fn(row)
            mark = "✓" if ok else "✗"
            print(f"  │  {mark}  {line}")
            if ok: block_pass += 1
        grand_pass  += block_pass
        grand_total += len(rows)
        pct = block_pass/len(rows)*100 if rows else 0
        bar = "█"*round(28*block_pass/len(rows)) + "░"*(28-round(28*block_pass/len(rows))) if rows else ""
        print(f"  └─  [{bar}]  {block_pass}/{len(rows)}  ({pct:.0f}%)")
        print()

    # ── 1. Lot lookups ────────────────────────────────────────────────────
    lot_tests = [
        # Pass 1: B + A
        ("B","20H",  1,    "H000001",  "B row 1 first lot"),
        ("A","1",    44,   "H000044",  "A row 1 last lot"),
        # Pass 2: D + C
        ("D","1U",   837,  "H000837",  "D row 1 first lot"),
        ("D","384A", 1690, "H001690A", "D double-row A"),
        ("C","417",  1871, "H001871",  "C row 24 last lot"),
        # Pass 3: F + E
        ("F","18",   1872, "H001872",  "F row 1 first lot"),
        ("E","19",   1890, "H001890",  "E row 1 first lot"),
        ("E","199A", 2260, "H002260A", "E double-row A"),
        # Section 2
        ("B","373",  2332, "H002332",  "B margin first lot"),
        ("B","390C", 2364, "H002364",  "B margin sub-lot"),
        ("D","542",  2373, "H002373",  "D margin first lot"),
        ("D","563H", 2401, "H002401",  "D margin last lot"),
        ("F","199",  2402, "H002402",  "F margin first lot"),
        ("G","58",   2414, "H002414",  "G row 1 first lot"),
        ("H","23",   2436, "H002436",  "H row 1 first lot"),
        ("G","75",   2563, "H002563",  "G last lot"),
        ("H","70",   2586, "H002586",  "H last lot — end of Section 2"),
        # Section 3: M
        ("M","11",   2587, "H002587",  "M row 1 first lot — start of Section 3"),
        ("M","12",   2588, "H002588",  "M row 1 last lot"),
        ("M","61",   2618, "H002618",  "M row 9 last lot (jumps from 55)"),
        ("M","70",   2631, "H002631",  "M row 12 first lot"),
        ("M","279",  2835, "H002835",  "M row 54 last lot — end of system"),
    ]
    def lot_fn(row):
        sec,lot,exp_h,exp_fmt,desc = row
        h,hfmt = h_lot(sec,lot)
        ok = (h==exp_h and hfmt==exp_fmt)
        return ok, f"h_lot('{sec}', {lot:>5})  →  {str(hfmt):14s}  {desc}"
    run_block("LOT LOOKUP — forward encoding", lot_tests, lot_fn)

    # ── 2. Reverse lookups ────────────────────────────────────────────────
    rev_tests = [
        (1,    "B", "20H", "B/A pass first lot"),
        (44,   "A", "1",   "B/A pass last lot"),
        (837,  "D", "1U",  "D/C pass first lot"),
        (1871, "C", "417", "D/C pass last lot"),
        (1872, "F", "18",  "F/E pass first lot"),
        (1911, "E", "1",   "F/E pass — E row 1 last lot"),
    ]
    def rev_fn(row):
        h_in,exp_sec,exp_lot,desc = row
        res = decode_h(h_in)
        ok  = bool(res and res['section']==exp_sec and res['lot_label']==exp_lot)
        found = f"Sec {res['section']}  Lot {res['lot_label']:<6}" if res else "NOT FOUND"
        return ok, f"decode_h({h_in:6d})  →  {found:<24}  [{desc}]"
    run_block("REVERSE LOOKUP — H number → section + lot", rev_tests, rev_fn)

    # ── 3. Double-row D ───────────────────────────────────────────────────
    dr_d = [
        ("D","384",  1690, "H001690",  "D row 20 — base lot"),
        ("D","384A", 1690, "H001690A", "D row 20 — 384A = same H + A suffix"),
        ("D","384B", 1690, "H001690B", "D row 20 — 384B = same H + B suffix"),
        ("D","376",  1698, "H001698",  "D row 20 — base lot 376"),
        ("D","376A", 1698, "H001698A", "D row 20 — 376A"),
        ("D","376B", 1698, "H001698B", "D row 20 — 376B"),
        ("D","367",  1741, "H001741",  "D row 21 zone 2 — base lot"),
        ("D","367A", 1741, "H001741A", "D row 21 zone 2 — 367A"),
        ("D","367B", 1741, "H001741B", "D row 21 zone 2 — 367B"),
    ]
    def dr_fn(row):
        sec,lot,exp_h,exp_fmt,desc = row
        h,hfmt = h_lot(sec,lot)
        ok = (h==exp_h and hfmt==exp_fmt)
        mark = "" if ok else f"  exp {exp_fmt}"
        return ok, f"h_lot('{sec}', {lot:>5})  →  {str(hfmt):14s}  {desc}{mark}"
    run_block("DOUBLE-ROW  Section D — shared H + A/B suffix (rows 20-21)", dr_d, dr_fn)

    # ── 4. Double-row E ───────────────────────────────────────────────────
    dr_e = [
        ("E","199A", 2260, "H002260A", "E·199 A-row c=12 r=11"),
        ("E","199B", 2260, "H002260B", "E·199 B-row (same base H)"),
        ("E","190A", 2269, "H002269A", "E·190 A-row c=1  r=10"),
        ("E","190B", 2269, "H002269B", "E·190 B-row (same base H)"),
    ]
    run_block("DOUBLE-ROW  Section E — shared H + suffix", dr_e, dr_fn)

    # ── 5. Grave H-numbers ────────────────────────────────────────────────
    grave_tests = [
        ("B","20H", 1, "H0000011",  "Regular    H000001 × 10 + 1"),
        ("B","20H", 2, "H0000012",  "Regular    H000001 × 10 + 2"),
        ("F","18",  1, "H0018721",  "Section F  H001872 × 10 + 1"),
        ("D","376A",3, "H001698A3", "D double-row 376A grave 3"),
        ("D","376B",3, "H001698B3", "D double-row 376B grave 3"),
        ("E","199A",2, "H002260A2", "E double-row 199A grave 2"),
    ]
    def gv_fn(row):
        sec,lot,g,exp,desc = row
        h,hfmt = h_grave(sec,lot,g)
        ok = (hfmt==exp)
        return ok, f"h_grave('{sec}', {lot}, {g})  →  {str(hfmt):16s}  {desc}"
    run_block("GRAVE H-NUMBERS — H_lot × 10 + grave_number", grave_tests, gv_fn)

    # ─── Final accuracy panel ─────────────────────────────────────────────
    pct      = grand_pass / grand_total * 100 if grand_total else 0
    bar_len  = 40
    filled   = round(bar_len * grand_pass / grand_total) if grand_total else 0
    bar      = "█"*filled + "░"*(bar_len-filled)
    status   = "ALL TESTS PASSED  ✓" if grand_pass==grand_total else f"{grand_total-grand_pass} FAILURE(S)  ✗"

    print()
    box_top()
    box_row("ACCURACY REPORT")
    box_mid()
    box_row(f"Tests run      :  {grand_total}")
    box_row(f"Tests passed   :  {grand_pass}")
    box_row(f"Tests failed   :  {grand_total - grand_pass}")
    box_row(f"Accuracy       :  {pct:.2f}%")
    box_row(f"[{bar}]  {grand_pass}/{grand_total}")
    box_mid()
    box_row(f"STATUS  :  {status}")
    box_bot()
    print()



# ── Display helpers ───────────────────────────────────────────────────────
import time as _time

def _print_slow(lines, delay=0.03):
    """Print lines one by one with a small delay for animation effect."""
    import sys
    for line in lines:
        print(line)
        sys.stdout.flush()
        _time.sleep(delay)

def _box(rows, width=54):
    """Render a clean box around rows of (label, value) or plain strings."""
    top = f"  ┌{'─'*width}┐"
    bot = f"  └{'─'*width}┘"
    out = [top]
    for row in rows:
        if row is None:
            out.append(f"  ├{'─'*width}┤")
        elif isinstance(row, str):
            out.append(f"  │  {row:<{width-4}}│")
        else:
            label, val = row
            lw = 18
            vw = width - lw - 4
            out.append(f"  │  {label:<{lw}}│  {str(val):<{vw}}│")
    out.append(bot)
    return out

def _show(section, lot_label, grave=None):
    sec = section.upper().strip()
    lot = str(lot_label).strip()
    h, hfmt = h_lot(sec, lot)
    if h is None:
        print(f"\n  ✗  {hfmt}\n")
        return

    # Work out section pass / H-number section label
    if h <= _EF_MAX_H:
        pass_map = {'B':'Pass 1','A':'Pass 1','D':'Pass 2',
                    'C':'Pass 2','E':'Pass 3','F':'Pass 3'}
        sec_label = f"Section 1 · The Grid  ·  {pass_map.get(sec,'Pass ?')}"
    elif h <= _S2_MAX_H:
        sec_label = "Section 2 · The Margins"
    elif h <= _S3_MAX_H:
        sec_label = "Section 3 · Section M"
    elif h <= _S4_MAX_H:
        sec_label = f"Section 4 · {sec}"
    else:
        sec_label = "Section 4"

    # Detect double-row suffix
    sfx = hfmt[-1] if hfmt and hfmt[-1] in ('A','B') else None
    dr_str = ('A-row (inner)' if sfx == 'A' else 'B-row (outer)') if sfx else None

    W  = 52          # box inner width
    DW = W - 2       # data column: label + value

    def row(label, value):
        return f"  │  {label:<18}{str(value):<{W-20}}│"

    def div():
        return f"  ├{'─'*W}┤"

    lines = []
    lines.append(f"  ┌{'─'*W}┐")
    lines.append(f"  │  {'Section ' + sec + '  ·  Lot ' + lot:<{W-2}}│")
    lines.append(f"  │  {sec_label:<{W-2}}│")
    lines.append(div())
    lines.append(row("H Lot Number", hfmt))
    if dr_str:
        lines.append(row("Double-row", dr_str))
    if grave is not None:
        hg, hgfmt = h_grave(sec, lot, int(grave))
        lines.append(div())
        lines.append(row("Grave",        grave))
        lines.append(row("H Grave",      hgfmt if hgfmt else "—"))
        lines.append(row("Formula",      f"H{h:06d} × 10 + {grave}"))
    lines.append(f"  └{'─'*W}┘")

    print()
    print("\n".join(lines))
    print()


# ── Interactive CLI ───────────────────────────────────────────────────────
HELP_TEXT = """
  ╔══════════════════════════════════════════════════════════════════╗
  ║  CEDAR GROVE CEMETERY — H-Number Decoder                        ║
  ║  University of Notre Dame  ·  Notre Dame, Indiana               ║
  ╚══════════════════════════════════════════════════════════════════╝

  COMMANDS
  ─────────────────────────────────────────────────────────────────

  lookup <section> <lot> [grave]
      Compute the H number for a lot, optionally for a specific grave.
      Supports double-row suffix lots (A/B).
      Examples:
        lookup B 20H          →  H000001
        lookup D 384A         →  H001647A
        lookup D 376H 3       →  H001634A3
        lookup E 199B 2       →  H002102B2
        lookup F 18           →  H001673
        lookup C 417          →  H001672

  reverse <H-number>
      Find which section and lot corresponds to an H number.
      Accepts H000001, 000001, or just 1.
      Examples:
        reverse 1             →  Section B  Lot 20H
        reverse H000837       →  Section D  Lot 1U
        reverse 1672          →  Section C  Lot 417

  test [section]
      Run the full accuracy test suite.
      Optionally test a single section only.
      Examples:
        test                  →  full 31-test suite
        test B                →  Section B anchor tests only
        test E                →  Section E + double-row tests
        test D                →  Section D + double-row tests

  table <section>
      Print all mapped lots for a section, sorted by H number.
      Sections: A  B  C  D  E  F
      Examples:
        table B               →  all B lots
        table E               →  all E lots incl. double-rows

  export [directory]
      Save all 6 section tables to CSV files.
      Default directory: current folder.
      Examples:
        export                →  saves to ./
        export ~/Downloads    →  saves to ~/Downloads/

  info
      Show system constants, pass ranges and coverage summary.

  help
      Show this command reference.

  quit  (or  exit  or  q)
      Exit the decoder.

  ─────────────────────────────────────────────────────────────────
  SECTIONS & PASSES
    Pass 1  B + A   H000001 – H000836   SWEEP=44  ROWS=19
    Pass 2  D + C   H000837 – H001672   SWEEP=44  ROWS=19
    Pass 3  F + E   H001673 – H002152   SWEEP=40  ROWS=12
  ─────────────────────────────────────────────────────────────────
"""

def _do_info():
    lines = [
        "",
        "  ┌── SYSTEM CONSTANTS ─────────────────────────────────────────┐",
        f"  │  Pass 1  B + A   SWEEP={SWEEP:<3} ROWS={ROWS:<3} "
        f"OFFSET={0:<7} H000001 – H{OFFSET:06d}  │",
        f"  │  Pass 2  D + C   SWEEP={SWEEP:<3} ROWS={ROWS:<3} "
        f"OFFSET={OFFSET:<7} H{OFFSET+1:06d} – H{OFFSET*2:06d}  │",
        f"  │  Pass 3  F + E   SWEEP={SWEEP_EF:<3} ROWS={ROWS_EF:<3} "
        f"OFFSET={OFFSET_EF:<7} H{OFFSET_EF+1:06d} – H{OFFSET_EF+SWEEP_EF*ROWS_EF:06d}  │",
        "  └────────────────────────────────────────────────────────────┘",
        "",
        "  ┌── SECTION COVERAGE ─────────────────────────────────────────┐",
    ]
    section_meta = [
        ('B','1·B+A', N_B, ROWS,    20, B_DECODER, {}),
        ('A','1·B+A', N_A, ROWS,    19, A_DECODER, {}),
        ('D','2·D+C', N_D, ROWS,    20, D_DECODER, _D_DR_PAIRS),
        ('C','2·D+C', N_C, ROWS,    23, C_DECODER, {}),
        ('F','3·F+E', N_F, 11,      18, F_DECODER, {}),
        ('E','3·F+E', N_E, ROWS_EF, 19, E_DECODER, E_DOUBLE_ROW),
    ]
    total = 0
    for sec,pair,cols,rows,inc,dec,dr in section_meta:
        n = sum(1 for v in dec.values() if v[1]>0)
        conf = sum(1 for v in dr.values() if v is not None)//2 if dr else 0
        pend = sum(1 for v in dr.values() if v is None)//2 if dr else 0
        dr_s = f"{conf} pairs" + (f" ({pend} pend)" if pend else "") if conf else "—"
        lines.append(f"  │  {sec} {pair:<7} {cols:>3} cols {rows:>3} rows "
                     f"inc={inc:<3} {n:>5} lots  DR:{dr_s:<18}│")
        total += n
    lines += [
        f"  │  Total: {total:,} lots                                           │",
        "  └────────────────────────────────────────────────────────────┘",
        "",
    ]
    _print_slow(lines, 0.018)

def _do_test_section(sec=None):
    """Run comprehensive tests — all sections or a single one."""

    ALL = {
        'B': [
            ("B","20H",  1,   "H000001", "Row 1  c=1  — first lot in system"),
            ("B","40H",  45,  "H000045", "Row 2  c=1"),
            ("B","60H",  89,  "H000089", "Row 3  c=1"),
            ("B","380H", 793, "H000793", "Row 19 c=1  — last B H-lot"),
            ("B","19A",  2,   "H000002", "Row 1  c=2  — special 19A label"),
            ("B","1",    21,  "H000021", "Row 1  c=21"),
            ("B","12",   22,  "H000022", "Row 1  c=22 — leftmost strip"),
        ],
        'A': [
            ("A","19",   23,  "H000023", "Row 1  c=1  — first A lot"),
            ("A","1",    44,  "H000044", "Row 1  c=22 — last of Pass 1"),
            ("A","13H",  29,  "H000029", "Row 1  c=7  — H-lot"),
            ("A","5H",   38,  "H000038", "Row 1  c=16 — H-lot"),
            ("A","1H",   43,  "H000043", "Row 1  c=21 — H-lot"),
            ("A","361",  815, "H000815", "Row 19 c=1  — last regular A lot"),
        ],
        'D': [
            ("D","1U",   837,  "H000837",  "Row 1  pos 1  — first lot in Pass 2"),
            ("D","20H",  901,  "H000901",  "Row 2  pos 1  — first H-lot"),
            ("D","40H",  944,  "H000944",  "Row 3  pos 1"),
            ("D","1A",   871,  "H000871",  "Row 1  — lettered sub-lot A"),
            ("D","F1",   876,  "H000876",  "Row 1  — F1 lot"),
            ("D","355H", 1678, "H001678",  "Row 20 pos 1  — double-row zone 1 start"),
            ("D","384",  1690, "H001690",  "Row 20 — base lot (single)"),
            ("D","384A", 1690, "H001690A", "Row 20 — 384A: same H as 384 + A"),
            ("D","384B", 1690, "H001690B", "Row 20 — 384B: same H as 384 + B"),
            ("D","376",  1698, "H001698",  "Row 20 — base lot 376"),
            ("D","376A", 1698, "H001698A", "Row 20 — 376A"),
            ("D","376B", 1698, "H001698B", "Row 20 — 376B"),
            ("D","366H", 1721, "H001721",  "Row 21 pos 1  — zone 2 start"),
            ("D","367A", 1741, "H001741A", "Row 21 — zone 2 367A"),
            ("D","367B", 1741, "H001741B", "Row 21 — zone 2 367B"),
            ("D","500",  1827, "H001827",  "Row 23 last   — far-left strip lot"),
        ],
        'C': [
            ("C","19",   880,  "H000880",  "Row 1  pos 1  — first C lot"),
            ("C","1",    900,  "H000900",  "Row 1  last   — last of row 1"),
            ("C","9H",   890,  "H000890",  "Row 1  H-lot"),
            ("C","5H",   895,  "H000895",  "Row 1  H-lot"),
            ("C","263C", 1443, "H001443",  "Row 14 — C-suffix triple lot"),
            ("C","263A", 1445, "H001445",  "Row 14 — A-suffix lot"),
            ("C","384C", 1742, "H001742",  "Row 21 — C-suffix lot"),
            ("C","432C", 1850, "H001850",  "Row 24 pos 1  — first of last row"),
            ("C","417",  1871, "H001871",  "Row 24 last   — end of Pass 2"),
        ],
        'F': [
            ("F","18",   1872, "H001872",  "Row 1  c=1  — first of Pass 3"),
            ("F","17",   1873, "H001873",  "Row 1  c=2"),
            ("F","1",    1889, "H001889",  "Row 1  c=18 — last of F row 1"),
            ("F","36",   1912, "H001912",  "Row 2  c=1"),
            ("F","198",  2270, "H002270",  "Row 11 c=1  — last F lot"),
        ],
        'E': [
            ("E","19",   1890, "H001890",  "Row 1  c=1  — first E lot"),
            ("E","13H",  1896, "H001896",  "Row 1  c=7  — H-lot"),
            ("E","5H",   1906, "H001906",  "Row 1  c=16 — H-lot"),
            ("E","1",    1911, "H001911",  "Row 1  c=22 — last of E row 1"),
            ("E","199A", 2260, "H002260A", "Row 11 c=12 — double-row A (shared H)"),
            ("E","199B", 2260, "H002260B", "Row 11 c=12 — double-row B (same H)"),
            ("E","190A", 2269, "H002269A", "Row 10 c=1  — double-row A"),
            ("E","190B", 2269, "H002269B", "Row 10 c=1  — double-row B"),
            ("E","214",  2331, "H002331",  "Row 12 c=17 — lot 214"),
        ],
        'G': [
            ("G","58",   2414, "H002414", "Row 1 first lot — Section 2 start"),
            ("G","1",    2435, "H002435", "Row 1 last lot"),
            ("G","8H",   2427, "H002427", "Row 1 H-lot"),
            ("G","38H",  2460, "H002460", "Row 2 H-lot"),
            ("G","59",   2459, "H002459", "Row 2 first lot"),
            ("G","60",   2504, "H002504", "Row 3 first lot"),
            ("G","75",   2563, "H002563", "Row 4 last lot — last G lot"),
        ],
        'H': [
            ("H","23",   2436, "H002436", "Row 1 first lot"),
            ("H","1",    2458, "H002458", "Row 1 last lot"),
            ("H","46",   2481, "H002481", "Row 2 first lot"),
            ("H","24",   2503, "H002503", "Row 2 last lot"),
            ("H","92",   2564, "H002564", "Row 4 first lot"),
            ("H","70",   2586, "H002586", "Row 4 last lot — last H lot"),
        ],
        'M': [
            ("M","11",   2587, "H002587", "Row 1 first — Section 3 start"),
            ("M","12",   2588, "H002588", "Row 1 last"),
            ("M","61",   2618, "H002618", "Row 9 last  (gap: skips 56-60)"),
            ("M","70",   2631, "H002631", "Row 12 first"),
            ("M","82",   2638, "H002638", "Row 13 first"),
            ("M","100",  2656, "H002656", "Row 16 first"),
            ("M","160",  2716, "H002716", "Row 26 first"),
            ("M","270",  2826, "H002826", "Row 50 first"),
            ("M","279",  2835, "H002835", "Row 54 last  — system max"),
        ],
        'K': [
            ("K","1",    2836, "H002836", "Row 1  first lot — S4 start"),
            ("K","3",    2838, "H002838", "Row 1  last lot"),
            ("K","6",    2839, "H002839", "Row 2  first lot"),
            ("K","22",   2847, "H002847", "Row 4  single lot"),
            ("K","5",    2848, "H002848", "Row 5  single lot"),
            ("K","246",  2913, "H002913", "Row 35 first lot"),
            ("K","361",  2950, "H002950", "Row 44 last lot — K end"),
        ],
        'J': [
            ("J","1",    2951, "H002951", "Row 1  first lot — J start"),
            ("J","5",    2955, "H002955", "Row 1  last lot"),
            ("J","6",    2956, "H002956", "Row 2  first lot"),
            ("J","47",   2997, "H002997", "Row 7  last lot"),
            ("J","132",  3082, "H003082", "Row 28 last lot — J end"),
        ],
        'I': [
            ("I","1",    3083, "H003083", "Row 1  first lot — I start"),
            ("I","2",    3084, "H003084", "Row 1  last lot"),
            ("I","63",   3145, "H003145", "Row 32 first lot"),
            ("I","64",   3146, "H003146", "Row 32 last lot — I end"),
        ],
        'L': [
            ("L","69",   3147, "H003147", "Row 1  first lot — L start"),
            ("L","73",   3151, "H003151", "Row 1  last lot"),
            ("L","74",   3152, "H003152", "Row 2  first lot"),
            ("L","92",   3170, "H003170", "Row 4  last lot"),
            ("L","107",  3185, "H003185", "Row 7  last lot — system max"),
        ],
    }

    W = 74
    def rule(label):
        dash = max(0, W - len(label) - 8)
        print(f"  ┌── {label} {'─'*dash}┐")

    sections = [sec.upper()] if sec else ['B','A','D','C','F','E','G','H','M','K','J','I','L']
    grand_pass = grand_total = 0
    print()

    for s in sections:
        tests = ALL.get(s)
        if not tests:
            print(f"  ✗  No tests defined for '{s}'. Valid: A B C D E F"); continue

        rule(f"Section {s} — {len(tests)} tests")
        block_pass = 0
        for sec_,lot,exp_h,exp_fmt,desc in tests:
            h, hfmt = h_lot(sec_, lot)
            ok = (h == exp_h and hfmt == exp_fmt)
            mark = "✓" if ok else "✗"
            got  = str(hfmt) if hfmt else "NOT FOUND"
            tail = f"  exp {exp_fmt}" if not ok else ""
            print(f"  │  {mark}  h_lot('{sec_}',{lot:>6})  →  {got:<14}  {desc}{tail}")
            if ok: block_pass += 1

        grand_pass  += block_pass
        grand_total += len(tests)
        pct    = block_pass / len(tests) * 100
        filled = round(28 * block_pass / len(tests))
        bar    = "█" * filled + "░" * (28 - filled)
        print(f"  └─  [{bar}]  {block_pass}/{len(tests)}  ({pct:.0f}%)")
        print()

    if len(sections) > 1:
        pct    = grand_pass / grand_total * 100 if grand_total else 0
        filled = round(40 * grand_pass / grand_total) if grand_total else 0
        bar    = "█" * filled + "░" * (40 - filled)
        inner  = W - 6
        print(f"  ╔{'═'*(W-4)}╗")
        print(f"  ║ {'SECTION TEST SUMMARY':<{inner}} ║")
        print(f"  ╠{'═'*(W-4)}╣")
        print(f"  ║ {'Tests run     : ' + str(grand_total):<{inner}} ║")
        print(f"  ║ {'Tests passed  : ' + str(grand_pass):<{inner}} ║")
        print(f"  ║ {'Accuracy      : ' + f'{pct:.2f}%':<{inner}} ║")
        print(f"  ║ [{bar}]  {grand_pass}/{grand_total}{'':>{inner-len(bar)-6}} ║")
        print(f"  ╠{'═'*(W-4)}╣")
        status = "ALL PASSED ✓" if grand_pass == grand_total else f"{grand_total - grand_pass} FAILURE(S) ✗"
        print(f"  ║ {status:<{inner}} ║")
        print(f"  ╚{'═'*(W-4)}╝")
        print()




# ═══════════════════════════════════════════════════════════════════════
# DISPLAY HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _box(content_lines, width=70):
    """
    Render a box. content_lines is a list of (type, text) tuples:
      ('head', text)  → bold section header row  ╠═╣
      ('row',  text)  → normal content row        ║ text ║
      ('div',  '')    → thin divider              ╟─╢
    width = total outer width including ║ chars.
    """
    inner = width - 4   # space between ║ and ║
    out = []
    out.append(f"  ╔{'═'*(width-4)}╗")
    for kind, text in content_lines:
        if kind == 'head':
            out.append(f"  ╠{'═'*(width-4)}╣")
            out.append(f"  ║ {text:<{inner}} ║")
        elif kind == 'div':
            out.append(f"  ╟{'─'*(width-4)}╢")
        else:
            out.append(f"  ║ {text:<{inner}} ║")
    out.append(f"  ╚{'═'*(width-4)}╝")
    return '\n'.join(out)


def _section_block(title, rows, footer, width=70):
    """
    Render a plain ┌─┐ block.
    rows = list of strings (each trimmed to width-6 chars).
    """
    inner = width - 6
    dash  = width - len(title) - 8
    out   = [f"  ┌── {title} {'─'*max(0,dash)}┐"]
    for r in rows:
        out.append(f"  │  {r[:inner]:<{inner}}  │")
    if footer:
        out.append(f"  ├{'─'*(width-4)}┤")
        out.append(f"  │  {footer[:inner]:<{inner}}  │")
    out.append(f"  └{'─'*(width-4)}┘")
    return '\n'.join(out)


def _stats():
    W = 70
    I = W - 6   # inner content width for ┌─┐ blocks

    # ── Gather numbers ────────────────────────────────────────────────
    s1_B = sum(1 for v in B_DECODER.values() if v[1] > 0)
    s1_A = sum(1 for v in A_DECODER.values() if v[1] > 0)
    s1_D, s1_C = len(_D_LOT_H), len(_C_LOT_H)
    s1_F, s1_E = len(_F_LOT_H), len(_E_LOT_H)
    s1 = s1_B + s1_A + s1_D + s1_C + s1_F + s1_E

    s2_B, s2_D, s2_F = len(_B2_LOT_H), len(_D2_LOT_H), len(_F2_LOT_H)
    s2_G, s2_H = len(_G_LOT_H), len(_H_LOT_H)
    s2 = s2_B + s2_D + s2_F + s2_G + s2_H

    s3_M  = len(_M_LOT_H)
    s4    = len(_K_LOT_H)+len(_J_LOT_H)+len(_I_LOT_H)+len(_L_LOT_H)
    grand = s1 + s2 + s3_M + s4

    # ── Summary header ────────────────────────────────────────────────
    hdr = _box([
        ('row', 'CEDAR GROVE CEMETERY  ·  H-Number Decoder'),
        ('row', 'University of Notre Dame  ·  Notre Dame, Indiana'),
        ('div', ''),
        ('row', f"{'System range':<22} H000001  –  H{_S4_MAX_H:06d}"),
        ('row', f"{'Total H numbers':<22} {_S4_MAX_H:,}"),
        ('row', f"{'Lots catalogued':<22} {grand:,}"),
        ('row', f"{'Sections':<22} A  B  C  D  E  F  G  H  I  J  K  L  M"),
        ('div', ''),
        ('row', f"{'Section 4':<22} K  J  I  L   ·   H{_S3_MAX_H+1:06d} – H{_S4_MAX_H:06d}"),
    ], W)
    print()
    print(hdr)
    print()

    # ── Section 1 ─────────────────────────────────────────────────────
    COL = f"{'Sec':<6}{'Lots':>5}  H Range"
    SEP = f"{'─'*6}{'─'*5}  {'─'*20}"
    rows1 = [
        COL, SEP,
        f"{'B':<6}{s1_B:>5}  H000001 – H{OFFSET:06d}      (Pass 1 · interleaved with A)",
        f"{'A':<6}{s1_A:>5}  H000001 – H{OFFSET:06d}      (Pass 1 · interleaved with B)",
        f"{'D':<6}{s1_D:>5}  H{OFFSET+1:06d} – H{_DC_MAX_H:06d}  (Pass 2 · interleaved with C)",
        f"{'C':<6}{s1_C:>5}  H{OFFSET+1:06d} – H{_DC_MAX_H:06d}  (Pass 2 · interleaved with D)",
        f"{'F':<6}{s1_F:>5}  H{_DC_MAX_H+1:06d} – H{_EF_MAX_H:06d}  (Pass 3 · interleaved with E)",
        f"{'E':<6}{s1_E:>5}  H{_DC_MAX_H+1:06d} – H{_EF_MAX_H:06d}  (Pass 3 · interleaved with F)",
        SEP,
    ]
    footer1 = f"{'TOTAL':<6}{s1:>5}  H000001 – H{_EF_MAX_H:06d}"
    print(_section_block(f"SECTION 1 · THE GRID  ·  H000001 – H{_EF_MAX_H:06d}", rows1, footer1, W))
    print()

    # ── Section 2 ─────────────────────────────────────────────────────
    rows2 = [
        COL, SEP,
        f"{'B':<6}{s2_B:>5}  H{min(_B2_LOT_H.values()):06d} – H{max(_B2_LOT_H.values()):06d}  (North curved edge strip)",
        f"{'D':<6}{s2_D:>5}  H{min(_D2_LOT_H.values()):06d} – H{max(_D2_LOT_H.values()):06d}  (North curved edge strip)",
        f"{'F':<6}{s2_F:>5}  H{min(_F2_LOT_H.values()):06d} – H{max(_F2_LOT_H.values()):06d}  (Side strip)",
        f"{'G':<6}{s2_G:>5}  H{min(_G_LOT_H.values()):06d} – H{max(_G_LOT_H.values()):06d}  (Section G · alt. rows with H)",
        f"{'H':<6}{s2_H:>5}  H{min(_H_LOT_H.values()):06d} – H{max(_H_LOT_H.values()):06d}  (Section H · alt. rows with G)",
        SEP,
    ]
    footer2 = f"{'TOTAL':<6}{s2:>5}  H{_EF_MAX_H+1:06d} – H{_S2_MAX_H:06d}"
    print(_section_block(f"SECTION 2 · THE MARGINS  ·  H{_EF_MAX_H+1:06d} – H{_S2_MAX_H:06d}", rows2, footer2, W))
    print()

    # ── Section 3 ─────────────────────────────────────────────────────
    rows3 = [
        COL, SEP,
        f"{'M':<6}{s3_M:>5}  H{_S2_MAX_H+1:06d} – H{_S3_MAX_H:06d}  (54 rows, lots 11–279)",
        SEP,
    ]
    footer3 = f"{'TOTAL':<6}{s3_M:>5}  H{_S2_MAX_H+1:06d} – H{_S3_MAX_H:06d}"
    print(_section_block(f"SECTION 3 · SECTION M  ·  H{_S2_MAX_H+1:06d} – H{_S3_MAX_H:06d}", rows3, footer3, W))
    print()

    # ── Section 4 ─────────────────────────────────────────────────────
    s4_K = len(_K_LOT_H); s4_J = len(_J_LOT_H)
    s4_I = len(_I_LOT_H); s4_L = len(_L_LOT_H)
    s4_total = s4_K + s4_J + s4_I + s4_L
    rows4 = [
        COL, SEP,
        f"{'K':<6}{s4_K:>5}  H{min(_K_LOT_H.values()):06d} – H{max(_K_LOT_H.values()):06d}  (44 rows)",
        f"{'J':<6}{s4_J:>5}  H{min(_J_LOT_H.values()):06d} – H{max(_J_LOT_H.values()):06d}  (28 rows)",
        f"{'I':<6}{s4_I:>5}  H{min(_I_LOT_H.values()):06d} – H{max(_I_LOT_H.values()):06d}  (32 rows, 2 lots each)",
        f"{'L':<6}{s4_L:>5}  H{min(_L_LOT_H.values()):06d} – H{max(_L_LOT_H.values()):06d}  (7 rows)",
        SEP,
    ]
    footer4 = f"{'TOTAL':<6}{s4_total:>5}  H{_S3_MAX_H+1:06d} – H{_S4_MAX_H:06d}"
    print(_section_block(f"SECTION 4 · K J I L  ·  H{_S3_MAX_H+1:06d} – H{_S4_MAX_H:06d}", rows4, footer4, W))
    print()


def _help():
    W = 70
    I = W - 6

    def cmd_block(title, items):
        rows = []
        for cmd, desc in items:
            if cmd:
                rows.append(f"  {cmd:<28} {desc}")
            else:
                rows.append(desc)
        return _section_block(title, rows, None, W)

    print()
    print(_box([
        ('row', 'CEDAR GROVE CEMETERY  ·  H-Number Decoder'),
        ('row', 'Command Reference'),
    ], W))
    print()

    print(_section_block("LOOKUP", [
        "lookup <section> <lot>            Compute the H lot number.",
        "lookup <section> <lot> <grave>    Compute the H grave number (1-9).",
        "",
        "lookup B 20H             →  H000001",
        "lookup D 384A            →  H001690A   (double-row lot)",
        "lookup D 376B 3          →  H001698B3  (double-row grave)",
        "lookup E 199A 2          →  H002260A2  (double-row grave)",
        "lookup B 390C            →  H002364    (B margin sub-lot)",
        "lookup G 58              →  H002414    (Section G)",
        "lookup M 279             →  H002835    (Section M last lot)",
    ], None, W))
    print()

    print(_section_block("REVERSE", [
        "reverse <H>    Find which section and lot owns an H number.",
        "               Accepts H002835, 002835, or 2835.",
        "",
        "reverse 1            →  Section B  Lot 20H",
        "reverse H000837      →  Section D  Lot 1U",
        "reverse 2587         →  Section M  Lot 11",
        "reverse 2414         →  Section G  Lot 58",
    ], None, W))
    print()

    print(_section_block("TESTING", [
        "test              Full accuracy suite (47 anchors across all sections).",
        "test <section>    Section-specific anchor tests.",
        "",
        "Sections:  A  B  C  D  E  F  G  H  I  J  K  L  M",
        "           test K  →  Section K anchor tests",
        "           test J  →  Section J anchor tests",
        "           test M  →  Section M anchor tests",
    ], None, W))
    print()

    print(_section_block("TABLES & EXPORT", [
        "table <section>   Print all lots sorted by H number.",
        "export [dir]      Save all 9 section CSVs (default: current dir).",
        "",
        "table M           →  249 lots, H002587–H002835",
        "table G           →  80 lots",
        "export            →  saves A B C D E F G H M csv files",
    ], None, W))
    print()

    print(_section_block("INFORMATION", [
        "stats    Full coverage breakdown across all 4 H-number sections.",
        "info     Quick constants and range reference.",
        "help     This command reference.",
        "quit     Exit  (also: exit  or  q).",
    ], None, W))
    print()


def _info():
    W = 70
    print()
    rows = [
        f"{'Pass 1  B + A':<20} SWEEP=44   ROWS=19   OFFSET=0",
        f"{'':20} H000001 – H{OFFSET:06d}",
        "",
        f"{'Pass 2  D + C':<20} Table-driven (variable row widths)",
        f"{'':20} H{OFFSET+1:06d} – H{_DC_MAX_H:06d}",
        "",
        f"{'Pass 3  F + E':<20} Table-driven (variable row widths)",
        f"{'':20} H{_DC_MAX_H+1:06d} – H{_EF_MAX_H:06d}",
        "",
        f"{'Section 2 Margins':<20} B/D/F strips  +  G  +  H",
        f"{'':20} H{_EF_MAX_H+1:06d} – H{_S2_MAX_H:06d}",
        "",
        f"{'Section 3  M':<20} 54 rows, lots 11–279",
        f"{'':20} H{_S2_MAX_H+1:06d} – H{_S3_MAX_H:06d}",
        "",
        f"{'Section 4  K J I L':<20} H{_S3_MAX_H+1:06d} – H{_S4_MAX_H:06d}",
        "",
        f"{'System max':<20} H{_S4_MAX_H:06d}  ({_S4_MAX_H:,} H numbers)",
    ]
    print(_section_block("SYSTEM CONSTANTS  ·  Quick Reference", rows, None, W))
    print()


def interactive():
    W = 70
    print()
    print(_box([
        ('row', 'CEDAR GROVE CEMETERY  ·  H-Number Decoder'),
        ('row', 'University of Notre Dame  ·  Notre Dame, Indiana'),
        ('div', ''),
        ('row', f"H000001 – H{_S3_MAX_H:06d}   ·   Sections: A B C D E F G H M"),
        ('row', f"Section 4: K J I L  ·  Type  help  to get started"),
    ], W))
    print()

    while True:
        try:
            raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye."); break
        if not raw:
            continue
        parts = raw.split()
        cmd   = parts[0].lower()

        if cmd in ('quit', 'exit', 'q'):
            print("  Goodbye."); break

        elif cmd == 'lookup':
            if len(parts) < 3:
                print("  Usage:  lookup <section> <lot> [grave]"); continue
            grv = int(parts[3]) if len(parts) >= 4 else None
            _show(parts[1], parts[2], grv)

        elif cmd == 'reverse':
            if len(parts) < 2:
                print("  Usage:  reverse <H-number>"); continue
            raw_n = parts[1].upper().lstrip('H').lstrip('0') or '0'
            try:
                n = int(raw_n)
            except ValueError:
                print(f"  Invalid H number: {parts[1]}"); continue
            res = decode_h(n)
            if res is None:
                print(f"\n  H{n:06d} is out of range.  System max: H{_S3_MAX_H:06d}\n")
            else:
                print(f"\n  {res['h_formatted']}  →  Section {res['section']}  ·  Lot {res['lot_label']}\n")

        elif cmd == 'test':
            sec = parts[1].upper() if len(parts) >= 2 else None
            _do_test_section(sec) if sec else self_test()

        elif cmd == 'table':
            if len(parts) < 2:
                print("  Usage:  table <section>  (A B C D E F G H M)"); continue
            sec_up = parts[1].upper()
            rows = full_table(sec_up)
            if not rows:
                print(f"  No lots found for '{sec_up}'."); continue
            print(f"\n  Section {sec_up} — {len(rows)} lots\n")
            print(f"  {'H Lot':<12} {'Lot':<10} {'Grave 1':<12} {'Grave 2':<12} {'Grave 3'}")
            print(f"  {'─'*60}")
            for row in rows:
                print(f"  {row['h_lot']:<12} {row['lot_label']:<10} "
                      f"{row.get('h_grave_1','—'):<12} {row.get('h_grave_2','—'):<12} "
                      f"{row.get('h_grave_3','—')}")
            print()

        elif cmd == 'export':
            out = parts[1] if len(parts) >= 2 else '.'
            import os
            print(f"\n  Exporting to: {os.path.abspath(out)}")
            export_all_csv(out)
            print()

        elif cmd == 'stats':
            _stats()

        elif cmd == 'info':
            _info()

        elif cmd == 'help':
            _help()

        else:
            print(f"  Unknown command '{cmd}'.  Type  help  for the command list.")


if __name__ == "__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1]=="--test": self_test(); sys.exit(0)
    if len(sys.argv)>1 and sys.argv[1]=="--export":
        export_all_csv(sys.argv[2] if len(sys.argv)>2 else "."); sys.exit(0)
    if len(sys.argv)>=3 and sys.argv[1] not in ("--test","--export"):
        grv=int(sys.argv[3]) if len(sys.argv)>3 else None
        _show(sys.argv[1],sys.argv[2],grv); sys.exit(0)
    interactive()
