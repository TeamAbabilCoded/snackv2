# Auto Video Cutter Pro v2.0

Auto Video Cutter Pro adalah aplikasi CLI berbasis Python untuk memotong
video menjadi beberapa bagian secara otomatis dengan tampilan vertikal
**9:16**.

## Fitur

-   Potong video otomatis berdasarkan durasi minimum & maksimum.
-   Output 720×1280 (9:16).
-   Video utama 720×720 di tengah.
-   Background berwarna dari `config.py`.
-   Judul otomatis (word wrap).
-   Label PART otomatis.
-   Watermark PNG transparan.
-   Logo tambahan di bagian atas (opsional).
-   Progress bar FFmpeg.
-   Informasi video (resolusi, FPS, durasi, ukuran).
-   Embed thumbnail ke MP4 (opsional).
-   Pengaturan melalui `config.py`.
-   Menu pengaturan interaktif melalui `main.py`.

## Struktur Folder

``` text
project/
│
├── assets/
│   ├── font.ttf
│   ├── logo.png
│   ├── logo_top.jpg
│   └── thumbnail.jpg
│
├── video/
├── cut/
├── cutter.py
├── main.py
├── config.py
└── README.md
```

## Instalasi

Pastikan sudah terpasang:

-   Python 3.10+
-   FFmpeg
-   FFprobe

Install dependensi:

``` bash
pip install -U pip
```

## Menjalankan

Masukkan video ke folder:

``` text
video/
```

Lalu jalankan:

``` bash
python main.py
```

## Menu

1.  Atur ulang video
2.  Gunakan setting yang tersimpan
3.  Lihat setting saat ini
4.  Reset ke default
5.  Keluar

## Pengaturan yang Bisa Diubah

-   MIN_DURATION
-   MAX_DURATION
-   FONT_SIZE
-   FONT_SIZE_PART
-   WM_SIZE
-   BG_COLOR
-   FONT_COLOR
-   PART_FONT_COLOR
-   BORDER_COLOR
-   SHADOW_COLOR

## File Konfigurasi

Semua pengaturan disimpan di:

``` text
config.py
```

## Output

Semua hasil video disimpan ke:

``` text
cut/
```

Nama file:

``` text
cut_1_namafile.mp4
cut_2_namafile.mp4
...
```

## Catatan

-   Thumbnail embedded tidak selalu digunakan oleh semua aplikasi
    (misalnya Telegram dapat membuat thumbnail sendiri).
-   Pastikan font dan aset tersedia di folder `assets`.

## Lisensi

Untuk penggunaan pribadi atau pengembangan sesuai kebutuhan.
