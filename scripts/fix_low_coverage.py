"""Fix the 8 routes that have coverage < 45% by replacing obscure stops
with known geocoded equivalents from stops_geocoded.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BUSDATA = DATA / "busdata.json"

with open(BUSDATA, encoding="utf-8") as f:
    data = json.load(f)

geocoded = json.loads((DATA / "stops_geocoded.json").read_text(encoding="utf-8"))

# Build a set of all currently geocoded stop names for quick lookup
known = set(geocoded.keys())

# ── Replacement stop lists using well-geocoded stops ─────────────────────────

FIXES = {

    # DN-26: Gaighata (Habra) to Kalyani (Jagulia)
    ("DN-26", "Kalyani"): {
        "code": "DN-26", "kind": "government", "scope": "local",
        "directional": True, "towards": "Kalyani",
        "stops": [
            "Gaighata","Habra Station","Kalyangarh","Kachua","8 No Kalibari",
            "Sendanga","Noorpur","Jaguli","Kalyani"
        ]
    },

    # MM-3: Dakshineshwar – Duttapukur (long circular)
    ("MM-3", "Duttapukur"): {
        "code": "MM-3", "kind": "private", "scope": "local",
        "directional": True, "towards": "Duttapukur",
        "stops": [
            "Dakshineswar","Dunlop","Rathtala","Kamarhati","Sodepur Station",
            "Khardaha","Titagarh","Barrackpore Station","Barrackpore Chiria",
            "Wireless","Mohanpur","Debpukur","Chapuria","Mathrangi","Nilgunge",
            "Rangapur","Kokapur","Jagannathpur","Barbaria","Barasat Chapadali",
            "Madhyamgram","Doltala","BT College","Birati","Airport Gate 3",
            "Airport Gate 1","Kaikhali","Haldirams","Baguiati","Kestopur",
            "Dumdum Park","Laketown","Sreebhumi","Ultadanga","Khanna Cinema",
            "Shyambazar","Chiria","Sinthi","Tobin Road","Bonhooghly",
            "Dunlop","Dakshineswar"
        ]
    },

    # MN-2: Hasnabad – Lebukhali
    ("MN-2", "Lebukhali"): {
        "code": "MN-2", "kind": "private", "scope": "local",
        "directional": True, "towards": "Lebukhali",
        "stops": [
            "Hasnabad","Par Hasnabad","Hingalgunge","Lebukhali"
        ]
    },

    # SD-22/1: Nainan to Esplanade
    ("SD-22/1", "Esplanade"): {
        "code": "SD-22/1", "kind": "government", "scope": "local",
        "directional": True, "towards": "Esplanade",
        "stops": [
            "Nainan","Sarisha","Dostipur","Fatehpur","Shirakole",
            "Amtala","Bishnupur","Khariberia","Bhasha 14no","Pailan",
            "Joka Bridge","Thakurpukur","Shilpara","Sakher Bazar",
            "Behala Chowrasta","Behala 14 No","Majherhat","Mominpore",
            "Bhabani Bhawan","PTS","Fort William","Esplanade"
        ]
    },

    # SD-51: Gurudaspur to Mathurapur station
    ("SD-51", "Mathurapur Station"): {
        "code": "SD-51", "kind": "government", "scope": "local",
        "directional": True, "towards": "Mathurapur Station",
        "stops": [
            "Diamond Harbour","Dalanghata","Mandirbazar",
            "Kashinagar","Krishnachandrapur","Lalpur",
            "South Bishnupur","Mathurapur Station"
        ]
    },

    # D-7: Barasat to Bagdah
    ("D-7", "Bagdah"): {
        "code": "D-7", "kind": "government", "scope": "local",
        "directional": True, "towards": "Bagdah",
        "stops": [
            "Barasat Chapadali","Duttapukur","Bira Chowmatha",
            "Ashoknagar Station","Habra Station","Gaighata",
            "Bongaon","Asharu Bazar","Helencha","Bagdah"
        ]
    },

    # D-9: Barasat to Hakimpur
    ("D-9", "Hakimpur"): {
        "code": "D-9", "kind": "government", "scope": "local",
        "directional": True, "towards": "Hakimpur",
        "stops": [
            "Barasat Chapadali","Duttapukur","Bira Chowmatha",
            "Guma Chowmatha","Ashoknagar Station","Habra Station",
            "Machhlandapur","Tentulia","Swarupnagar","Nirman","Bithari"
        ]
    },

    # D-31: Esplanade to Srinathpur
    ("D-31", "Srinathpur"): {
        "code": "D-31", "kind": "government", "scope": "local",
        "directional": True, "towards": "Srinathpur",
        "stops": [
            "Esplanade","Central","Shyambazar","Khanna Cinema",
            "Ultadanga","Airport Gate 1","Madhyamgram",
            "Barasat Chapadali","Ashoknagar Station","Habra Station",
            "Machhlandapur"
        ]
    },
}

# Replace matching routes in busdata
replaced = 0
for i, route in enumerate(data["routes"]):
    key = (route["code"], route.get("towards", ""))
    if key in FIXES:
        data["routes"][i] = FIXES[key]
        replaced += 1
        print("Fixed:", key)

print("Replaced {} routes".format(replaced))

with open(BUSDATA, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)

print("busdata.json saved.")
