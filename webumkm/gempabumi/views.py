import json
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

from django.shortcuts import render

BMKG_URL = "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json"
JUMLAH = 15


def gempaterkini(request):
    gempa = []
    error = None

    try:
        req = urllib.request.Request(BMKG_URL, headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
            ),
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)

        for g in data["Infogempa"]["gempa"][:JUMLAH]:
            lat, lng = (float(x) for x in g["Coordinates"].split(","))
            gempa.append({
                "tanggal": g["Tanggal"],
                "jam": g["Jam"],
                "lat": lat,
                "lng": lng,
                "magnitude": float(g["Magnitude"]),
                "kedalaman": int(g["Kedalaman"].split()[0]),  # "115 km" -> 115
                "wilayah": g["Wilayah"],
            })
    except Exception as e:
        error = f"Gagal mengambil data BMKG: {e}"

    context = {
        "gempa": gempa,
        "jumlah": len(gempa),
        "error": error,
        "diperbarui": datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%H.%M.%S"),
    }
    return render(request, "gempabumi/gempabumi.html", context)
