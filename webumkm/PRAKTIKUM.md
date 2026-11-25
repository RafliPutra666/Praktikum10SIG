# Praktikum WebGIS dengan Django — Latihan Mandiri 1 & 2

Mata kuliah Sistem Informasi Geografis — STT-NF (Dr. Sirojul Munir, S.Si., M.Kom.)

| Latihan | App / URL | Hasil |
|---|---|---|
| Mandiri 1 | `petaindonesia` → `/petadua/` | Peta Jabodetabek (5 marker kota + panel "Pilih kota") |
| Mandiri 2 | `gempabumi` → `/gempabumi/` | Peta 15 gempa terkini BMKG (M 5.0+) |

---

## 0. Prasyarat (dari materi Part II)

Latihan ini melanjutkan project `webumkm` dan app `petaindonesia` yang sudah dibuat di materi sebelumnya. Jika belum ada, buat dulu:

```bash
python -m venv webgis
cd webgis
# aktifkan venv:
#   Windows : Scripts\activate
#   Linux/Mac: source bin/activate
python -m pip install django

django-admin startproject webumkm
cd webumkm
python manage.py startapp petaindonesia
```

Pastikan kondisi berikut sudah terpenuhi:

1. `'petaindonesia'` ada di `INSTALLED_APPS` pada `webumkm/settings.py`.
2. `webumkm/settings.py` memiliki pengaturan referrer (agar tile OpenStreetMap tidak diblokir):
   ```python
   SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
   ```
3. `webumkm/urls.py` meng-include URL app:
   ```python
   from django.contrib import admin
   from django.urls import path, include

   urlpatterns = [
       path('', include('petaindonesia.urls')),
       path('admin/', admin.site.urls),
   ]
   ```
4. Struktur template sudah ada: `petaindonesia/templates/petaindonesia/`.
5. `petaindonesia/view_peta.py` dan `petaindonesia/urls.py` sudah berisi view `petasatu` (contoh dari dosen, kode `petasatu.html` ada di GitHub rojulman/leaflet — `peta-indonesia.html`).

Konsep alur yang dipakai: **User → URL (dispatcher) → View (proses logika) → Template (HTML) → HTTP Response**.

---

# LATIHAN MANDIRI 1 — Peta Jabodetabek (`/petadua/`)

**Target:** peta Leaflet + OpenStreetMap yang menampilkan 5 kota (Jakarta, Bogor, Depok, Tangerang, Bekasi) dengan marker berlabel, panel "Pilih kota" untuk zoom ke kota, dan tombol "Tampilkan semua".

## Langkah 1 — Buat view baru `petadua`

File: `webumkm/petaindonesia/view_peta.py` (tambahkan di bawah fungsi `petasatu`)

```python
from django.shortcuts import render
from django.http import HttpResponse


def petasatu(request):
    return render(request, 'petaindonesia/petasatu.html')


def petadua(request):
    return render(request, 'petaindonesia/petadua.html')
```

## Langkah 2 — Buat template HTML

File: `webumkm/petaindonesia/templates/petaindonesia/petadua.html`

```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Peta Jabodetabek</title>

  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <style>
    html, body { height: 100%; margin: 0; font-family: Arial, sans-serif; }
    header {
      background: #0b4a8b; color: #fff; padding: 12px 16px;
      font-weight: bold; font-size: 18px;
    }
    #map { height: calc(100% - 46px); width: 100%; }

    /* Panel pilih kota */
    .panel {
      background: #fff; padding: 10px; border-radius: 8px;
      box-shadow: 0 1px 6px rgba(0,0,0,.3); min-width: 150px;
    }
    .panel h4 { margin: 0 0 8px; font-size: 14px; }
    .panel button {
      display: block; width: 100%; margin-bottom: 4px; padding: 6px 8px;
      text-align: left; border: 1px solid #ccc; background: #f7f7f7;
      border-radius: 4px; cursor: pointer;
    }
    .panel button:hover { background: #e6f0fb; }
  </style>
</head>
<body>
  <header>Peta Jabodetabek: Jakarta, Bogor, Depok, Tangerang, Bekasi</header>
  <div id="map"></div>

  <script>
    // Data kota [nama, latitude, longitude]
    const kota = [
      { nama: "Jakarta",   lat: -6.2088, lng: 106.8456 },
      { nama: "Bogor",     lat: -6.5971, lng: 106.8060 },
      { nama: "Depok",     lat: -6.4025, lng: 106.7942 },
      { nama: "Tangerang", lat: -6.1783, lng: 106.6319 },
      { nama: "Bekasi",    lat: -6.2383, lng: 106.9756 }
    ];

    // Peta + basemap
    const map = L.map('map').setView([-6.35, 106.85], 10);

    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const satelit = L.tileLayer(
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
      attribution: 'Tiles &copy; Esri'
    });

    // Kontrol layer + skala
    L.control.layers({ "OpenStreetMap": osm, "Satelit": satelit }).addTo(map);
    L.control.scale({ metric: true, imperial: false }).addTo(map);

    // Marker + label permanen
    const markers = {};
    kota.forEach(k => {
      const m = L.marker([k.lat, k.lng]).addTo(map);
      m.bindTooltip(k.nama, { permanent: true, direction: 'top', offset: [0, -20] });
      m.bindPopup(`<b>${k.nama}</b><br>${k.lat}, ${k.lng}`);
      markers[k.nama] = m;
    });

    // Panel "Pilih kota"
    const panel = L.control({ position: 'topright' });
    panel.onAdd = function () {
      const div = L.DomUtil.create('div', 'panel');
      let html = '<h4>Pilih kota</h4>';
      kota.forEach(k => { html += `<button data-kota="${k.nama}">${k.nama}</button>`; });
      html += '<button data-kota="__all__">Tampilkan semua</button>';
      div.innerHTML = html;
      L.DomEvent.disableClickPropagation(div);
      return div;
    };
    panel.addTo(map);

    document.querySelectorAll('.panel button').forEach(btn => {
      btn.addEventListener('click', () => {
        const nama = btn.dataset.kota;
        if (nama === '__all__') {
          map.fitBounds(L.featureGroup(Object.values(markers)).getBounds().pad(0.2));
        } else {
          map.setView(markers[nama].getLatLng(), 13);
          markers[nama].openPopup();
        }
      });
    });

    // Tampilan awal: semua kota
    map.fitBounds(L.featureGroup(Object.values(markers)).getBounds().pad(0.2));
  </script>
</body>
</html>
```

## Langkah 3 — Daftarkan URL di app `petaindonesia`

File: `webumkm/petaindonesia/urls.py`

```python
from django.urls import path
from . import views, view_peta

urlpatterns = [
    path('welcome/', views.welcome, name='welcome'),
    path('petasatu/', view_peta.petasatu, name='petasatu'),
    path('petadua/', view_peta.petadua, name='petadua'),
]
```

## Langkah 4 — Jalankan server

```bash
python manage.py runserver
```

## Langkah 5 — Akses URL

Buka **http://localhost:8000/petadua/**

**Checklist hasil:**
- [ ] Judul biru "Peta Jabodetabek: Jakarta, Bogor, Depok, Tangerang, Bekasi"
- [ ] 5 marker dengan label nama kota
- [ ] Panel "Pilih kota" di kanan atas; klik nama kota → zoom ke kota tersebut
- [ ] Tombol "Tampilkan semua" mengembalikan tampilan 5 kota
- [ ] Kontrol layer (OSM/Satelit) dan skala (mis. `10 km`) tampil

---

# LATIHAN MANDIRI 2 — Peta Gempa Terkini BMKG (`/gempabumi/`)

**Target:** app baru `gempabumi` yang mengambil 15 data gempa terbaru (M 5.0+) dari BMKG, menampilkannya sebagai daftar di sisi kiri dan 15 marker di peta Indonesia. Warna marker = kedalaman, ukuran lingkaran = magnitudo, klik marker = popup detail.

## Langkah 1 — Buat app baru `gempabumi`

```bash
python manage.py startapp gempabumi
```

Daftarkan di `webumkm/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'petaindonesia',
    'gempabumi',
]
```

## Langkah 2 — Pelajari sumber data BMKG

- Halaman data terbuka: https://data.bmkg.go.id/gempabumi/
- Endpoint JSON (gempa M 5.0+): https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json

Buka URL JSON di browser dan perhatikan strukturnya:

```json
{
  "Infogempa": {
    "gempa": [
      {
        "Tanggal": "17 Nov 2026",
        "Jam": "04:11:20 WIB",
        "DateTime": "2026-11-16T21:11:20+00:00",
        "Coordinates": "-3.50,128.20",
        "Lintang": "3.50 LS",
        "Bujur": "128.20 BT",
        "Magnitude": "7.1",
        "Kedalaman": "115 km",
        "Wilayah": "130 km BaratDaya MALUKUTENGGARA",
        "Potensi": "..."
      }
    ]
  }
}
```

Field yang dipakai: `Tanggal`, `Jam`, `Coordinates` (format `"lat,lon"`), `Magnitude`, `Kedalaman`, `Wilayah`.

> Data diambil **di sisi server (Django)**, bukan langsung dari JavaScript browser, supaya tidak terkena masalah CORS.

## Langkah 3 — Atur `urls.py` app `gempabumi`

Buat file baru `webumkm/gempabumi/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.gempaterkini, name='gempaterkini'),
]
```

Hubungkan ke root URL — `webumkm/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('petaindonesia.urls')),
    path('gempabumi/', include('gempabumi.urls')),
    path('admin/', admin.site.urls),
]
```

## Langkah 4 — Ambil 15 data gempa terakhir (View)

File: `webumkm/gempabumi/views.py`

```python
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
        req = urllib.request.Request(BMKG_URL, headers={"User-Agent": "Mozilla/5.0"})
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
```

## Langkah 5 — Buat peta gempa (Template)

Buat folder `webumkm/gempabumi/templates/gempabumi/` lalu file `gempabumi.html`:

```html
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Gempa Terkini BMKG</title>

  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <style>
    html, body { height: 100%; margin: 0; font-family: Arial, sans-serif; }
    header {
      background: #0b4a8b; color: #fff; padding: 10px 16px;
      display: flex; justify-content: space-between; align-items: center;
    }
    header h1 { margin: 0; font-size: 18px; }
    header small { opacity: .85; }
    header button {
      background: #fff; border: 0; border-radius: 4px;
      padding: 6px 12px; cursor: pointer;
    }
    .wrap { display: flex; height: calc(100% - 56px); }
    #list { width: 300px; overflow-y: auto; border-right: 1px solid #ddd; }
    #map { flex: 1; }

    .item { padding: 10px 12px; border-bottom: 1px solid #eee; cursor: pointer; }
    .item:hover { background: #f0f6ff; }
    .item .mag {
      display: inline-block; color: #fff; font-weight: bold;
      padding: 2px 8px; border-radius: 4px; margin-right: 6px;
    }
    .item .wil { font-weight: bold; font-size: 13px; }
    .item .meta { font-size: 12px; color: #666; margin-top: 4px; }
    .err { background: #fdecea; color: #b71c1c; padding: 12px; }

    .legend {
      background: #fff; padding: 10px; border-radius: 8px;
      box-shadow: 0 1px 6px rgba(0,0,0,.3); font-size: 12px; line-height: 1.6;
    }
    .legend i {
      display: inline-block; width: 12px; height: 12px;
      border-radius: 50%; margin-right: 6px;
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>{{ jumlah }} Gempa Terkini (M 5.0+)</h1>
      <small>{{ jumlah }} gempa M 5.0+ terakhir · diperbarui {{ diperbarui }}</small>
    </div>
    <button onclick="location.reload()">Muat ulang</button>
  </header>

  <div class="wrap">
    <div id="list">
      {% if error %}<div class="err">{{ error }}</div>{% endif %}
    </div>
    <div id="map"></div>
  </div>

  {{ gempa|json_script:"gempa-data" }}

  <script>
    const data = JSON.parse(document.getElementById('gempa-data').textContent);

    // Warna berdasarkan kedalaman (km)
    function warna(km) {
      if (km < 70)   return '#e53935'; // dangkal  - merah
      if (km <= 300) return '#fb8c00'; // menengah - oranye
      return '#43a047';                // dalam    - hijau
    }
    // Radius lingkaran berdasarkan magnitudo
    const radius = mag => Math.max(5, (mag - 3) * 4);

    const map = L.map('map').setView([-2.5, 118], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Data gempa: <a href="https://www.bmkg.go.id">BMKG</a>'
    }).addTo(map);

    L.control.scale({ metric: true, imperial: false }).addTo(map);

    // Legenda
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = () => {
      const div = L.DomUtil.create('div', 'legend');
      div.innerHTML = `
        <b>Kedalaman</b><br>
        <i style="background:#e53935"></i>Dangkal (&lt; 70 km)<br>
        <i style="background:#fb8c00"></i>Menengah (70–300 km)<br>
        <i style="background:#43a047"></i>Dalam (&gt; 300 km)<br>
        <small>Ukuran lingkaran = magnitudo</small>`;
      return div;
    };
    legend.addTo(map);

    // Marker + daftar
    const list = document.getElementById('list');
    const bounds = [];

    data.forEach(g => {
      const c = warna(g.kedalaman);

      const marker = L.circleMarker([g.lat, g.lng], {
        radius: radius(g.magnitude),
        color: '#333', weight: 1, fillColor: c, fillOpacity: 0.8
      }).addTo(map);

      marker.bindPopup(`
        <b>M ${g.magnitude.toFixed(1)}</b> — ${g.wilayah}<br>
        ${g.tanggal}, ${g.jam}<br>
        Kedalaman: ${g.kedalaman} km<br>
        Koordinat: ${g.lat}, ${g.lng}`);

      bounds.push([g.lat, g.lng]);

      const item = document.createElement('div');
      item.className = 'item';
      item.innerHTML = `
        <span class="mag" style="background:${c}">${g.magnitude.toFixed(1)}</span>
        <span class="wil">${g.wilayah}</span>
        <div class="meta">${g.tanggal} ${g.jam} · ${g.kedalaman} km</div>`;
      item.addEventListener('click', () => {
        map.setView([g.lat, g.lng], 8);
        marker.openPopup();
      });
      list.appendChild(item);
    });

    if (bounds.length) map.fitBounds(bounds, { padding: [40, 40] });
  </script>
</body>
</html>
```

## Langkah 6 — Akses aplikasi

```bash
python manage.py runserver
```

Buka **http://localhost:8000/gempabumi/**

**Checklist hasil:**
- [ ] Header "15 Gempa Terkini (M 5.0+)" + waktu diperbarui + tombol "Muat ulang"
- [ ] Daftar 15 gempa di kiri (badge magnitudo, wilayah, tanggal/jam, kedalaman)
- [ ] 15 marker lingkaran di peta Indonesia; klik marker → popup detail
- [ ] Legenda kedalaman (merah/oranye/hijau) + keterangan ukuran = magnitudo
- [ ] Atribusi `Leaflet | © OpenStreetMap contributors | Data gempa: BMKG`

---

## Troubleshooting

| Masalah | Penyebab / solusi |
|---|---|
| `TemplateDoesNotExist` | Folder harus persis `app/templates/app/file.html`, dan app sudah ada di `INSTALLED_APPS`. |
| Halaman 404 | URL belum di-include di `webumkm/urls.py`, atau lupa akhiran `/`. |
| Tile peta kosong / "Referer required" | Cek `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"` di `settings.py`. |
| `Gagal mengambil data BMKG` | Cek koneksi internet / buka URL JSON langsung di browser. Server BMKG kadang lambat — klik "Muat ulang". |
| `ModuleNotFoundError: zoneinfo/tzdata` (Windows) | `python -m pip install tzdata` |
| Perubahan template tidak tampil | Hard refresh (`Ctrl+Shift+R`); development server otomatis reload file `.py`. |

## Struktur akhir project

```
webumkm/
├── manage.py
├── webumkm/
│   ├── settings.py
│   └── urls.py
├── petaindonesia/
│   ├── views.py
│   ├── view_peta.py
│   ├── urls.py
│   └── templates/petaindonesia/
│       ├── petasatu.html
│       └── petadua.html          ← Mandiri 1
└── gempabumi/                    ← Mandiri 2
    ├── views.py
    ├── urls.py
    └── templates/gempabumi/
        └── gempabumi.html
```