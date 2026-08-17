"""Geocode Kolkata bus stops using OSM data, existing coords, and Nominatim."""
from __future__ import annotations

import json
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BUSDATA = DATA / "busdata.json"
OSM_STOPS = DATA / "osm_bus_stops.json"
GEOCODE_CACHE = DATA / "geocode_cache.json"
STOPS_OUT = DATA / "stops_geocoded.json"

HUB = {
    # ── Core city terminals & hubs ──────────────────────────────────────────
    "Esplanade": [22.5645, 88.3510],
    "Howrah Station": [22.5838, 88.3426],
    "Sealdah": [22.5675, 88.3700],
    "BBD Bag": [22.5697, 88.3486],
    "Barabazar": [22.5760, 88.3530],
    "Shyambazar": [22.5990, 88.3740],
    "Hatibagan": [22.5945, 88.3720],
    "Girish Park": [22.5870, 88.3620],
    "MG Road": [22.5820, 88.3570],
    "Maniktala": [22.5860, 88.3870],
    "Ultadanga": [22.5910, 88.3990],
    "Kankurgachi": [22.5800, 88.3960],
    "Phoolbagan": [22.5760, 88.3920],
    "Beleghata": [22.5640, 88.4060],
    "Park Circus": [22.5390, 88.3670],
    "Moulali": [22.5610, 88.3680],
    "Rabindra Sadan": [22.5440, 88.3470],
    "Maidan": [22.5530, 88.3460],
    "Park Street": [22.5530, 88.3520],
    "Exide": [22.5430, 88.3520],
    "Hazra More": [22.5260, 88.3450],
    "Kalighat": [22.5180, 88.3430],
    "Rashbehari": [22.5140, 88.3530],
    "Gariahat": [22.5170, 88.3660],
    "Golpark": [22.5130, 88.3650],
    "Dhakuria": [22.5040, 88.3680],
    "Jodhpur Park": [22.5055, 88.3635],
    "Jadavpur 8B": [22.4970, 88.3710],
    "Jadavpur PS": [22.4960, 88.3690],
    "Tollygunge": [22.5010, 88.3460],
    "Tollygunge Phari": [22.5020, 88.3500],
    "Tollygunge Metro": [22.4988, 88.3473],
    "South City": [22.5017, 88.3617],
    "Lords": [22.5020, 88.3564],
    "Lake Gardens": [22.5053, 88.3548],
    "Anwar Shah Road": [22.5020, 88.3495],
    "Prince Anwar Shah Connector": [22.5018, 88.3520],
    "Rabindra Sarovar": [22.5070, 88.3530],
    # ── South Kolkata ────────────────────────────────────────────────────────
    "Behala Chowrasta": [22.4980, 88.3110],
    "Behala 14 No": [22.5060, 88.3170],
    "Taratala": [22.5160, 88.3120],
    "Majherhat": [22.5230, 88.3210],
    "Mominpore": [22.5310, 88.3270],
    "Ekbalpur": [22.5350, 88.3280],
    "Kidderpore": [22.5380, 88.3320],
    "Hastings": [22.5470, 88.3340],
    "New Alipore": [22.5040, 88.3320],
    "Alipore Zoo": [22.5360, 88.3320],
    "Chetla": [22.5170, 88.3370],
    "Garia Metro": [22.4680, 88.3970],
    "Garia Station": [22.4640, 88.3940],
    "Naktala": [22.4760, 88.3760],
    "Bansdroni": [22.4800, 88.3650],
    "Baghajatin": [22.4790, 88.3870],
    "Patuli": [22.4720, 88.3940],
    "Mukundapur": [22.4980, 88.3990],
    "Ruby": [22.5130, 88.4010],
    "Ruby Hospital": [22.5130, 88.4010],
    "Anandapur": [22.5090, 88.4030],
    "Thakurpukur": [22.4670, 88.3050],
    "Joka Bridge": [22.4700, 88.3060],
    "Santoshpur": [22.4870, 88.3780],
    "Kasba": [22.5160, 88.3870],
    "Kasba PS": [22.5155, 88.3862],
    "Kasba Post Office": [22.5160, 88.3870],
    "Ballygunge Station": [22.5290, 88.3650],
    "Ballygunge": [22.5290, 88.3650],
    "Ballygunge Phari": [22.5275, 88.3638],
    "Deshapriya Park": [22.5220, 88.3560],
    "Hazra": [22.5260, 88.3450],
    "Bhowanipore": [22.5300, 88.3450],
    "Bhawani Bhawan": [22.5335, 88.3395],
    "Bhabani Bhawan": [22.5335, 88.3395],
    "Alipore Court": [22.5310, 88.3370],
    "Chetla Park": [22.5170, 88.3370],
    "Kudghat": [22.5012, 88.3468],
    "Netaji Nagar": [22.4880, 88.3520],
    "Ranikuthi": [22.4910, 88.3500],
    "Malancha Cinema": [22.4950, 88.3480],
    "Haridevpur": [22.4870, 88.3540],
    "Keorapukur": [22.4840, 88.3560],
    "Kabardanga": [22.4820, 88.3580],
    "Barisha": [22.4890, 88.3090],
    "Shilpara": [22.4830, 88.3120],
    "Sakher Bazar": [22.4950, 88.3090],
    # ── East Kolkata ─────────────────────────────────────────────────────────
    "Science City": [22.5400, 88.3950],
    "Chingrighata": [22.5780, 88.4150],
    "Saltlake Stadium": [22.5700, 88.4050],
    "Karunamoyee": [22.5780, 88.4170],
    "Sector V": [22.5760, 88.4320],
    "College More": [22.5770, 88.4290],
    "Newtown": [22.5810, 88.4640],
    "Rajarhat Chowmatha": [22.5978, 88.4670],
    "Nicco Park": [22.5720, 88.4200],
    "Nicco Park More": [22.5720, 88.4200],
    "Chinar Park": [22.6230, 88.4480],
    "City Centre 2": [22.6180, 88.4480],
    "City Center 2": [22.6180, 88.4480],
    "Baguiati": [22.6130, 88.4310],
    "Kestopur": [22.6010, 88.4280],
    "Dumdum Park": [22.6090, 88.4140],
    "Haldirams": [22.6010, 88.4280],
    "Teghoria": [22.6190, 88.4330],
    "VIP Bazar": [22.5900, 88.4180],
    "Acropolis Mall": [22.5247, 88.3928],
    "Bosepukur": [22.5180, 88.3910],
    "Quest Mall": [22.5275, 88.3638],
    "Bondel Gate": [22.5445, 88.3870],
    "Park Circus 5 Point": [22.5390, 88.3670],
    "Topsia": [22.5540, 88.3900],
    "Kustia": [22.5500, 88.3880],
    "4 No Bridge": [22.5490, 88.3870],
    "EM Bypass": [22.5100, 88.4000],
    # ── North Kolkata ─────────────────────────────────────────────────────────
    "Airport Gate 1": [22.6470, 88.4410],
    "Kaikhali": [22.6320, 88.4370],
    "Dumdum": [22.6420, 88.4310],
    "Nager Bazar": [22.6300, 88.4200],
    "Lake Town": [22.6080, 88.4080],
    "Laketown": [22.6080, 88.4080],
    "Sreebhumi": [22.6050, 88.4080],
    "Belgachia": [22.6010, 88.3850],
    "RG Kar": [22.6060, 88.3770],
    "Sinthi": [22.6230, 88.3870],
    "Chiria": [22.6290, 88.3750],
    "Dunlop": [22.6440, 88.3760],
    "Dakshineswar": [22.6550, 88.3570],
    "Bonhooghly": [22.6360, 88.3820],
    "Kamarhati": [22.6720, 88.3760],
    "Sodepur": [22.7000, 88.3870],
    "Barasat": [22.7240, 88.4810],
    "Madhyamgram": [22.6970, 88.4500],
    "Patipukur": [22.6150, 88.3960],
    "Kalindi": [22.6100, 88.3960],
    "Bangur Avenue": [22.6160, 88.4020],
    "Diamond Plaza": [22.6210, 88.4160],
    "Central Jail": [22.6480, 88.4260],
    "Airport Gate 3": [22.6440, 88.4380],
    "Birati": [22.6670, 88.4360],
    "Michaelnagar": [22.6790, 88.4450],
    "BT College": [22.6820, 88.4420],
    "Doltala": [22.6850, 88.4430],
    "Bagbazar": [22.6010, 88.3650],
    "Cossipore": [22.6150, 88.3680],
    "Rajabazar": [22.5790, 88.3760],
    "Khanna Cinema": [22.5950, 88.3830],
    "Rajballavpara": [22.6010, 88.3670],
    "Hatibagan": [22.5945, 88.3720],
    # ── Central Kolkata ───────────────────────────────────────────────────────
    "Central": [22.5730, 88.3540],
    "Chandni Chowk": [22.5670, 88.3520],
    "College Street": [22.5750, 88.3640],
    "Wellington": [22.5630, 88.3590],
    "Babu Ghat": [22.5640, 88.3400],
    "Eden Garden": [22.5648, 88.3430],
    "Fort William": [22.5540, 88.3410],
    "Sovabazar": [22.5980, 88.3670],
    "Princep Ghat": [22.5610, 88.3360],
    "Prinsep Ghat": [22.5610, 88.3360],
    "BBD Bag": [22.5697, 88.3486],
    "Podder Court": [22.5710, 88.3520],
    "Bowbazar": [22.5710, 88.3600],
    "Medical College": [22.5740, 88.3640],
    "Lalbazar": [22.5710, 88.3520],
    "High Court": [22.5680, 88.3450],
    "Lansdowne": [22.5250, 88.3500],
    "Sishu Mangal": [22.5240, 88.3480],
    "Minto Park": [22.5360, 88.3490],
    "Beck Bagan": [22.5380, 88.3560],
    "Mallick Bazar": [22.5430, 88.3620],
    "Amherst Street": [22.5780, 88.3640],
    "Vivekananda Road": [22.5840, 88.3630],
    "Hedua": [22.5890, 88.3660],
    "Hind Cinema": [22.5650, 88.3560],
    "Bank Of India": [22.5730, 88.3610],
    # ── Howrah ────────────────────────────────────────────────────────────────
    "Howrah Maidan": [22.5890, 88.3340],
    "Santragachi": [22.5850, 88.2870],
    "Vidyasagar Setu": [22.5700, 88.3300],
    "Shibpur Bazar": [22.5800, 88.3270],
    "Mallick Fatak": [22.5840, 88.3290],
    "Kazipara": [22.5810, 88.3250],
    "Bataitala Phari": [22.5775, 88.3210],
    "Avani Mall": [22.5810, 88.3250],
    "Belurmath": [22.6370, 88.3530],
    "Liluah": [22.6180, 88.3240],
    "Bally Bazar": [22.6260, 88.3210],
    "Ballykhal": [22.6200, 88.3200],
    "Ballyhalt": [22.6230, 88.3070],
    "Dankuni": [22.6800, 88.2930],
    "Domjur": [22.6350, 88.2650],
    "Kona": [22.5920, 88.2920],
    "Tikiapara Bypass": [22.5980, 88.3180],
    "Dasnagar": [22.5980, 88.3060],
    "Shanpur": [22.5950, 88.3020],
    "Ichapur": [22.5915, 88.3015],
    "Kadamtala": [22.5860, 88.3150],
    "Panchanantala": [22.5860, 88.3280],
    "Power House": [22.5850, 88.3200],
    "Kamardanga": [22.5870, 88.3080],
    "Golabarai PS": [22.5870, 88.3330],
    "Bandha Ghat": [22.5890, 88.3280],
    "Malipanchghara": [22.6100, 88.3260],
    "Garden Reach": [22.5480, 88.3100],
    "Ramnagar": [22.5430, 88.3090],
    "Babubazar": [22.5450, 88.3120],
    "Kidderpore Dock": [22.5340, 88.3240],
    "Metiabruz": [22.5310, 88.3010],
    # ── Far North ─────────────────────────────────────────────────────────────
    "Belgharia": [22.6580, 88.3890],
    "Barrackpore": [22.7600, 88.3700],
    "Barrackpore Court": [22.7640, 88.3720],
    "Barrackpore Station": [22.7580, 88.3680],
    "New Barrackpore": [22.6880, 88.4120],
    "Panihati": [22.6940, 88.3740],
    "Khardaha": [22.7200, 88.3780],
    "Titagarh": [22.7380, 88.3730],
    "Naihati": [22.8940, 88.4210],
    "Naihati Station": [22.8940, 88.4210],
    "Kalyani": [22.9750, 88.4340],
    "Chandannagar": [22.8630, 88.3670],
    "Serampore": [22.7540, 88.3420],
    "Sodepur Station": [22.7000, 88.3870],
    "Kamarhati Rathtala": [22.6720, 88.3750],
    "Rathtala": [22.6680, 88.3740],
    "Bhatpara": [22.8690, 88.4080],
    "Kankinara": [22.8500, 88.4010],
    "Kanchrapara": [22.9450, 88.4330],
    # ── Outer West Bengal ─────────────────────────────────────────────────────
    "Uluberia": [22.4730, 88.1040],
    "Bagnan": [22.4620, 87.9570],
    "Amta": [22.5980, 87.9890],
    "Panchla": [22.5740, 88.1450],
    "Dhulagarh": [22.5790, 88.2000],
    "Sankrail": [22.5850, 88.2350],
    "Barrackpore": [22.7600, 88.3700],
    "Digha": [21.6266, 87.5074],
    "New Digha": [21.6234, 87.4950],
    "Old Digha": [21.6270, 87.5110],
    "Nabadwip": [23.4075, 88.3662],
    "Benachity": [23.5510, 87.2910],
    "Kalna": [23.2185, 88.3685],
    "Kharagpur": [22.3369, 87.3275],
    "Kharagpurchowrangee": [22.3550, 87.3100],
    "Garia Bus Stand": [22.4650, 88.3930],
    "Habra Depot": [22.8364, 88.6318],
    "Habra": [22.8350, 88.6300],
    "Purulia": [23.3323, 86.3653],
    "Dhamakhali": [22.3562, 88.8570],
    "Bakkhali": [21.5647, 88.2625],
    "Frazerganj": [21.5790, 88.2560],
    "Panshkura": [22.3956, 87.7288],
    "Panskura": [22.3956, 87.7288],
    "Golf Green": [22.4930, 88.3630],
    "Picnic Garden": [22.5340, 88.3840],
    "Gadiara": [22.2178, 88.0538],
    "Jangipur": [24.4727, 88.0720],
    "Kulti": [23.7314, 86.8450],
    "Burul": [22.3780, 88.1340],
    "Patharpratima": [21.7925, 88.3540],
    "Amrabati": [22.7120, 88.3810],
    "Chinsurah Court": [22.8900, 88.3900],
    "Khadina": [22.8920, 88.3810],
    "Ladhurka": [23.3610, 86.4950],
    "Raghunathganj": [24.4640, 88.0820],
    "Nayabad": [22.4740, 88.4060],
    "Badartala": [22.5250, 88.2930],
    "Tarakeswar": [22.8910, 88.0210],
    "Joka Depot": [22.4610, 88.3030],
    "Dhupguri": [26.5950, 89.0140],
    "Salbari": [26.7450, 88.3970],
    "Siliguri": [26.7271, 88.4173],
    "Asansol": [23.6889, 86.9661],
    "Durgapur": [23.5204, 87.3119],
    "Burdwan": [23.2324, 87.8615],
    "Krishnanagar": [23.4013, 88.5010],
    "Berhampore": [24.1025, 88.2505],
    "Midnapore": [22.4257, 87.3199],
    "Haldia": [22.0667, 88.0667],
    "Contai": [21.7781, 87.7513],
    "Kakdwip": [21.8764, 88.1895],
    "Namkhana": [21.7675, 88.2325],
    "Canning": [22.3160, 88.6580],
    "Basirhat": [22.6570, 88.8910],
    "Hasnabad": [22.5710, 88.9180],
    "Taki": [22.5900, 88.9220],
    "Bongaon": [23.0470, 88.8260],
    "Andul Station": [22.5780, 88.2430],
    "Ariadaha": [22.6610, 88.3660],
    "Bagdah": [23.2080, 88.8780],
    "Diamond Harbour": [22.1880, 88.1920],
    "Santragachi Station": [22.5810, 88.2770],
    "Sealdah Station": [22.5675, 88.3700],
    "Kolkata Station": [22.6020, 88.3780],
    "Barasat": [22.7240, 88.4810],
    "Machlandapur": [22.8940, 88.7510],
    "Chakdaha": [23.0800, 88.5200],
    "Ranaghat": [23.1800, 88.5800],
    "Chinsurah": [22.9000, 88.3900],
    "Bandel": [22.9200, 88.3800],
    "Balisai": [21.6620, 87.5620],
    "BT College": [22.6460, 88.3810],
    "B.T. College": [22.6460, 88.3810],
    "Alampur": [22.3550, 87.3100],
    "Posta Bazar": [22.5860, 88.3510],
    "Posta": [22.5860, 88.3510],
    "Bagmari Bazar": [22.5840, 88.3860],
    "Bagmari": [22.5840, 88.3860],
    "Baranagar Bazar": [22.6390, 88.3680],
    "Baranagar": [22.6390, 88.3680],
    "College More": [22.5770, 88.4290],
    "Swasthya Bhawan": [22.5706, 88.4264],
    "Bikash Bhawan": [22.5890, 88.4110],
    "Bhowani Bhawan": [22.5335, 88.3395],
    "Doordarshan Bhawan": [22.5020, 88.3490],
    "GST Bhawan": [22.5160, 88.3870],
    "Colony More": [22.7232, 88.4785],
    "Rajarhat Chowmatha": [22.6267, 88.4890],
    "City Centre 1": [22.5890, 88.4084],
    "City Center 1": [22.5890, 88.4084],
    "City Centre 2": [22.6180, 88.4480],
    "City Center 2": [22.6180, 88.4480],
}



SPELLING = {
    # Alternate spellings / transliterations
    "rashbihari": "rashbehari",
    "rashbilhari": "rashbehari",
    "rash bihari": "rashbehari",
    "khiderpur": "kidderpore",
    "khidirpur": "kidderpore",
    "kidderpur": "kidderpore",
    "burrabazar": "barabazar",
    "barra bazar": "barabazar",
    "mominpur": "mominpore",
    "bhawanipur": "bhowanipore",
    "bhowanipore": "bhowanipore",
    "bhavaanipur": "bhowanipore",
    "tollygunj": "tollygunge",
    "tollyganj": "tollygunge",
    "dum dum": "dumdum",
    "ultodanga": "ultadanga",
    "sobhabazar": "sovabazar",
    "shobhabazar": "sovabazar",
    "moulai": "moulali",
    "moulali": "moulali",
    "babughat": "babu ghat",
    "baboo ghat": "babu ghat",
    "eden gardens": "eden garden",
    "howrah stn": "howrah station",
    "howrah st": "howrah station",
    "hwr stn": "howrah station",
    "kolkata stn": "sealdah",
    "rg kar hospital": "rg kar",
    "r g kar": "rg kar",
    "salt lake sector v": "sector v",
    "saltlake sector v": "sector v",
    "saltlake": "salt lake",
    "new town": "newtown",
    "airport gate no 1": "airport gate 1",
    "airport gate no.1": "airport gate 1",
    "airport gate no 1": "airport gate 1",
    "airport gate i": "airport gate 1",
    "ballygaunj": "ballygunge",
    "ballygunj": "ballygunge",
    "belgachhia": "belgachia",
    "belghoria": "belgharia",
    "barrack pore": "barrackpore",
    "santragachhi": "santragachi",
    "santragachi": "santragachi",
    "deshapriya park": "deshapriya park",
    "deshoprio park": "deshapriya park",
    "deshopriya park": "deshapriya park",
    "jadavpur": "jadavpur 8b",
    "ruby more": "ruby",
    "science city more": "science city",
    "nicco park more": "nicco park more",
    "city centre ii": "city centre 2",
    "city center ii": "city centre 2",
    "city centre 2": "city centre 2",
    # Ghat / water-front variants
    "babughat": "babu ghat",
    "princep ghat": "prinsep ghat",
    "prinsep ghat": "prinsep ghat",
    # Station / metro suffix stripping
    "sealdah station": "sealdah",
    "sealdah stn": "sealdah",
    "howrah bridge": "howrah station",
    "garia station": "garia station",
    "barrackpore station": "barrackpore station",
    "naihati stn": "naihati station",
    "bhatpara station": "bhatpara",
    # North Kolkata
    "chiria more": "chiria",
    "chiria": "chiria",
    "shyam bazar": "shyambazar",
    "belgachhi": "belgachia",
    "rajbari": "rajabazar",
    "khanna": "khanna cinema",
    "patipukur more": "patipukur",
    # South Kolkata
    "jadavpur 8 b": "jadavpur 8b",
    "8b jadavpur": "jadavpur 8b",
    "jadu babu bazar": "jadavpur 8b",
    "golpark more": "golpark",
    "gariahat more": "gariahat",
    "kalighat metro": "kalighat",
    "tollygunge metro station": "tollygunge metro",
    "mahanayak uttam kumar metro": "tollygunge metro",
    "nsc bose metro": "netaji metro",
    "rabindra sarobar": "rabindra sarovar",
    "rabindra sarovar metro": "rabindra sarovar",
    "behala": "behala chowrasta",
    "behala chowrasta": "behala chowrasta",
    "biren roy road": "behala chowrasta",
    "thakurpukur": "thakurpukur",
    "takurpukur": "thakurpukur",
    # East / EM Bypass
    "em bypass": "em bypass",
    "eastern metropolitan bypass": "em bypass",
    "ruby crossing": "ruby",
    "ruby hospital": "ruby hospital",
    "acropolis": "acropolis mall",
    "vip road": "vip bazar",
    "vip bazar": "vip bazar",
    "vip market": "vip bazar",
    "kalikapur more": "kalikapur",
    "mukundapur more": "mukundapur",
    # Howrah
    "howrah maidan": "howrah maidan",
    "h maidan": "howrah maidan",
    "santragachhi": "santragachi",
    "santragachi station": "santragachi",
    "shibpur td": "shibpur td",
    "shibpur td more": "shibpur td",
    "tikiapara": "tikiapara bypass",
    "tikiapara more": "tikiapara bypass",
    # Barrackpore corridor
    "dunlop more": "dunlop",
    "bonhoogli": "bonhooghly",
    "bon hooghly": "bonhooghly",
    "sodepur more": "sodepur",
    "khardah": "khardaha",
    "khardha": "khardaha",
    "titagarh station": "titagarh",
    # Salt Lake / Newtown
    "bikash bhawan": "bikash bhawan",
    "bik bhawan": "bikash bhawan",
    "city centre 1": "city centre 1",
    "city center 1": "city centre 1",
    "salt lake city centre": "city centre 1",
    "karunamoyee bus stand": "karunamoyee",
    "wipro more": "wipro",
    "techno india": "sector v",
    "sdf more": "sdf",
    "mahishbathaan": "mahishbathan",
    # Common suffix/prefix stripping handled in norm_key
}


# Suffixes/prefixes that can be stripped to improve match rate
_STRIP_SUFFIXES = (
    " bus stop", " bus stand", " bus terminus", " terminus",
    " bus depot", " depot", " crossing", " intersection",
    " halt", " junction",
)
_STRIP_PREFIXES = ("new ",)


def norm_key(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # Apply spelling aliases
    for src, dst in SPELLING.items():
        if src in text:
            text = text.replace(src, dst)
    # Strip common meaningless suffixes that hurt fuzzy matching
    for suf in _STRIP_SUFFIXES:
        if text.endswith(suf):
            text = text[: -len(suf)].strip()
            break
    return text


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


_GENERIC_TOKENS = {
    "bazar", "bazaar", "market", "station", "stn", "stop", "stand", "terminus",
    "depot", "road", "street", "lane", "gate", "park", "more", "crossing",
    "bridge", "nagar", "colony", "hospital", "college", "school", "court",
    "house", "bhavan", "bhawan", "ghat", "danga", "pur", "para", "pukur",
    "bypass", "chowmatha", "chourasta", "cinema", "hall", "ground", "railway",
    "rlway", "metro", "bus", "auto", "junction", "jct", "cinema", "office",
}


def build_osm_index(osm_stops: list[dict]):
    index = {}
    tokens_index = {}
    for stop in osm_stops:
        key = norm_key(stop["name"])
        if not key:
            continue
        index.setdefault(key, []).append((stop["lat"], stop["lon"], stop["name"]))
        for tok in key.split():
            if len(tok) >= 5 and tok not in _GENERIC_TOKENS:
                tokens_index.setdefault(tok, []).append((stop["lat"], stop["lon"], stop["name"], key))
    return index, tokens_index


def best_osm_match(name: str, index: dict, tokens_index: dict, threshold: float = 0.82):
    key = norm_key(name)
    if not key:
        return None
    if key in index:
        lat, lon, src = index[key][0]
        return lat, lon, "osm_exact", src

    key_tokens = set(key.split())
    non_generic_kt = {t for t in key_tokens if t not in _GENERIC_TOKENS}
    if not non_generic_kt:
        return None  # Do not attempt fuzzy matching if name has only generic tokens!

    candidates = set()
    for tok in non_generic_kt:
        if len(tok) >= 4:
            for okey in index:
                if len(okey) >= 4 and tok in okey:
                    candidates.add(okey)

    best = None
    for okey in candidates:
        if len(okey) <= 3:
            continue
        ot = set(okey.split())
        non_generic_ot = {t for t in ot if t not in _GENERIC_TOKENS}
        if not (non_generic_kt & non_generic_ot):
            continue  # Must share at least one non-generic token!

        ratio = SequenceMatcher(None, key, okey).ratio()
        overlap = len(non_generic_kt & non_generic_ot) / max(len(non_generic_kt), len(non_generic_ot))
        ratio = max(ratio, overlap * 0.90)

        if ratio >= threshold and (best is None or ratio > best[0]):
            lat, lon, src = index[okey][0]
            best = (ratio, lat, lon, "osm_fuzzy" if ratio < 0.90 else "osm_exact", src)


    if best:
        return best[1], best[2], best[3], best[4]

    return None

    return None


def nominatim_geocode(name: str):
    query = f"{name}, Kolkata, West Bengal, India"
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "q": query, "format": "json", "limit": 1, "countrycodes": "in",
    })
    req = urllib.request.Request(url, headers={"User-Agent": "kolkata-bus-map/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        results = json.loads(resp.read())
    if not results:
        return None
    lat, lon = float(results[0]["lat"]), float(results[0]["lon"])
    if 22.3 <= lat <= 23.0 and 88.0 <= lon <= 88.8:
        return lat, lon
    return None


def interpolate_missing(routes: list, geocoded: dict):
    """Fill gaps by linear interpolation between known stops on same route."""
    added = 0
    for route in routes:
        stops = route["stops"]
        known = [(i, geocoded[s]["lat"], geocoded[s]["lng"]) for i, s in enumerate(stops) if s in geocoded]
        if len(known) < 2:
            continue
        for i, s in enumerate(stops):
            if s in geocoded:
                continue
            prev = next((k for k in reversed(known) if k[0] < i), None)
            nxt = next((k for k in known if k[0] > i), None)
            if prev and nxt:
                t = (i - prev[0]) / (nxt[0] - prev[0])
                lat = prev[1] + t * (nxt[1] - prev[1])
                lon = prev[2] + t * (nxt[2] - prev[2])
                geocoded[s] = {"lat": lat, "lng": lon, "source": "interpolated", "matched": s}
                added += 1
    return added


def main(max_nominatim: int = 0):
    busdata = load_json(BUSDATA, {})
    osm_stops = load_json(OSM_STOPS, [])
    cache = load_json(GEOCODE_CACHE, {})
    osm_index, tokens_index = build_osm_index(osm_stops)

    stop_names = sorted({s["name"] for s in busdata.get("stops", [])} |
                        {stop for r in busdata.get("routes", []) for stop in r["stops"]})

    geocoded = dict(cache)
    stats = {"hub": 0, "busdata": 0, "osm_exact": 0, "osm_fuzzy": 0, "osm_token": 0,
             "cache": 0, "nominatim": 0, "interpolated": 0, "missing": 0}
    nominatim_used = sum(1 for v in geocoded.values() if v.get("source") == "nominatim")

    busdata_coords = {s["name"]: (s["lat"], s["lng"]) for s in busdata.get("stops", [])
                      if s.get("lat") is not None and s.get("lng") is not None}

    for i, name in enumerate(stop_names):
        if name in HUB:
            geocoded[name] = {"lat": HUB[name][0], "lng": HUB[name][1], "source": "hub", "matched": name}
            stats["hub"] += 1
            continue

        if name in geocoded:
            stats["cache"] += 1
            continue

        lat = lon = source = matched = None

        if name in busdata_coords:
            lat, lon = busdata_coords[name]; source, matched = "busdata", name; stats["busdata"] += 1
        else:
            hit = best_osm_match(name, osm_index, tokens_index)
            if hit:
                lat, lon, source, matched = hit[0], hit[1], hit[2], hit[3]
                stats[source] += 1
            elif nominatim_used < max_nominatim:
                try:
                    coords = nominatim_geocode(name)
                    time.sleep(1.1)
                    if coords:
                        lat, lon = coords; source, matched = "nominatim", name
                        stats["nominatim"] += 1; nominatim_used += 1
                except Exception:
                    pass

        if lat is not None:
            geocoded[name] = {"lat": lat, "lng": lon, "source": source, "matched": matched}
            if i % 25 == 0:
                save_json(GEOCODE_CACHE, geocoded)
        else:
            stats["missing"] += 1

    interp = interpolate_missing(busdata.get("routes", []), geocoded)
    stats["interpolated"] = interp

    save_json(GEOCODE_CACHE, geocoded)
    save_json(STOPS_OUT, geocoded)
    print(f"Geocoded {len(geocoded)}/{len(stop_names)} stops")
    print("Stats:", stats)


if __name__ == "__main__":
    main()
