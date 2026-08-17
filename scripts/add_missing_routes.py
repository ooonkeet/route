"""Add missing routes from kolbusopedia.com to busdata.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
BUSDATA = DATA / "busdata.json"

with open(BUSDATA, encoding="utf-8") as f:
    data = json.load(f)

existing_ids = set()
for r in data["routes"]:
    rid = (r["code"], r.get("towards", ""), r.get("kind", ""))
    existing_ids.add(rid)

def already(code, towards, kind):
    return (code, towards, kind) in existing_ids

def add(code, kind, stops, towards, scope="local", directional=True):
    rid = (code, towards, kind)
    if rid in existing_ids:
        return
    data["routes"].append({
        "code": code,
        "kind": kind,
        "stops": stops,
        "scope": scope,
        "directional": directional,
        "towards": towards,
    })
    existing_ids.add(rid)

# ── S-series (Mini/RT private Howrah) ──────────────────────────────────────
# These are the "S-" numbered mini routes from the kolbusopedia private page

add("S-101", "mini", ["Garia Bus Stand","Ramgarh","Baghajatin","Jadavpur 8B","Dhakuria","Golpark","Gariahat","Ballygunge Phari","Gurusaday Road","Beck Bagan","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag"], "BBD Bag")
add("S-101/1", "mini", ["Garia Station","Dhalai Bridge","Patuli","Hiland Park","Ajaynagar","Mukundapur","Kalikapur","Ruby","VIP Bazar","Science City","Topsia","Park Circus","Beck Bagan","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag"], "BBD Bag")
add("S-102", "mini", ["Patuli","Baisnabghata","Ramgarh","Baghajatin","Jadavpur 8B","Dhakuria","Golpark","Gariahat","Ballygunge Phari","Gurusaday Road","Beck Bagan","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag"], "BBD Bag")
add("S-103", "mini", ["Jadavpur 8B","Dhakuria","Golpark","Gariahat","Ballygunge Phari","Gurusaday Road","Beck Bagan","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag"], "BBD Bag")
add("S-104", "mini", ["Jodhpur Park","Dhakuria","Golpark","Gariahat","Ballygunge Phari","Gurusaday Road","Beck Bagan","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag"], "BBD Bag")
add("S-106", "mini", ["Daspara","Nayabad","Mukundapur","EM Bypass","Ajaynagar","Santoshpur","Jadavpur 8B","Dhakuria","Golpark","Gariahat","Ballygunge Phari","Gurusaday Road","Beck Bagan","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag"], "BBD Bag")
add("S-107", "mini", ["Anandapur","Ruby","Acropolis Mall","Bosepukur","Kasba PS","Ballygunge Station","Gariahat","Ballygunge Phari","Garcha Road","Sishu Mangal","Lansdowne","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-107/1", "mini", ["Anandapur","Ruby","Acropolis Mall","Bosepukur","Kasba PS","Ballygunge Station","Gariahat","Deshapriya Park","Rashbehari","Kalighat","Hazra","Bhowanipore","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-108", "mini", ["Kasba Rathtala","Kasba Post Office","Ballygunge Station","Gariahat","Ballygunge Phari","Quest Mall","Park Circus","Mallick Bazar","Moulali","Wellington","Chandni Chowk","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-109", "mini", ["Ballygunge Station","Gariahat","Ballygunge Phari","Gurusaday Road","Beck Bagan","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag"], "BBD Bag")
add("S-110", "mini", ["Golf Green","Doordarshan Bhawan","Lake Gardens","South City","Jadavpur PS","Dhakuria","Golpark","Gariahat","Ballygunge Phari","Quest Mall","Park Circus","Chittaranjan Hospital","CIT Road","Moulali","Wellington","Chandni Chowk","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-111", "mini", ["Lake Road","Deshapriya Park","Sishu Mangal","Lansdowne","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-112", "mini", ["Garia Station","Dhalai Bridge","Garia Metro","Naktala","Bansdroni","Netaji Nagar","Ranikuthi","Malancha Cinema","Tollygunge Metro","Rabindra Sarovar","Rashbehari","Kalighat","Hazra","Bhowanipore","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-113", "mini", ["Harinavi","Rajpur Bazar","Narendrapur","Kamalgazi","Mahamayatala","Garia Metro","Naktala","Bansdroni","Netaji Nagar","Ranikuthi","Malancha Cinema","Tollygunge Metro","Rabindra Sarovar","Rashbehari","Kalighat","Hazra","Bhowanipore","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-117", "mini", ["Kalitala Housing","Kabardanga","Keorapukur","Haridevpur","Tollygunge Metro","Rabindra Sarovar","Rashbehari","Kalighat","Hazra","Bhowanipore","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-121", "mini", ["Behala Chowrasta","Behala 14 No","Majherhat","Mominpore","Alipore Court","Bhabani Bhawan","Alipore Zoo","PTS","Fort William","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-123", "mini", ["Metiabruz","Bichali Ghat","Kamal Talkies","Ramnagar","Garden Reach","Babubazar","Kidderpore","Hastings","Fort William","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-124", "mini", ["Garia Station","Peerless Hospital","EM Bypass","Ajaynagar","Mukundapur","Kalikapur","Sapuipara","Saheed Nagar","Jadavpur PS","Dhakuria","Golpark","Gariahat","Deshapriya Park","Sishu Mangal","Lansdowne","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-125", "mini", ["Picnic Garden","Bondel Gate","Park Circus","Mallick Bazar","Moulali","Wellington","Chandni Chowk","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-126", "mini", ["Batanagar","Bata","Dakghar","Mollar Gate","Rampur Quarter","SM Nagar","Sarkarpool","Jhinjhira Bazar","Brace Bridge","Hide Road","Babubazar","Kidderpore","Hastings","Fort William","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-128", "mini", ["Picnic Garden","Colony Bazar","Bondel Gate","4 No Bridge","Chittaranjan Hospital","CIT Road","Moulali","Wellington","Chandni Chowk","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-129", "mini", ["Rabindra Nagar","Parnasree","Behala PS","Majherhat","Mominpore","Alipore Court","Bhabani Bhawan","Alipore Zoo","PTS","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-131", "mini", ["Joka Bridge","Thakurpukur","Shilpara","Sakher Bazar","Behala Chowrasta","Behala 14 No","Majherhat","Mominpore","Alipore Court","Hazra","Kalighat","Rashbehari","Deshapriya Park","Gariahat","Ballygunge Station","Kasba PS","Bosepukur","Acropolis Mall","EM Bypass","Ruby"], "Ruby")
add("S-135", "mini", ["Baisnabghata","Ramgarh","Baghajatin","Jadavpur 8B","South City","Lake Gardens","Anwar Shah Road","Tollygunge Phari","Rabindra Sarovar","Rashbehari","Kalighat","Hazra","Bhowanipore","Rabindra Sadan","Maidan","Park Street","Esplanade","BBD Bag","Barabazar","Howrah Station","Howrah Maidan"], "Howrah Maidan")
add("S-139", "mini", ["Shyambazar","Rajballavpara","Sovabazar","Girish Park","MG Road","Central","BBD Bag","Babughat"], "Babughat")
add("S-151", "mini", ["Airport Gate 1","Kaikhali","Haldirams","Baguiati","Kestopur","Dumdum Park","Laketown","Sreebhumi","Ultadanga","Kankurgachi","Maniktala","Vivekananda Road","Girish Park","MG Road","Central","BBD Bag"], "BBD Bag")
add("S-152", "mini", ["Baguiati","Kestopur","Dumdum Park","Laketown","Sreebhumi","Ultadanga","Kankurgachi","Maniktala","Vivekananda Road","Girish Park","MG Road","Central","BBD Bag"], "BBD Bag")
add("S-158", "mini", ["Dakshineswar","Alambazar","Deshbandhu Road","Bonhooghly","Baranagar Bazar","Sinthi","Chiria","Shyambazar","Hatibagan","Hedua","Vivekananda Road","Amherst Street","Bank Of India","Bowbazar","Central","BBD Bag","Babughat"], "Babughat")
add("S-159", "mini", ["Dunlop","Bonhooghly","Tobin Road","Sinthi","Chiria","Shyambazar","Rajballavpara","Sovabazar","Girish Park","MG Road","Central","BBD Bag"], "BBD Bag")
add("S-161", "mini", ["Shyambazar","Rajballavpara","Sovabazar","Girish Park","MG Road","Central","BBD Bag","Esplanade","Babughat","Princep Ghat","Hastings","Kidderpore","Babubazar","Garden Reach","Ramnagar","Kamal Talkies","Bichali Ghat","Metiabruz"], "Metiabruz")
add("S-163", "mini", ["Shyambazar","Rajballavpara","Sovabazar","Girish Park","MG Road","Central","BBD Bag"], "BBD Bag")
add("S-165", "mini", ["Phoolbagan","Rajabazar","Sealdah","Bank Of India","Bowbazar","Central","Lalbazar","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-166", "mini", ["Tangra","RN Chowdhury Road","Palmer Bazar","Sealdah","Moulali","Wellington","Chandni Chowk","Esplanade","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-167", "mini", ["Saltlake","Bikash Bhawan","Karunamoyee","Saltlake 12no Tank","Sushrut Hospital","Saltlake 14no Tank","Saltlake 16no Tank","Beleghata Building","Beleghata","Sealdah","Moulali","Wellington","Chandni Chowk","Esplanade","BBD Bag"], "BBD Bag")
add("S-168", "mini", ["Nager Bazar","Dumdum Station","Chiria","Shyambazar","Rajballavpara","Sovabazar","Beadon Street","Jorabagan","Malapara","Barabazar","Posta Bazar","Howrah Station"], "Howrah Station")
add("S-172", "mini", ["Teghoria","Baguiati","Kestopur","Dumdum Park","Laketown","Sreebhumi","Ultadanga","Khanna Cinema","Maniktala","Vivekananda Road","Girish Park","MG Road","Barabazar","Howrah Maidan"], "Howrah Maidan")
add("S-173", "mini", ["Saltlake","Bikash Bhawan","Karunamoyee","Central Park","Labony Estate","Saltlake 13no Tank","Saltlake Stadium","Kadapara","Subhash Sarobar","Beleghata","Sealdah","College Street","MG Road","Barabazar","Howrah Station"], "Howrah Station")
add("S-175", "mini", ["New Barrackpore","BT College","Michaelnagar","Birati","Airport Gate 3","Airport Gate 1","Kaikhali","Haldirams","Baguiati","Kestopur","Dumdum Park","Laketown","Sreebhumi","Ultadanga","Khanna Cinema","Hatibagan","Sovabazar","Girish Park","MG Road","Central","BBD Bag","Barabazar","Howrah Station"], "Howrah Station")
add("S-176", "mini", ["Shyambazar","Rajballavpara","Sovabazar","BK Paul","Ahiritola","Jorabagan","Malapara","Barabazar","Posta Bazar","Howrah Station","Howrah Maidan"], "Howrah Maidan")
add("S-178", "mini", ["Behala 14 No","Majherhat","Mominpore","Alipore Court","Kalighat","Hazra","Bhowanipore","Rabindra Sadan","Minto Park","Beck Bagan","Mallick Bazar","Moulali","Sealdah","Rajabazar"], "Rajabazar")
add("S-180", "mini", ["Belgharia Station","Rathtala","Dunlop","Bonhooghly","Tobin Road","Sinthi","Chiria","Shyambazar","Rajballavpara","Sovabazar","BK Paul","Ahiritola","Jorabagan","Malapara","Barabazar","Posta Bazar","Howrah Station","Howrah Maidan"], "Howrah Maidan")
add("S-184", "mini", ["Birati Station","Birati","Airport Gate 3","Airport Gate 1","Kaikhali","Haldirams","Baguiati","Kestopur","Dumdum Park","Laketown","Sreebhumi","Ultadanga","Kankurgachi","Maniktala","Vivekananda Road","Girish Park","MG Road","Central","BBD Bag"], "BBD Bag")
add("S-185", "mini", ["Nimta Bazar","Belgharia Station","Rathtala","Dunlop","Bonhooghly","Tobin Road","Sinthi","Chiria","Shyambazar","Rajballavpara","Sovabazar","BK Paul","Ahiritola","Jorabagan","Malapara","Barabazar","Posta Bazar","Howrah Station"], "Howrah Station")
add("S-186", "mini", ["Uttar Panchannagram","Science City","Topsia","4 No Bridge","Chittaranjan Hospital","CIT Road","Moulali","Sealdah","College Street","MG Road","Barabazar","Howrah Station"], "Howrah Station")
add("S-189", "mini", ["Shyambazar","Rajballavpara","Sovabazar","BK Paul","Ahiritola","Jorabagan","Malapara","Barabazar","Posta Bazar","Howrah Station","Howrah Maidan"], "Howrah Maidan")

# ── RT-Series (Howrah private) ─────────────────────────────────────────────
add("RT-1", "private", ["Salkia Chowrasta","Bandha Ghat","Golabarai PS","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-1A", "private", ["Satyabala","Salkia Chowrasta","Bandha Ghat","Golabarai PS","Howrah Station","Barabazar","BBD Bag","Esplanade","Park Street","Maidan","Rabindra Sadan","Minto Park","Lansdowne","Sishu Mangal"], "Sishu Mangal")
add("RT-2", "private", ["Salkia Chowrasta","Bandha Ghat","Golabarai PS","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-3", "private", ["Kadamtala","Ichapur","Shanpur","Tikiapara Bypass","Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-3A", "private", ["Kamardanga","Ichapur","Shanpur","Tikiapara Bypass","Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-5", "private", ["Japani Gate","Dasnagar","Shanpur","Tikiapara Bypass","Howrah Station","Barabazar","Posta Bazar","Malapara","Jorabagan","Ahiritola","BK Paul","Sovabazar","Hatibagan","Khanna Cinema","Ultadanga","Saltlake PNB","Saltlake 4no Tank","Baisakhi","Purta Bhawan","Karunamoyee","Wipro","SDF","College More","Sector V"], "Sector V")
add("RT-6", "private", ["B Garden","Shalimar Station","Bataitala Phari","Kazipara","Avani Mall","Shibpur Bazar","Mallick Fatak","Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-6A", "private", ["Danesh Shaikh Lane","Amtala Phari","Narayana Hospital","Bataitala Phari","Kazipara","Avani Mall","Shibpur Bazar","Mallick Fatak","Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-7", "private", ["Howrah Maidan","Amtala Phari","Howrah Station","Barabazar","Posta Bazar","Malapara","Jorabagan","Ahiritola","BK Paul","Sovabazar","Rajballavpara","Shyambazar"], "Shyambazar")
add("RT-8", "private", ["Mandirtala","Kazipara","Avani Mall","Shibpur Bazar","Mallick Fatak","Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-10", "private", ["Ballykhal","Bally Bazar","Belurmath","Liluah","Bandha Ghat","Salkia Chowrasta","Golabarai PS","Howrah Station","Barabazar","BBD Bag","Esplanade","Babughat","Princep Ghat","Hastings","Kidderpore"], "Kidderpore")
add("RT-11", "private", ["Belurmath","Liluah","Bandha Ghat","Salkia Chowrasta","Golabarai PS","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-11A", "private", ["Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade","Park Street","Maidan","Rabindra Sadan"], "Rabindra Sadan")
add("RT-13", "private", ["Ranihati","Dhulagarh","Alampur","Andul Bazar","Mourigram","Chunavati","Hanskhali","Bakultala","Danesh Shaikh Lane","Amtala Phari","Narayana Hospital","Bataitala Phari","Kazipara","Avani Mall","Shibpur Bazar","Mallick Fatak","Howrah Maidan","Howrah Station","Barabazar","Posta Bazar","Malapara","Jorabagan","Ahiritola"], "Ahiritola")
add("RT-13A", "private", ["Fatickgachi","Dhulagarh","Alampur","Andul Bazar","Mourigram","Chunavati","Hanskhali","Bakultala","Danesh Shaikh Lane","Amtala Phari","Narayana Hospital","Bataitala Phari","Kazipara","Avani Mall","Shibpur Bazar","Mallick Fatak","Howrah Maidan","Howrah Station","Barabazar","Posta Bazar","Malapara","Jorabagan","Ahiritola"], "Ahiritola")
add("RT-18", "private", ["Kona","Biradingi","Belgachia","Bamangachi","Salkia Chowrasta","Bandha Ghat","Golabarai PS","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-20", "private", ["Alampur","Andul Bazar","Mourigram","Chunavati","Hanskhali","Bakultala","Danesh Shaikh Lane","Amtala Phari","Narayana Hospital","Bataitala Phari","Kazipara","Avani Mall","Shibpur Bazar","Mallick Fatak","Howrah Maidan","Howrah Station","Barabazar","Posta Bazar","Malapara","Jorabagan","Ahiritola","BK Paul","Sovabazar","Hatibagan","Khanna Cinema","Ultadanga"], "Ultadanga")
add("RT-20A", "private", ["Mourigram","Chunavati","Hanskhali","Bakultala","Danesh Shaikh Lane","Amtala Phari","Narayana Hospital","Bataitala Phari","Kazipara","Avani Mall","Shibpur Bazar","Mallick Fatak","Howrah Maidan","Howrah Station","Barabazar","MG Road","Girish Park","Maniktala","Vivekananda Road","Kankurgachi","Ultadanga","Saltlake PNB","Saltlake CA Block","Labony Estate","Saltlake 13no Tank","Saltlake Stadium"], "Saltlake Stadium")
add("RT-21", "private", ["Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade","Fort William","PTS","Alipore Zoo","Ekbalpur","Mominpore","Majherhat","Behala 14 No","Behala Chowrasta","Sakher Bazar","Shilpara"], "Shilpara")
add("RT-24", "private", ["Sankrail","Chapatala","Rajgunge","Radhadashi","Podra Bazar","Nazirgunge","Bakultala","Danesh Shaikh Lane","Amtala Phari","Narayana Hospital","Bataitala Phari","Kazipara","Avani Mall","Shibpur Bazar","Mallick Fatak","Howrah Maidan","Howrah Station"], "Howrah Station")
add("RT-25", "private", ["Malipanchghara","Bandha Ghat","Salkia Chowrasta","Golabarai PS","Howrah Station","Barabazar","MG Road","College Street","Sealdah"], "Sealdah")
add("RT-26", "private", ["Santragachi","Baksara","Belepole","Natun Rasta","Ichapur","Shanpur","Tikiapara Bypass","Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-27", "private", ["Bankra Bazar","Japani Gate","Dasnagar","Shanpur","Tikiapara Bypass","Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade","Chandni Chowk","Wellington","Moulali","CIT Road","Chittaranjan Hospital","Park Circus"], "Park Circus")
add("RT-27A", "private", ["Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade","Chandni Chowk","Wellington","Moulali","CIT Road","Chittaranjan Hospital","Park Circus"], "Park Circus")
add("RT-29", "private", ["Tikiapara","Belilious Road","Howrah Maidan","Howrah Station","Barabazar","Posta Bazar","Malapara","Jorabagan","Ahiritola","BK Paul","Sovabazar","Hatibagan","Khanna Cinema","Ultadanga","Saltlake PNB","Saltlake 4no Tank","Baisakhi","Purta Bhawan","Karunamoyee","Wipro","SDF","College More","Sector V"], "Sector V")
add("RT-30", "private", ["Baluhati","Jagadishpur","Chamrail","Kona","Biradingi","Belgachia","Bamangachi","Salkia Chowrasta","Bandha Ghat","Golabarai PS","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-31", "private", ["Makardaha","Katlia","Salap","Bankra Bazar","Japani Gate","Dasnagar","Shanpur","Tikiapara Bypass","Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade","Park Street","Maidan","Rabindra Sadan"], "Rabindra Sadan")
add("RT-32", "private", ["Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade","Park Street","Maidan","Rabindra Sadan"], "Rabindra Sadan")
add("RT-34", "private", ["Purash","Ghoradaha","Munshirhat","Bargachia","Domjur","Makardaha","Katlia","Salap","Bankra Bazar","Japani Gate","Dasnagar","Shanpur","Tikiapara Bypass","Howrah Maidan","Howrah Station"], "Howrah Station")
add("RT-35", "private", ["Hantal","Bargachia","Domjur","Makardaha","Katlia","Salap","Bankra Bazar","Japani Gate","Dasnagar","Shanpur","Tikiapara Bypass","Howrah Maidan","Howrah Station"], "Howrah Station")
add("RT-38", "private", ["Dasnagar","Shanpur","Tikiapara Bypass","Howrah Maidan","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")
add("RT-39", "private", ["Bhattanagar","Liluah Station","Bamangachi","Salkia Chowrasta","Bandha Ghat","Golabarai PS","Howrah Station","Barabazar","BBD Bag","Esplanade"], "Esplanade")

# ── Specific missing routes ────────────────────────────────────────────────

# 3C/2: Anandapur to Nagerbazar (via different route than 3C/1)
add("3C/2", "private", ["Anandapur","Ruby","Acropolis Mall","Bosepukur","Kasba PS","Ballygunge Station","Gariahat","Deshapriya Park","Shishu Mangal","Minto Park","Rabindra Sadan","Maidan","Park Street","Esplanade","Wellington","College Street","Hatibagan","Shyambazar","RG Kar","Belgachia","Patipukur","Kalindi","Bangur Avenue","Diamond Plaza","Nager Bazar"], "Nager Bazar")

# 91B: Shyambazar to Pakapole
add("91B", "private", ["Shyambazar","RG Kar","Belgachia","Patipukur","Kalindi","Bangur Avenue","Diamond Plaza","Nager Bazar","Central Jail","Airport Gate 1","Kaikhali","Haldirams","Chinar Park","Salua Bazar","Derozio College","Reckjuani","Rajarhat Chowmatha","Bishnupur","Lauhati","Vedic Village","Shikharpur","Pakapole"], "Pakapole")

# 204/1: Chetla Park to Rajabazar
add("204/1", "private", ["Chetla Park","Alipore Court","Kalighat","Hazra","Sishu Mangal","Garcha","Ballygunge Phari","Broad Street","4 No Bridge","CIT Road","Chittaranjan Hospital","Moulali","Sealdah","Rajabazar"], "Rajabazar")

# 241: Santoshpur Station to Esplanade
add("241", "private", ["Santoshpur Station","Akra Fatak","Bartala Bazar","Metiabruz","Bichali Ghat","Kamal Talkies","Ramnagar","Garden Reach","Babubazar","Kidderpore","Hastings","Fort William","Esplanade"], "Esplanade")

# DN-2: Barasat to Dakshineshwar
add("DN-2", "government", ["Barasat Chapadali","Madhyamgram","B.T. College","Birati More","Birati Station","Nimta Bazar","Culture","Badamtala","Belgharia Station","Rathtala","Dunlop","Dakshineswar"], "Dakshineswar")

# DN-19: Barrackpore Court to Chapadali shuttle
add("DN-19", "government", ["Barrackpore Court","Barrackpore Cantonment","Chiriamore","Barrackpore Station","Nonachandanpukur","Wireless Gate","Mohanpur","Chapuria","Gheedah","Mathrangi More","Nilgunge Hat","Kazibari","Jagannathpur","Helabattala","Colony More","Barasat Chapadali"], "Barasat Chapadali")

# DN-21: Baduria runs to Barasat
add("DN-21", "government", ["Baduria","Banipur","Habra","Ashoknagar","Guma","Lakshmipool","Bira","Duttapukur","Bamangachi","Barasat Chapadali","Madhyamgram","Airport Gate 1","Baguiati","Kestopur","Ultadanga"], "Ultadanga")

# DN-26: Gaighata to Kalyani (Jagulia)
add("DN-26", "government", ["Gaighata","Habra Station","Habra Mansabari","Radha Chemical More","Kalyangarh","Kachua More","Kankpul School","Kankpul More","Daulatpur","Sendanga","Pumlia Bazar","Noorpur","Shrikrishnapur","Amragachhi","Rajberia","Jaguli Anandapur","Kapileshwar","Kalyani"], "Kalyani")

# MM-3: Dakshineshwar – Duttapukur
add("MM-3", "private", ["Dakshineshwar","Kashimpur","Shibalaya","Santoshpur","Mirhati","Daripukur","Khilkapur","Kathgola","Noapara","Hela Battala More","Satabharat","Nababharati","Talikhola","Lokenath Mandir","Barbadia","Barasat State University","Jagannathpur","Kokapur","Subhash Nagar","Rangapur","Nilgunge Hat","Nilgunge","Chapuria","Debpukur","Mohanpur","Wireless Gate","Nonachandanpukur","Barrackpore Station","Barrackpore Chiria More","Talpukur","Titagarh","Khardah","Sodepur","Panihati","Kamarhati","Rathtala","Dunlop","Alambazar","Dakshineshwar"], "Duttapukur")

# MM-6/1: Jafarpur to Bagjola
add("MM-6/1", "private", ["Jafarpur","Barasat","Berachampa","Jadurhati","Bagjola"], "Bagjola")

# MN-2: Hasnabad to Lebukhali
add("MN-2", "private", ["Hasnabad","Hingalganj","Lebukhali"], "Lebukhali")

# SD-22/1: Nainan to Esplanade
add("SD-22/1", "government", ["Nainan","Kalatalahat","Sarisha More","Dostipur","Fatehpur","Shirakole","Amtala","Bishnupur","Khariberia","Bhasha 14no","Pailan","Joka Bridge","Thakurpukur","Shilpara","Sakher Bazar","Behala Chowrasta","Behala 14 No","Majherhat","Mominpore","Bhabani Bhawan","PTS","Fort William","Esplanade"], "Esplanade")

# SD-51: Gurudaspur to Mathurapur station
add("SD-51", "government", ["Gurudaspur","Milan More","Ferry Ghat","Subhasnagar","Tentultala","Kautala","Kashinagar","Krishnachandrapur","Lalpur","South Bishnupur","Mathurapur Station"], "Mathurapur Station")

# Government routes from kolbusopedia.com/bus-routes-government

# S-23: Saltlake Karunamoyee to Howrah Station
add("S-23", "government", ["Karunamoyee","Central Park","FD Park","Labony Estate","Purbachal 13no Tank","Stadium Island","AMRI Hospital","Building More","Chingrighata","Mathpukur","Science City","Topsia","Park Circus","Beck Bagan","Minto Park","Exide","Maidan","Park Street","Mayo Road","BBD Bag","GPO","Shipping Corporation","Barabazar","Howrah Station"], "Howrah Station")

# S-37A: Airport Gate 1 to Garia Bus Stand
add("S-37A", "government", ["Airport Gate 1","Kaikhali","Haldirams","Teghoria","Baguiati","Kestopur","Dumdum Park","Laketown","Sreebhumi","Ultadanga","Bengal Chemical","Mani Square","Apollo Hospital","Swabhumi","Building More","Chingrighata","Mathpukur","Science City","Uttar Panchannagram","VIP Bazar","Fortis","Ruby","Kalikapur","EM Bypass","Mukundapur","Ajaynagar","Hiland Park","Peerless Hospital","Patuli","45 Bus Stand","Garia Bus Stand"], "Garia Bus Stand")

# AC-37C: Airport Domestic Terminus to Garia Bus Stand
add("AC-37C", "government", ["Airport Terminal","Kaikhali","Haldirams","Teghoria","Baguiati","Kestopur","Dumdum Park","Laketown","Sreebhumi","Ultadanga","Bengal Chemical","Mani Square","Apollo Hospital","Swabhumi","Building More","Chingrighata","Mathpukur","Science City","Uttar Panchannagram","VIP Bazar","Fortis Hospital","Ruby","Kalikapur","EM Bypass","Mukundapur","Ajaynagar","Hiland Park","Peerless Hospital","Patuli","45 Bus Stand","Garia Bus Stand"], "Garia Bus Stand")

# S-59: Saltlake Karunamoyee to Howrah Station
add("S-59", "government", ["Karunamoyee","Bikash Bhawan","Labony Estate","GD Island","AMRI Hospital","Stadium Island","Building More","Beleghata","Sealdah","NRS Hospital","Moulali","Esplanade","GPO","Shipping Corporation","Barabazar","Howrah Station"], "Howrah Station")

# AC-59: Saltlake Karunamoyee to Howrah Station (AC version)
add("AC-59", "government", ["Karunamoyee","Bikash Bhawan","City Centre 1","Saltlake CA Block","Saltlake PNB","Ultadanga","Kankurgachi","Maniktala","Girish Park","MG Road","Barabazar","Howrah Station"], "Howrah Station")

# AC-50: Belurmath to Garia Bus Stand
add("AC-50", "government", ["Belurmath","Lalbaba College","Bally Bazar","Ballykhal","Dakshineswar","Dunlop","Mathkal","Durganagar","Airport Gate 3","Airport Gate 1","Kaikhali","Haldirams","Teghoria","Baguiati","Kestopur","Dumdum Park","Laketown","Sreebhumi","Ultadanga","Bengal Chemical","Mani Square","Apollo Hospital","Swabhumi","Saltlake Stadium","Building More","Chingrighata","Mathpukur","Science City","Uttar Panchannagram","Fortis Hospital","Ruby","Kalikapur","EM Bypass","Mukundapur","Ajaynagar","Hiland Park","Peerless Hospital","Patuli","45 Bus Stand","Garia Bus Stand"], "Garia Bus Stand")

# C-30: Rajabazar Tram Depot to Sankrail
add("C-30", "government", ["Rajabazar","Sealdah","Bowbazar","Central","Lalbazar","BBD Bag","Esplanade","Park Street","Rabindra Sadan","PTS","Hastings","Toll Tax","Bakultala","Hanskhali","Sankrail"], "Sankrail")

# C-36: Rajabazar Tram Depot to Chandmari
add("C-36", "government", ["Rajabazar","Sealdah","Bowbazar","Central","Lalbazar","BBD Bag","Esplanade","Park Street","Rabindra Sadan","PTS","Hastings","Toll Tax","Bakultala","Hanskhali","Chandmari"], "Chandmari")

# D-7: Barasat to Bagdah
add("D-7", "government", ["Barasat Chapadali","Duttapukur","Bira","Ashoknagar","Habra","Chongda More","Gaighata","Bongaon","Asharu Bazar","Helencha","Bagdah"], "Bagdah")

# D-9: Barasat to Hakimpur
add("D-9", "government", ["Barasat Chapadali","Duttapukur","Bira","Guma","Ashoknagar","Habra","Machhlandapur","Tentulia","Swarupnagar","Nirman","Bithari","Hakimpur"], "Hakimpur")

# D-26: Park Circus to Hakimpur
add("D-26", "government", ["Park Circus","Science City","Chingrighata","Karunamoyee","Sector V","Newtown Bus Terminus","Chinar Park","Airport Gate 1","Barasat","Berachampa","Baduria","Swarupnagar","Nirman","Bithari","Hakimpur"], "Hakimpur")

# D-31: Esplanade to Srinathpur
add("D-31", "government", ["Esplanade","Central Avenue","Shyambazar","Lake Town","Nagerbazar","Airport Gate 1","Madhyamgram","Barasat","Ashoknagar","Habra","Machhalandapur","Charghat","Kapileswarpur","Srinathpur"], "Srinathpur")

print(f"\nTotal routes in busdata.json: {len(data['routes'])}")

# Count how many we added
with open(BUSDATA, encoding="utf-8") as f:
    old_data = json.load(f)
added_count = len(data["routes"]) - len(old_data["routes"])
print(f"New routes added: {added_count}")

# Write back
with open(BUSDATA, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)

print("Done. busdata.json updated.")
