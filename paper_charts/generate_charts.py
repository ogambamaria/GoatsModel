import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

os.makedirs("charts", exist_ok=True)

# ── Styling ──────────────────────────────────────────────────────────────────
COLORS = {
    "dairy":    "#1f77b4",
    "beef":     "#d62728",
    "goats":    "#2ca02c",
    "sheep":    "#9467bd",
    "camels":   "#8c564b",
    "poultry":  "#e377c2",
    "apiculture":"#bcbd22",
    "pigs":     "#ff7f0e",
    "rabbits":  "#17becf",
}

plt.rcParams.update({
    "font.family":      "serif",
    "font.size":        9,
    "axes.titlesize":   10,
    "axes.labelsize":   9,
    "legend.fontsize":  8,
    "xtick.labelsize":  8,
    "ytick.labelsize":  8,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "figure.dpi":       150,
})

YEARS     = list(range(2019, 2042))
VAL_YEARS = list(range(2020, 2026))   # validation window
PRJ_YEARS = list(range(2026, 2042))   # projection window

def clean(s):
    """Strip commas and convert to float; return NaN on failure."""
    try:
        return float(str(s).replace(",", "").strip())
    except:
        return np.nan

def shade_validation(ax, alpha=0.08):
    ax.axvspan(2020, 2025, color="grey", alpha=alpha)

def millions(x, _):  return f"{x/1e6:.1f}M"
def billions(x, _):  return f"{x/1e9:.2f}B"
def thousands(x, _): return f"{x/1e3:.0f}k"

# ── Raw data (all values as strings matching CSV) ────────────────────────────
data = {
    # RUMINANTS ─ Population
    "dairy_pop":   [4536553,4724213,4930885,5150652,5384433,5643528,5929195,6229572,6545364,6877312,7226205,7592880,7978220,8383157,8808678,9255823,9725682,10219406,10738202,11283340,11856156,12458058,13090518],
    "beef_pop":    [16640373,17318289,18227105,19271976,20435898,21713771,23167556,24760512,26470095,28302392,30264608,32364899,34612283,37016605,39588523,42339522,45281939,48429006,51794904,55394809,59244967,63362754,67766769],
    "goat_pop":    [34657969,38799923,40989145,43205818,45615188,48164175,50854376,53694678,56693632,59860088,63203397,66733436,70460636,74396007,78551176,82938421,87570702,92461705,97625881,103078487,108835631,114914325,121332525],
    "sheep_pop":   [27440945,27804845,28213956,29657962,30826464,31951592,33098524,34272326,35470828,36694072,37943578,39221260,40529053,41868834,43242450,44651710,46098409,47584333,49111260,50680971,52295248,53955893,55664712],
    "camel_pop":   [4721900,4929617,5246341,5597537,5953482,6307322,6660619,7016975,7379901,7752367,8136813,8535274,8949515,9381082,9831410,10301833,10793641,11308092,11846453,12409983,12999984,13617787,14264763],
    # RUMINANTS ─ Production
    "dairy_milk":  [3087368416,3327251942,3478907825,3643020340,3818910429,4006225798,4204857951,4414884749,4636523186,4870101303,5116035213,5374815065,5646994826,5933180799,6234032895,6550258254,6882609966,7231887074,7598933294,7984640848,8389949184,8815848808,9263381283],
    "beef_prod":   [322144382,445106919,430076921,430701505,444601892,466824542,478670424,503042485,537164288,574123896,613877045,656496142,702120920,750932894,803142465,858979464,918694716,982557320,1050856599,1123901657,1202022152,1285570862,1374926402],
    "goat_milk":   [156322451,138747530,177177532,190059945,199593743,210632194,222413125,234838304,247954305,261802993,276425228,291864146,308165357,325377024,343549999,362737971,382997630,404388834,426974779,450822197,476001541,502587204,530657730],
    "goat_meat":   [53888699,574661150,575819227,609034680,643793421,679763354,717715227,757800187,800125127,844813786,891998366,941818303,994420787,1049961228,1108603717,1170521508,1235897535,1304924948,1377807683,1454761068,1536012458,1621801904,1712382868],
    "sheep_mutton":[49378634,127862456,103600372,86709061,93201929,97176370,100364950,103556059,106878470,110317323,113858219,117499118,121243087,125094331,129057157,133135856,137334747,141658208,146110688,150696719,155420925,160288025,165302845],
    "sheep_wool":  [840111,2200047,2165005,2197333,2259737,2329972,2402390,2477059,2554048,2633430,2715280,2799674,2886690,2976412,3068922,3164307,3262657,3364063,3468622,3576430,3687589,3802203,3920380],
    "camel_meat":  [57569433,59575664,70467250,80113230,88579916,96397822,103863357,111108513,118208350,125234225,132258603,139351153,146576375,153990008,161638636,169563513,177799181,186378339,195328356,204678202,214451127,224674095,235371417],
    "camel_milk":  [985030518,1897135425,2115780076,2286734962,2424225712,2548658250,2671810313,2798782200,2931441638,3070456202,3216156639,3368822738,3528757238,3696289874,3871775362,4055593726,4248140850,4449828150,4661091337,4882386713,5114185087,5356992713,5611326976],
    # RUMINANTS ─ Feed
    "dairy_feed":  [14297334,15064338,15652233,16283617,16962078,17747721,18645904,19590366,20583328,21627120,22724217,23877249,25088988,26362359,27700469,29106582,30584127,32136722,33768162,35482440,37283756,39176543,41165421],
    "beef_feed":   [57386494,58790745,60448320,63011455,66262040,70038712,74614927,79737039,85247372,91157076,97485755,104258000,111504000,119253000,127542000,136407000,145888000,156028000,166873000,178472000,190877000,204144000,218333000],
    "goat_feed":   [np.nan,10528051,12235330,12926162,13623188,14382785,15186534,16034779,16930347,17875941,18874349,19928520,21041569,22216783,23457636,24767793,26151125,27611719,29153891,30782195,32501444,34316716,np.nan],  # 2041 excluded (bad data)
    "sheep_feed":  [np.nan,7988541,8309244,8314382,8638786,8985365,9331551,9680832,10035035,10395078,10761641,11135367,11516883,11906804,12305727,12714237,13132905,13562295,14002963,14455462,14920340,15398148,15889434],
    "camel_feed":  [10207641,13473952,14723394,15953510,17132017,18274211,19398579,20519211,21647191,22792156,23962797,25166876,26411282,27702083,29044663,30443907,31904326,33430184,35025593,36694621,38441274,40269703,42184062],
    # NON-RUMINANTS ─ Population
    "poultry_ind": [46293265,47556649,48855684,50195999,51595001,53095713,54773766,56710198,58923236,61314719,63707443,65959710,68044320,70023483,71975093,73949670,75969644,78042922,80172476,82360100,84607413,86916047,89287675],
    "poultry_lay": [12844219,12853484,12864074,12880131,12912985,12983599,13114406,13308027,13531602,13731383,13869723,13945568,13981141,13998592,14010125,14020231,14030085,14039910,14049738,14059573,14069415,14079263,14089119],
    "poultry_bro": [45838194,45873744,45924155,46027766,46266464,46740986,47476857,48340935,49101994,49605599,49862852,49975349,50030266,50069068,50104646,50139774,50174876,50209999,50245146,50280317,50315514,50350734,50385980],
    "api_log":     [852241,890098,953047,1018446,1086115,1155837,1227361,1300404,1374653,1449772,1525404,1601182,1676729,1751673,1825647,1898299,1969297,2038337,2105144,2169476,2231128,2289933,2345760],
    "api_ktbh":    [220501,231757,251508,272408,294443,317589,341810,367057,393271,420380,448302,476947,506215,536005,566208,596715,627418,658212,688993,719667,750144,780345,810198],
    "api_lang":    [194788,200883,209339,217722,225980,234056,241894,249437,256629,263416,269748,275578,280864,285573,289674,293149,295982,298167,299706,300606,300882,300555,299650],
    "api_box":     [21624,22301,23239,24170,25087,25983,26853,27691,28489,29243,29946,30593,31180,31702,32158,32543,32858,33100,33271,33371,33402,33366,33265],
    "pig_pop":     [596413,606557,644030,683673,725627,770031,817041,866815,919520,975340,1034466,1097095,1163443,1233734,1308210,1387122,1470741,1559349,1653247,1752756,1858212,1969978,2088430],
    "rabbit_pop":  [737239,837300,891348,949302,1011388,1077855,1148969,1225021,1306320,1393202,1486027,1585180,1691074,1804151,1924885,2053783,2191386,2338272,2495059,2662408,2841025,3031662,3235123],
    # NON-RUMINANTS ─ Production
    "poultry_eggs":[np.nan,180376167,181574694,182867444,184393000,186416806,189247556,192981389,197273722,201454194,204962944,207670417,209797083,211637472,213390139,215146306,216937444,218772750,220655028,222585750,224566278,226597944,228682250],  # 2019 anomalous
    "poultry_meat":[82414052,83088027,83798980,84599396,85604052,86964888,88752568,90834821,92921033,94762272,96284855,97550027,98657252,99691183,100707242,101734133,102783552,103859491,104963429,106096261,107258790,108451827,109676204],
    "api_honey":   [13876800,14525577,15786411,17170799,18705033,20420870,22351256,24043411,25315593,26599273,27888703,29177984,30461180,31732428,32986051,34216660,35419249,36589275,37722721,38816146,39824979,40743100,41614591],
    "api_wax":     [1374400,2173060,2368663,2583849,2822717,3090227,3391565,3658062,3861664,4067823,4275637,4484173,4692484,4899623,5104666,5306726,5504969,5698629,5887017,6069532,6239130,6394749,6543217],
    "pig_meat":    [14440964,14982273,15581564,16204827,16853020,17527140,18228226,18957355,19715649,20504275,21324446,22177424,23064521,23987102,24946586,25944450,26982228,28061517,29183977,30351336,31565390,32828005,34141126],
    "rabbit_meat": [1761900,1624003,1698627,1776735,1858482,1944031,2033556,2127235,2225257,2327821,2435134,2547412,2664883,2787785,2916368,3050893,3191632,3338872,3492913,3654066,3822659,3999037,4183556],
    # NON-RUMINANTS ─ Feed
    "poultry_feed":[1873467,1899514,1926442,1954802,1985984,2022483,2067125,2120991,2181507,2243008,2299928,2349864,2393928,2434796,2474769,2515123,2556373,2598691,2642138,2686751,2732562,2779604,2827910],
    "api_nectar":  [851656,899837,963817,1031495,1103083,1178749,1258552,1342368,1429813,1520211,1612628,1705967,1785629,1864583,1942407,2018728,2093218,2165599,2235635,2303128,2367922,2429892,2488950],
    "pig_feed":    [448225,472832,492585,513067,534300,556332,579189,602911,627540,653112,679669,707255,735909,765683,796621,828772,862184,896911,933011,970537,1009546,1050101,1092265],
    "rabbit_feed": [18268,20878,21765,22703,23692,24735,25832,26985,28197,29468,30802,32201,33667,35203,36813,38498,40263,42111,44046,46070,48190,50407,52728],
}

yrs = np.array(YEARS)

def cagr(series, y0=2019, y1=2041):
    idx0 = YEARS.index(y0)
    idx1 = YEARS.index(y1)
    v0 = series[idx0]
    v1 = series[idx1]
    if np.isnan(v0) or np.isnan(v1) or v0 <= 0:
        return np.nan
    n = y1 - y0
    return ((v1 / v0) ** (1 / n) - 1) * 100

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Ruminant Population
# ═══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
fig.suptitle("Ruminant Population Projections (2019-2041)", fontsize=10, fontweight="bold")

# Left: cattle (dairy + beef)
ax = axes[0]
ax.plot(yrs, np.array(data["dairy_pop"])/1e6, color=COLORS["dairy"], lw=1.8, label="Dairy cattle")
ax.plot(yrs, np.array(data["beef_pop"])/1e6,  color=COLORS["beef"],  lw=1.8, label="Beef cattle")
# shade_validation(ax)
ax.set_title("Cattle")
ax.set_xlabel("Year"); ax.set_ylabel("Population (millions)")
ax.legend(); ax.set_xlim(2019, 2041)

# Right: small ruminants + camels
ax = axes[1]
ax.plot(yrs, np.array(data["goat_pop"])/1e6,  color=COLORS["goats"],  lw=1.8, label="Goats")
ax.plot(yrs, np.array(data["sheep_pop"])/1e6, color=COLORS["sheep"],  lw=1.8, label="Sheep")
ax.plot(yrs, np.array(data["camel_pop"])/1e6, color=COLORS["camels"], lw=1.8, label="Camels")
# shade_validation(ax)
ax.set_title("Small Ruminants & Camels")
ax.set_xlabel("Year"); ax.set_ylabel("Population (millions)")
ax.legend(); ax.set_xlim(2019, 2041)

plt.tight_layout()
plt.savefig("paper_charts/ruminant_pop.png", bbox_inches="tight")
plt.close()
print("Fig 1 done")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Ruminant Production
# ═══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
fig.suptitle("Ruminant Production Projections (2019-2041)", fontsize=10, fontweight="bold")

ax = axes[0]
ax.plot(yrs, np.array(data["dairy_milk"])/1e9,  color=COLORS["dairy"],  lw=1.8, label="Dairy milk")
ax.plot(yrs, np.array(data["camel_milk"])/1e9,  color=COLORS["camels"], lw=1.8, label="Camel milk")
ax.plot(yrs, np.array(data["goat_milk"])/1e9,   color=COLORS["goats"],  lw=1.8, label="Goat milk")
# shade_validation(ax)
ax.set_title("Milk Production")
ax.set_xlabel("Year"); ax.set_ylabel("Production (billion kg)")
ax.legend(); ax.set_xlim(2019, 2041)

ax = axes[1]
ax.plot(yrs, np.array(data["beef_prod"])/1e9,    color=COLORS["beef"],   lw=1.8, label="Beef")
ax.plot(yrs, np.array(data["goat_meat"])/1e9,    color=COLORS["goats"],  lw=1.8, label="Chevon")
ax.plot(yrs, np.array(data["sheep_mutton"])/1e6, color=COLORS["sheep"],  lw=1.8, label="Mutton (M kg)")
ax.plot(yrs, np.array(data["camel_meat"])/1e6,   color=COLORS["camels"], lw=1.8, label="Camel meat (M kg)")
# shade_validation(ax)
ax.set_title("Meat Production")
ax.set_xlabel("Year"); ax.set_ylabel("Production (billion kg / M kg)")
ax.legend(fontsize=7); ax.set_xlim(2019, 2041)

plt.tight_layout()
plt.savefig("paper_charts/ruminant_prod.png", bbox_inches="tight")
plt.close()
print("Fig 2 done")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Ruminant Feed
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7.2, 3.2))
fig.suptitle("Ruminant Feed Demand Projections (2019-2041)", fontsize=10, fontweight="bold")

goat_y  = [v/1e6 if not np.isnan(v) else np.nan for v in data["goat_feed"]]
sheep_y = [v/1e6 if not np.isnan(v) else np.nan for v in data["sheep_feed"]]

ax.plot(yrs, np.array(data["beef_feed"])/1e6,  color=COLORS["beef"],   lw=1.8, label="Beef cattle")
ax.plot(yrs, np.array(data["dairy_feed"])/1e6, color=COLORS["dairy"],  lw=1.8, label="Dairy cattle")
ax.plot(yrs, np.array(data["camel_feed"])/1e6, color=COLORS["camels"], lw=1.8, label="Camels")
ax.plot(yrs, goat_y,  color=COLORS["goats"],   lw=1.8, linestyle="--", label="Goats (2020-2040)")
ax.plot(yrs, sheep_y, color=COLORS["sheep"],   lw=1.8, linestyle="--", label="Sheep (2020-2041)")
# shade_validation(ax)
ax.set_xlabel("Year"); ax.set_ylabel("Feed Demand (million tonnes DM)")
ax.legend(ncol=2, fontsize=7.5); ax.set_xlim(2019, 2041)

plt.tight_layout()
plt.savefig("paper_charts/ruminant_feed.png", bbox_inches="tight")
plt.close()
print("Fig 3 done")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Non-ruminant Population
# ═══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2))
fig.suptitle("Non-Ruminant Population Projections (2019-2041)", fontsize=10, fontweight="bold")

ax = axes[0]
ax.plot(yrs, np.array(data["poultry_ind"])/1e6, color=COLORS["poultry"],     lw=1.8, label="Indigenous")
ax.plot(yrs, np.array(data["poultry_lay"])/1e6, color=COLORS["apiculture"],  lw=1.8, label="Layers", linestyle="--")
ax.plot(yrs, np.array(data["poultry_bro"])/1e6, color=COLORS["pigs"],        lw=1.8, label="Broilers", linestyle=":")
# shade_validation(ax)
ax.set_title("Poultry")
ax.set_xlabel("Year"); ax.set_ylabel("Population (millions)")
ax.legend(); ax.set_xlim(2019, 2041)

ax = axes[1]
ax_r = ax.twinx()
api_total = [sum(x) for x in zip(data["api_log"], data["api_ktbh"], data["api_lang"], data["api_box"])]
ax.plot(yrs,   np.array(data["pig_pop"])/1e6,    color=COLORS["pigs"],       lw=1.8, label="Pigs")
ax.plot(yrs,   np.array(data["rabbit_pop"])/1e6, color=COLORS["rabbits"],    lw=1.8, label="Rabbits", linestyle="--")
ax_r.plot(yrs, np.array(api_total)/1e6,          color=COLORS["apiculture"], lw=1.8, label="Total hives", linestyle=":")
ax.set_title("Pigs, Rabbits & Apiculture")
ax.set_xlabel("Year"); ax.set_ylabel("Population (millions)")
ax_r.set_ylabel("Hive count (millions)", color=COLORS["apiculture"])
ax_r.tick_params(axis='y', labelcolor=COLORS["apiculture"])
ax_r.spines["top"].set_visible(False)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax_r.get_legend_handles_labels()
ax.legend(lines1+lines2, labels1+labels2, fontsize=7.5)
# shade_validation(ax); ax.set_xlim(2019, 2041)

plt.tight_layout()
plt.savefig("paper_charts/nonrum_pop.png", bbox_inches="tight")
plt.close()
print("Fig 4 done")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — Non-ruminant Production
# ══════════════════════════════════
ax.plot(yrs, np.array(data["poultry_meat"])/1e6, color=COLORS["poultry"],    lw=1.8, label="Poultry meat")
ax.plot(yrs, np.array(data["pig_meat"])/1e6,     color=COLORS["pigs"],       lw=1.8, label="Pork")
ax.plot(yrs, np.array(data["rabbit_meat"])/1e6,  color=COLORS["rabbits"],    lw=1.8, label="Rabbit meat", linestyle="--")
ax.plot(yrs, np.array(data["api_honey"])/1e6,    color=COLORS["apiculture"], lw=1.8, label="Honey", linestyle=":")
# shade_validation(ax)
ax.set_title("Meat & Honey")
ax.set_xlabel("Year"); ax.set_ylabel("Production (million kg)")
ax.legend(fontsize=7.5); ax.set_xlim(2019, 2041)

ax = axes[1]
egg_y = [v/1e6 if not np.isnan(v) else np.nan for v in data["poultry_eggs"]]
ax.plot(yrs, egg_y,                               color=COLORS["poultry"],    lw=1.8, label="Eggs (M trays)")
ax.plot(yrs, np.array(data["api_wax"])/1e6,       color=COLORS["apiculture"], lw=1.8, label="Beeswax", linestyle=":")
# shade_validation(ax)
ax.set_title("Eggs \& Wax")
ax.set_xlabel("Year"); ax.set_ylabel("Production (million trays / million kg)")
ax.legend(fontsize=7.5); ax.set_xlim(2019, 2041)
ax.annotate("2019 baseline\nexcluded (unit\nmismatch)", xy=(2020, egg_y[1]),
            xytext=(2024, egg_y[1]*0.985), fontsize=6.5, color="grey",
            arrowprops=dict(arrowstyle="->", color="grey", lw=0.8))

plt.tight_layout()
plt.savefig("paper_charts/nonrum_prod.png", bbox_inches="tight")
plt.close()
print("Fig 5 done")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 6 — Non-ruminant Feed
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7.2, 3.2))
fig.suptitle("Non-Ruminant Feed Demand Projections (2019-2041)", fontsize=10, fontweight="bold")

ax.plot(yrs, np.array(data["poultry_feed"])/1e6, color=COLORS["poultry"],    lw=1.8, label="Poultry (DMI)")
ax.plot(yrs, np.array(data["pig_feed"])/1e6,     color=COLORS["pigs"],       lw=1.8, label="Pigs (DMI)")
ax.plot(yrs, np.array(data["rabbit_feed"])/1e3,  color=COLORS["rabbits"],    lw=1.8, label="Rabbits (kt DM)", linestyle="--")
ax.plot(yrs, np.array(data["api_nectar"])/1e6,   color=COLORS["apiculture"], lw=1.8, label="Apiculture (nectar)", linestyle=":")
# shade_validation(ax)
ax.set_xlabel("Year"); ax.set_ylabel("Feed / Nectar Demand (million tonnes)")
ax.legend(fontsize=8); ax.set_xlim(2019, 2041)

plt.tight_layout()
plt.savefig("paper_charts/nonrum_feed.png", bbox_inches="tight")
plt.close()
print("Fig 6 done")

# ═══════════════════════════════════════════════════════════════════════════════
# CAGR TABLE (printed for LaTeX)
# ═══════════════════════════════════════════════════════════════════════════════
cagr_data = {
    # (display name, domain, series key, note)
    ("Dairy cattle",  "Population",  "dairy_pop",    ""):  None,
    ("Beef cattle",   "Population",  "beef_pop",     ""):  None,
    ("Goats",         "Population",  "goat_pop",     ""):  None,
    ("Sheep",         "Population",  "sheep_pop",    ""):  None,
    ("Camels",        "Population",  "camel_pop",    ""):  None,
    ("Dairy cattle",  "Production",  "dairy_milk",   "milk kg"):  None,
    ("Beef cattle",   "Production",  "beef_prod",    "meat kg"):  None,
    ("Goats",         "Production",  "goat_milk",    "milk kg"):  None,
    ("Goats",         "Production",  "goat_meat",    "meat kg"):  None,
    ("Sheep",         "Production",  "sheep_mutton", "mutton kg"):None,
    ("Sheep",         "Production",  "sheep_wool",   "wool kg"):  None,
    ("Camels",        "Production",  "camel_milk",   "milk kg"):  None,
    ("Camels",        "Production",  "camel_meat",   "meat kg"):  None,
    ("Dairy cattle",  "Feed",        "dairy_feed",   "t DM"):     None,
    ("Beef cattle",   "Feed",        "beef_feed",    "t DM"):     None,
    ("Goats",         "Feed",        "goat_feed",    "t DM, 2020-2040"): None,
    ("Sheep",         "Feed",        "sheep_feed",   "t DM, 2020-2041"): None,
    ("Camels",        "Feed",        "camel_feed",   "t DM"):     None,
    ("Poultry (ind)", "Population",  "poultry_ind",  ""):  None,
    ("Poultry (lay)", "Population",  "poultry_lay",  ""):  None,
    ("Poultry (bro)", "Population",  "poultry_bro",  ""):  None,
    ("Pigs",          "Population",  "pig_pop",      ""):  None,
    ("Rabbits",       "Population",  "rabbit_pop",   ""):  None,
    ("Poultry",       "Production",  "poultry_meat", "meat kg"):  None,
    ("Poultry",       "Production",  "poultry_eggs", "trays, 2020-2041"): None,
    ("Pigs",          "Production",  "pig_meat",     "pork kg"):  None,
    ("Rabbits",       "Production",  "rabbit_meat",  "meat kg"):  None,
    ("Apiculture",    "Production",  "api_honey",    "honey kg"): None,
    ("Apiculture",    "Production",  "api_wax",      "wax kg"):   None,
    ("Poultry",       "Feed",        "poultry_feed", "t DM"):     None,
    ("Pigs",          "Feed",        "pig_feed",     "t DM"):     None,
    ("Rabbits",       "Feed",        "rabbit_feed",  "t DM"):     None,
    ("Apiculture",    "Feed",        "api_nectar",   "nectar t"): None,
}

rows = []
for (name, domain, key, note), _ in cagr_data.items():
    series = data[key]
    if "2020-2040" in note:
        c = cagr(series, 2020, 2040)
    elif "2020-2041" in note:
        c = cagr(series, 2020, 2041)
    else:
        c = cagr(series)
    rows.append((name, domain, note if note else "—", f"{c:.2f}\\%" if not np.isnan(c) else "n/a"))

# Print LaTeX rows
print("\n% CAGR TABLE ROWS:")
for r in rows:
    print(f"  {r[0]} & {r[1]} & {r[2]} & {r[3]} \\\\")

print("\nAll charts saved to ")