"""
Crop Knowledge Base — Punjab-specific profiles
Covers Kharif, Rabi, and Zaid seasons for all 3 Punjab soil zones
"""

CROP_PROFILES = {
    # ── KHARIF crops ──────────────────────────────────────────────
    "rice": {
        "name": "Rice",
        "local_name_hi": "चावल",
        "local_name_pa": "ਚੌਲ",
        "season": ["kharif"],
        "soil_types": ["loamy", "clay", "alluvial"],
        "water_req": "high",
        "duration_days": 130,
        "msp_per_quintal": 2300.0,
        "input_cost_per_acre": 15000.0,
        "expected_yield_qtl_per_acre": 28.0,
        "soil_zones": ["majha", "malwa", "doaba"],
        "stubble_friendly": False,          # major stubble burning concern
        "stubble_warning": "Rice stubble burning causes severe air pollution in Punjab. Consider alternatives.",
        "advice": "Transplant in June-July. Use SRI method to save 30% water.",
    },
    "maize": {
        "name": "Maize",
        "local_name_hi": "मक्का",
        "local_name_pa": "ਮੱਕੀ",
        "season": ["kharif"],
        "soil_types": ["loamy", "sandy-loam", "alluvial"],
        "water_req": "medium",
        "duration_days": 95,
        "msp_per_quintal": 2090.0,
        "input_cost_per_acre": 8000.0,
        "expected_yield_qtl_per_acre": 22.0,
        "soil_zones": ["majha", "malwa", "doaba"],
        "stubble_friendly": True,
        "stubble_warning": None,
        "advice": "Excellent rice alternative. Reduces stubble burning. Sow June 1–15.",
    },
    "cotton": {
        "name": "Cotton",
        "local_name_hi": "कपास",
        "local_name_pa": "ਕਪਾਹ",
        "season": ["kharif"],
        "soil_types": ["loamy", "sandy-loam"],
        "water_req": "medium",
        "duration_days": 180,
        "msp_per_quintal": 7020.0,
        "input_cost_per_acre": 20000.0,
        "expected_yield_qtl_per_acre": 8.0,
        "soil_zones": ["malwa"],
        "stubble_friendly": True,
        "stubble_warning": None,
        "advice": "Malwa zone specialty. Monitor pink bollworm from September.",
    },
    "groundnut": {
        "name": "Groundnut",
        "local_name_hi": "मूँगफली",
        "local_name_pa": "ਮੂੰਗਫਲੀ",
        "season": ["kharif"],
        "soil_types": ["sandy-loam"],
        "water_req": "low",
        "duration_days": 110,
        "msp_per_quintal": 6377.0,
        "input_cost_per_acre": 10000.0,
        "expected_yield_qtl_per_acre": 10.0,
        "soil_zones": ["malwa"],
        "stubble_friendly": True,
        "stubble_warning": None,
        "advice": "Best for sandy Malwa soils. Low water requirement suits limited irrigation.",
    },
    "moong": {
        "name": "Moong (Green Gram)",
        "local_name_hi": "मूंग",
        "local_name_pa": "ਮੂੰਗ",
        "season": ["kharif", "zaid"],
        "soil_types": ["loamy", "sandy-loam", "alluvial"],
        "water_req": "low",
        "duration_days": 60,
        "msp_per_quintal": 8558.0,
        "input_cost_per_acre": 5000.0,
        "expected_yield_qtl_per_acre": 5.0,
        "soil_zones": ["majha", "malwa", "doaba"],
        "stubble_friendly": True,
        "stubble_warning": None,
        "advice": "Short-duration legume. Fixes nitrogen, ideal before wheat. Reduces input cost.",
    },

    # ── RABI crops ────────────────────────────────────────────────
    "wheat": {
        "name": "Wheat",
        "local_name_hi": "गेहूं",
        "local_name_pa": "ਕਣਕ",
        "season": ["rabi"],
        "soil_types": ["loamy", "clay", "alluvial", "sandy-loam"],
        "water_req": "medium",
        "duration_days": 150,
        "msp_per_quintal": 2275.0,
        "input_cost_per_acre": 12000.0,
        "expected_yield_qtl_per_acre": 20.0,
        "soil_zones": ["majha", "malwa", "doaba"],
        "stubble_friendly": True,
        "stubble_warning": None,
        "advice": "Sow Nov 1–15. Use HD-3086 or PBW-723 varieties for Punjab conditions.",
    },
    "mustard": {
        "name": "Mustard",
        "local_name_hi": "सरसों",
        "local_name_pa": "ਸਰ੍ਹੋਂ",
        "season": ["rabi"],
        "soil_types": ["sandy-loam", "loamy"],
        "water_req": "low",
        "duration_days": 120,
        "msp_per_quintal": 5650.0,
        "input_cost_per_acre": 6000.0,
        "expected_yield_qtl_per_acre": 7.0,
        "soil_zones": ["malwa", "majha"],
        "stubble_friendly": True,
        "stubble_warning": None,
        "advice": "Low water oilseed crop. Sow Oct 15 – Nov 1. Good for water-scarce areas.",
    },
    "potato": {
        "name": "Potato",
        "local_name_hi": "आलू",
        "local_name_pa": "ਆਲੂ",
        "season": ["rabi"],
        "soil_types": ["loamy", "sandy-loam", "alluvial"],
        "water_req": "medium",
        "duration_days": 90,
        "msp_per_quintal": None,  # market-linked
        "input_cost_per_acre": 50000.0,
        "expected_yield_qtl_per_acre": 100.0,
        "soil_zones": ["doaba", "majha"],
        "stubble_friendly": True,
        "stubble_warning": None,
        "advice": "High value crop. Doaba & Majha zones best. Plant Oct–Nov.",
    },
    "sunflower": {
        "name": "Sunflower",
        "local_name_hi": "सूरजमुखी",
        "local_name_pa": "ਸੂਰਜਮੁਖੀ",
        "season": ["rabi", "zaid"],
        "soil_types": ["loamy", "sandy-loam"],
        "water_req": "low",
        "duration_days": 100,
        "msp_per_quintal": 6760.0,
        "input_cost_per_acre": 7000.0,
        "expected_yield_qtl_per_acre": 6.0,
        "soil_zones": ["majha", "malwa"],
        "stubble_friendly": True,
        "stubble_warning": None,
        "advice": "Drought-tolerant oilseed. Good alternative for water-scarce fields.",
    },

    # ── ZAID / vegetables ─────────────────────────────────────────
    "vegetables_mixed": {
        "name": "Seasonal Vegetables",
        "local_name_hi": "सब्जियां",
        "local_name_pa": "ਸਬਜ਼ੀਆਂ",
        "season": ["kharif", "rabi", "zaid"],
        "soil_types": ["loamy", "sandy-loam", "alluvial"],
        "water_req": "medium",
        "duration_days": 60,
        "msp_per_quintal": None,
        "input_cost_per_acre": 25000.0,
        "expected_yield_qtl_per_acre": 80.0,
        "soil_zones": ["majha", "malwa", "doaba"],
        "stubble_friendly": True,
        "stubble_warning": None,
        "advice": "High-margin option. Best for small landholdings. Tomato, pea, cauliflower recommended.",
    },
}

# Punjab free electricity irrigation windows (tube-well feeder schedule)
ELECTRICITY_SLOTS = {
    "morning": {"start": "05:00", "end": "08:00", "label": "Morning slot"},
    "night": {"start": "22:00", "end": "01:00", "label": "Night slot"},
}

# District to soil zone mapping
DISTRICT_ZONE_MAP = {
    # Majha zone
    "amritsar": "majha", "gurdaspur": "majha", "pathankot": "majha",
    "tarn taran": "majha",
    # Malwa zone
    "ludhiana": "malwa", "bathinda": "malwa", "mansa": "malwa",
    "muktsar": "malwa", "faridkot": "malwa", "ferozepur": "malwa",
    "moga": "malwa", "barnala": "malwa", "sangrur": "malwa",
    "patiala": "malwa", "fatehgarh sahib": "malwa",
    # Doaba zone
    "jalandhar": "doaba", "hoshiarpur": "doaba", "nawanshahr": "doaba",
    "kapurthala": "doaba",
}

# Month-wise crop calendar for Punjab (zone-specific where applicable)
# Each month lists: sow, fertilize, irrigate, harvest, and general_tip
CROP_CALENDAR = {
    1: {  # January
        "month_name": "January",
        "month_name_hi": "जनवरी",
        "month_name_pa": "ਜਨਵਰੀ",
        "season": "rabi",
        "activities": {
            "sow": [],
            "fertilize": [
                "Apply 2nd dose of nitrogen (urea) to wheat at crown-root stage",
                "Top-dress mustard with 20 kg N/acre if not done in December",
            ],
            "irrigate": [
                "1st irrigation to wheat (crown-root stage, 21–25 DAS)",
                "Irrigate potato every 10 days",
            ],
            "harvest": [
                "Early potato varieties (Oct-planted) may be harvested by late January",
            ],
            "pest_watch": [
                "Monitor wheat for yellow rust (Puccinia striiformis) — apply Propiconazole if lesions appear",
                "Check mustard for Painted Bug in early morning",
            ],
            "general_tip": "Frost risk — cover nursery beds. Avoid irrigation before predicted frost nights.",
            "general_tip_pa": "ਪਾਲੇ ਦਾ ਖ਼ਤਰਾ — ਨਰਸਰੀ ਦੀਆਂ ਕਿਆਰੀਆਂ ਢੱਕੋ। ਅਨੁਮਾਨਿਤ ਪਾਲੇ ਵਾਲੀਆਂ ਰਾਤਾਂ ਤੋਂ ਪਹਿਲਾਂ ਸਿੰਚਾਈ ਤੋਂ ਬਚੋ।",
        },
        "zone_notes": {
            "majha": "Amritsar/Gurdaspur: Watch for frost in low-lying fields near rivers.",
            "malwa": "Bathinda/Ludhiana: Apply zinc sulphate (25 kg/acre) to wheat showing interveinal chlorosis.",
            "doaba": "Jalandhar/Hoshiarpur: Potato in full growth — ensure adequate moisture.",
        },
    },
    2: {  # February
        "month_name": "February",
        "month_name_hi": "फ़रवरी",
        "month_name_pa": "ਫ਼ਰਵਰੀ",
        "season": "rabi",
        "activities": {
            "sow": [
                "Sow sunflower (Feb 1–15) for spring Zaid crop",
                "Sow summer moong after Feb 15 in well-drained fields",
            ],
            "fertilize": [
                "3rd dose of nitrogen to wheat at jointing stage (55–60 DAS)",
                "Apply boron spray to mustard at flowering for better pod set",
            ],
            "irrigate": [
                "2nd irrigation to wheat at jointing/tillering stage",
                "Irrigate sunflower nursery bed gently",
            ],
            "harvest": [
                "Main potato harvest (Oct–Nov planted) — dig after foliage yellows",
            ],
            "pest_watch": [
                "Aphid attack on mustard peaks in Feb — spray Dimethoate 0.03%",
                "Check wheat for loose smut — remove affected plants",
            ],
            "general_tip": "Ideal month to test soil before Kharif planning. Collect samples now.",
            "general_tip_pa": "ਖਰੀਫ਼ ਯੋਜਨਾਬੰਦੀ ਤੋਂ ਪਹਿਲਾਂ ਮਿੱਟੀ ਪਰਖਣ ਦਾ ਆਦਰਸ਼ ਮਹੀਨਾ। ਹੁਣੇ ਨਮੂਨੇ ਇਕੱਠੇ ਕਰੋ।",
        },
        "zone_notes": {
            "majha": "Spring onion and garlic transplanting continues.",
            "malwa": "Cotton land preparation can start — deep ploughing recommended.",
            "doaba": "Potato storage: grade tubers for seed purposes before market arrival.",
        },
    },
    3: {  # March
        "month_name": "March",
        "month_name_hi": "मार्च",
        "month_name_pa": "ਮਾਰਚ",
        "season": "rabi_end",
        "activities": {
            "sow": [
                "Sow summer moong (March 1–15) for Zaid season",
                "Sunflower sowing window closes March 10",
            ],
            "fertilize": [
                "Last foliar spray (micronutrients) to wheat if needed",
                "Top-dress sunflower with 20 kg N/acre at 30 DAS",
            ],
            "irrigate": [
                "3rd/4th irrigation to wheat at booting and heading stages",
                "Critical irrigation for sunflower at flowering",
            ],
            "harvest": [
                "Mustard harvest when pods turn golden-yellow (avoid shattering)",
                "Late-sown potato harvest completes",
            ],
            "pest_watch": [
                "Wheat: Karnal bunt risk — do not irrigate at night during heading",
                "Aphid on wheat — economic threshold: 10 aphids/ear",
            ],
            "general_tip": "Start field preparation for Kharif. Incorporate last Rabi stubble properly.",
            "general_tip_pa": "ਖਰੀਫ਼ ਲਈ ਖੇਤ ਤਿਆਰੀ ਸ਼ੁਰੂ ਕਰੋ। ਆਖਰੀ ਰਬੀ ਦੀ ਬਾਕੀ ਫ਼ਸਲ ਸਹੀ ਤਰ੍ਹਾਂ ਸ਼ਾਮਲ ਕਰੋ।",
        },
        "zone_notes": {
            "majha": "Begin field levelling for paddy nursery preparation.",
            "malwa": "Cotton seed treatment: Imidacloprid 600FS before sowing.",
            "doaba": "Vegetable sowing: Bitter gourd, bottle gourd nursery preparation.",
        },
    },
    4: {  # April
        "month_name": "April",
        "month_name_hi": "अप्रैल",
        "month_name_pa": "ਅਪ੍ਰੈਲ",
        "season": "zaid",
        "activities": {
            "sow": [
                "Sow vegetables (bitter gourd, bottle gourd, okra) in well-irrigated fields",
                "Green manure crops (sesbania) for soil health improvement",
            ],
            "fertilize": [
                "Apply basal fertilizer to summer vegetables: NPK 10:26:26 @1 bag/acre",
                "Top-dress moong with phosphate fertilizer",
            ],
            "irrigate": [
                "Last irrigation to wheat 2–3 weeks before harvest (if dry)",
                "Frequent irrigation for vegetables in rising heat",
            ],
            "harvest": [
                "Wheat harvest: April 20 – May 10 (combine harvester recommended)",
                "Mustard threshing and storage",
            ],
            "pest_watch": [
                "Wheat: Stem sawfly and aphid in warm spells",
                "Vegetable: Red pumpkin beetle on cucurbits — dust Carbaryl",
            ],
            "general_tip": "Do NOT burn wheat stubble! Punjab ₹2500/acre incentive for Happy Seeder use.",
            "general_tip_pa": "ਕਣਕ ਦੀ ਪਰਾਲੀ ਨਾ ਸਾੜੋ! Happy Seeder ਦੀ ਵਰਤੋਂ ਲਈ ਪੰਜਾਬ ਸਰਕਾਰ ₹2500/ਏਕੜ ਦਿੰਦੀ ਹੈ।",
        },
        "zone_notes": {
            "majha": "Paddy nursery bed preparation begins end of April.",
            "malwa": "Cotton sowing can begin April 25 onwards in south Malwa (Bathinda, Muktsar).",
            "doaba": "Vegetable cultivation peak — market demand for summer vegetables high.",
        },
    },
    5: {  # May
        "month_name": "May",
        "month_name_hi": "मई",
        "month_name_pa": "ਮਈ",
        "season": "kharif_prep",
        "activities": {
            "sow": [
                "Raise paddy nursery (May 15–June 15) for June transplanting",
                "Cotton sowing (Bt hybrid): May 1–June 15 in Malwa zone",
                "Maize sowing: May 15 onwards",
            ],
            "fertilize": [
                "Apply FYM / compost (10–12 tonnes/acre) before paddy field preparation",
                "Cotton basal dose: DAP 50 kg + MOP 25 kg/acre at sowing",
            ],
            "irrigate": [
                "Pre-sowing irrigation (palewa) for paddy fields",
                "Frequent irrigation for vegetable crops",
            ],
            "harvest": [
                "Wheat harvest completes by May 10–15",
                "Summer moong harvest: late May to June",
            ],
            "pest_watch": [
                "Paddy nursery: Yellow stem borer — treat nursery bed with Carbofuran",
                "Cotton: Thrips in seedling stage",
            ],
            "general_tip": "Best time to use Happy Seeder on wheat stubble before paddy transplanting.",
            "general_tip_pa": "ਚਾਵਲ ਲਾਉਣ ਤੋਂ ਪਹਿਲਾਂ ਕਣਕ ਦੀ ਬਾਕੀ ਫ਼ਸਲ 'ਤੇ Happy Seeder ਵਰਤਣ ਦਾ ਸਭ ਤੋਂ ਵਧੀਆ ਸਮਾਂ।",
        },
        "zone_notes": {
            "majha": "Paddy transplanting target: June 10–20 — do not delay beyond June 20.",
            "malwa": "Malwa cotton zone: Prefer Bt hybrids with 160+ days duration.",
            "doaba": "Hoshiarpur hills: Maize preferred over paddy — less water required.",
        },
    },
    6: {  # June
        "month_name": "June",
        "month_name_hi": "जून",
        "month_name_pa": "ਜੂਨ",
        "season": "kharif",
        "activities": {
            "sow": [
                "Paddy transplanting: June 10–20 (mandatory Punjab window)",
                "Maize sowing: June 1–15",
                "Arhar (Pigeon pea): June 1–15 in Doaba zone",
            ],
            "fertilize": [
                "Paddy basal: DAP 75 kg/acre + Zinc Sulphate 25 kg/acre",
                "Maize basal: Urea 50 kg + DAP 50 kg/acre",
            ],
            "irrigate": [
                "Paddy: Maintain 5 cm standing water after transplanting",
                "Maize: Avoid waterlogging — ensure field drainage",
            ],
            "harvest": [
                "Early summer vegetables (cucumber, beans)",
            ],
            "pest_watch": [
                "Paddy: Leaf folder and stem borer — Cartap Hydrochloride 4G @8 kg/acre",
                "Maize: Fall Armyworm (FAW) — apply Emamectin Benzoate",
            ],
            "general_tip": "Punjab tube-well free electricity: 5 AM–8 AM & 10 PM–1 AM. Plan paddy irrigation accordingly.",
            "general_tip_pa": "ਪੰਜਾਬ ਟਿਊਬਵੈੱਲ ਮੁਫ਼ਤ ਬਿਜਲੀ: ਸਵੇਰੇ 5–8 ਅਤੇ ਰਾਤ 10–1 ਵਜੇ। ਚਾਵਲ ਦੀ ਸਿੰਚਾਈ ਉਸੇ ਅਨੁਸਾਰ ਕਰੋ।",
        },
        "zone_notes": {
            "majha": "Avoid paddy transplanting before June 10 — groundwater table conservation.",
            "malwa": "Cotton: Thinning and gap filling after 15 DAS.",
            "doaba": "Maize intercropping with cowpea increases income from same field.",
        },
    },
    7: {  # July
        "month_name": "July",
        "month_name_hi": "जुलाई",
        "month_name_pa": "ਜੁਲਾਈ",
        "season": "kharif",
        "activities": {
            "sow": [
                "Late paddy transplanting (if delayed): complete by July 10",
                "Sow moong as intercrop in maize fields",
            ],
            "fertilize": [
                "Paddy 1st topdress: Urea 35 kg/acre at 21 DAS (active tillering)",
                "Cotton 1st topdress: Urea 25 kg/acre after 1 month",
                "Maize 1st topdress: Urea 50 kg/acre at knee-high stage",
            ],
            "irrigate": [
                "Paddy: Maintain continuous flooded conditions during monsoon",
                "Cotton: Ensure furrow drainage after heavy rain",
            ],
            "harvest": [],
            "pest_watch": [
                "Paddy: Brown plant hopper (BPH) — do not spray synthetic pyrethroids",
                "Cotton: Bollworm monitoring — install pheromone traps",
                "Maize: Fall armyworm — apply neem-based spray at early infestation",
            ],
            "general_tip": "Monsoon rains reduce irrigation cost. Track rainfall to avoid over-irrigation.",
            "general_tip_pa": "ਮੌਨਸੂਨ ਦੀ ਬਾਰਿਸ਼ ਸਿੰਚਾਈ ਖ਼ਰਚ ਘਟਾਉਂਦੀ ਹੈ। ਜ਼ਿਆਦਾ ਸਿੰਚਾਈ ਤੋਂ ਬਚਣ ਲਈ ਬਾਰਿਸ਼ ਦਾ ਹਿਸਾਬ ਰੱਖੋ।",
        },
        "zone_notes": {
            "majha": "Heavy monsoon — check field bunds to prevent flooding.",
            "malwa": "Pink bollworm first generation peaks — use Bt cotton effectively.",
            "doaba": "Maize silking stage — critical water requirement period.",
        },
    },
    8: {  # August
        "month_name": "August",
        "month_name_hi": "अगस्त",
        "month_name_pa": "ਅਗਸਤ",
        "season": "kharif",
        "activities": {
            "sow": [
                "Prepare nursery for vegetable crops (cauliflower, cabbage, tomato) for Oct–Nov",
            ],
            "fertilize": [
                "Paddy 2nd topdress: Urea 35 kg/acre at panicle initiation (45–50 DAS)",
                "Cotton 2nd topdress: Urea 25 kg/acre",
            ],
            "irrigate": [
                "Paddy: Alternate wetting-drying (AWD) saves 20–30% water without yield loss",
                "Maize: Post-monsoon supplemental irrigation if dry spell",
            ],
            "harvest": [
                "Early maize varieties (80-day): harvest from Aug 20 onwards",
                "Moong intercrop harvest",
            ],
            "pest_watch": [
                "Paddy: Neck blast (Pyricularia oryzae) — spray Tricyclazole 75 WP",
                "Cotton: Mealy bug colonies — apply Profenofos 50 EC",
            ],
            "general_tip": "Apply bio-decomposer spray on standing paddy straw to prepare for wheat (alternative to burning).",
            "general_tip_pa": "ਕਣਕ ਦੀ ਤਿਆਰੀ ਲਈ ਖੜੀ ਪਰਾਲੀ 'ਤੇ ਬਾਇਓ-ਡੀਕੰਪੋਜ਼ਰ ਸਪਰੇਅ ਕਰੋ (ਸਾੜਨ ਦਾ ਵਿਕਲਪ)।",
        },
        "zone_notes": {
            "majha": "Late paddy: Basmati types at tillering — reduce water for aroma enhancement.",
            "malwa": "Cotton boll formation — critical period, avoid water stress.",
            "doaba": "Vegetable nursery preparation: Cabbage, cauliflower, broccoli.",
        },
    },
    9: {  # September
        "month_name": "September",
        "month_name_hi": "सितंबर",
        "month_name_pa": "ਸਤੰਬਰ",
        "season": "kharif",
        "activities": {
            "sow": [
                "Transplant cauliflower and cabbage nursery (raised in Aug)",
                "Sow toria (turnip rape) in early Rabi fields",
            ],
            "fertilize": [
                "Final topdress for late paddy if needed",
                "Vegetable transplants: Starter dose NPK 12:32:16 @10 kg/acre",
            ],
            "irrigate": [
                "Paddy: Drain field 10–14 days before expected harvest",
                "Cotton: Irrigation every 15 days if dry",
            ],
            "harvest": [
                "Early paddy varieties (125-day): harvest from Sept 20 onwards",
                "Maize main crop harvest",
                "Groundnut harvest in Malwa",
            ],
            "pest_watch": [
                "Cotton: Pink bollworm 2nd generation — pheromone trap monitoring",
                "Paddy: Sheath blight near harvest — reduce canopy humidity",
            ],
            "general_tip": "Arrange combine harvester booking in advance — peak demand in October.",
            "general_tip_pa": "ਅਕਤੂਬਰ ਵਿੱਚ ਸਿਖਰ ਮੰਗ ਹੋਣ ਕਾਰਨ ਕੰਬਾਈਨ ਹਾਰਵੈਸਟਰ ਪਹਿਲਾਂ ਹੀ ਬੁੱਕ ਕਰੋ।",
        },
        "zone_notes": {
            "majha": "PR-126 and early paddy varieties harvested — prepare wheat land.",
            "malwa": "Cotton picking season begins — first picking gives highest quality.",
            "doaba": "Potato seed procurement and cold storage check for Oct planting.",
        },
    },
    10: {  # October
        "month_name": "October",
        "month_name_hi": "अक्टूबर",
        "month_name_pa": "ਅਕਤੂਬਰ",
        "season": "rabi_prep",
        "activities": {
            "sow": [
                "Potato planting: Oct 1–31 (Doaba and Majha zones)",
                "Mustard sowing: Oct 15 – Nov 1",
                "Toria: Oct 1–15",
            ],
            "fertilize": [
                "Potato basal: DAP 100 kg + MOP 50 kg/acre at planting",
                "Mustard basal: 25 kg DAP/acre",
            ],
            "irrigate": [
                "First irrigation to potato 15 days after planting",
                "Pre-sowing moisture check for wheat fields",
            ],
            "harvest": [
                "Main paddy harvest (PR-121, PR-122 varieties): Oct 1–31",
                "Cotton 2nd picking",
            ],
            "pest_watch": [
                "Paddy: Store-grain pests — dry paddy to <14% moisture before storage",
                "Potato: Late blight risk in Doaba hills — apply Mancozeb preventively",
            ],
            "general_tip": "⚠️ CRITICAL: Do not burn paddy stubble. Use Happy Seeder or bio-decomposer for wheat sowing.",
            "general_tip_pa": "⚠️ ਮਹੱਤਵਪੂਰਨ: ਚਾਵਲ ਦੀ ਪਰਾਲੀ ਨਾ ਸਾੜੋ। ਕਣਕ ਦੀ ਬਿਜਾਈ ਲਈ Happy Seeder ਜਾਂ ਬਾਇਓ-ਡੀਕੰਪੋਜ਼ਰ ਵਰਤੋ।",
        },
        "zone_notes": {
            "majha": "Paddy harvest — stagger threshing to ease transport to mandi.",
            "malwa": "Happy Seeder availability limited — book cooperative seeder NOW.",
            "doaba": "Potato planting peak month — ensure seed is virus-free certified.",
        },
    },
    11: {  # November
        "month_name": "November",
        "month_name_hi": "नवंबर",
        "month_name_pa": "ਨਵੰਬਰ",
        "season": "rabi",
        "activities": {
            "sow": [
                "Wheat sowing: Nov 1–15 (optimal window — do not delay beyond Nov 25)",
                "Use Happy Seeder for direct sowing into paddy stubble",
                "Sunflower for late Rabi: Nov 1–15",
            ],
            "fertilize": [
                "Wheat basal: DAP 55 kg + Urea 45 kg/acre at sowing",
                "Apply Zinc Sulphate 25 kg/acre if Malwa zone soil deficient",
            ],
            "irrigate": [
                "Pre-sowing palewa irrigation for wheat if moisture low",
                "1st irrigation to potato (hilling stage)",
            ],
            "harvest": [
                "Late paddy varieties (Basmati) harvest: Nov 1–20",
                "Cotton final picking",
            ],
            "pest_watch": [
                "Wheat: Seed treatment with Vitavax Power 75 WP before sowing",
                "Mustard: White rust (Albugo candida) — avoid excessive irrigation",
            ],
            "general_tip": "Timely wheat sowing in November gives 15–20% higher yield than December sowing.",
            "general_tip_pa": "ਨਵੰਬਰ ਵਿੱਚ ਸਮੇਂ ਸਿਰ ਕਣਕ ਬੀਜਣ ਨਾਲ ਦਸੰਬਰ ਬਿਜਾਈ ਨਾਲੋਂ 15–20% ਵੱਧ ਝਾੜ ਮਿਲਦਾ ਹੈ।",
        },
        "zone_notes": {
            "majha": "PBW-752, HD-3086 wheat varieties recommended for Amritsar, Gurdaspur.",
            "malwa": "DBW-303 or PBW-723 for Ludhiana, Bathinda — zinc supplement critical.",
            "doaba": "Wheat sowing after potato harvest may be delayed to late November.",
        },
    },
    12: {  # December
        "month_name": "December",
        "month_name_hi": "दिसंबर",
        "month_name_pa": "ਦਸੰਬਰ",
        "season": "rabi",
        "activities": {
            "sow": [
                "Late wheat sowing (if delayed) — use short-duration varieties (WH-1105)",
                "Rabi vegetables: Pea, spinach, fenugreek in kitchen gardens",
            ],
            "fertilize": [
                "1st top-dress urea (35 kg/acre) to wheat at 21 DAS (crown-root stage)",
                "Mustard topdress if not applied at sowing",
            ],
            "irrigate": [
                "1st critical irrigation to wheat: 20–25 DAS (crown-root initiation)",
                "Potato: Continue 10-day interval irrigation cycle",
            ],
            "harvest": [
                "Toria (turnip rape) harvest: Dec 25 onwards",
            ],
            "pest_watch": [
                "Wheat: Check for termite damage in light-textured soils (Malwa)",
                "Potato: Apply Chlorothalonil for early blight if wet conditions",
            ],
            "general_tip": "Cold nights protect wheat from early aphid attack. Monitor crop colour for nutrient deficiency.",
            "general_tip_pa": "ਠੰਡੀਆਂ ਰਾਤਾਂ ਕਣਕ ਨੂੰ ਮੁੱਢਲੇ ਮਾਹੂ ਹਮਲੇ ਤੋਂ ਬਚਾਉਂਦੀਆਂ ਹਨ। ਪੋਸ਼ਣ ਕਮੀ ਲਈ ਫ਼ਸਲ ਰੰਗ ਦੇਖੋ।",
        },
        "zone_notes": {
            "majha": "Fog season — foliar diseases risk up. Ensure good ventilation in fields.",
            "malwa": "Malwa sandy soils: Irrigate wheat more frequently (every 18–20 days).",
            "doaba": "Potato in tuber bulking stage — most critical irrigation window.",
        },
    },
}
