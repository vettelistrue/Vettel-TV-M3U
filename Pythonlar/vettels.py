import re
from fuzzywuzzy import process

def normalize_text(text):
    """Kanal adlarını standart hale getir: Harf dönüşümü + boşluk temizleme."""
    turkish_map = str.maketrans("ıİöÖüÜçÇğĞşŞ", "iIooUUcCgGsS")
    return text.translate(turkish_map).lower().replace(" ", "").strip()

def load_m3u(file_path):
    """M3U dosyasını oku ve içeriğini liste olarak döndür."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def parse_m3u(lines):
    """M3U içeriğini tvg-name'e göre ayrıştır."""
    channels = {}
    current_name = None

    for line in lines:
        if "#EXTINF" in line:
            match = re.search(r'tvg-name="([^"]+)"', line)
            if match:
                current_name = normalize_text(match.group(1))
        elif line.startswith("http"):
            if current_name:
                channels[current_name] = line.strip()

    return channels

def find_best_match(channel_name, vavoo_data):
    """En yakın eşleşmeyi bul (fuzzy matching)."""
    best_match, score = process.extractOne(channel_name, vavoo_data.keys())
    return best_match if score >= 80 else None  # %80 eşleşme şartı

def update_channels(vettecl_file, vavoo_file, output_file="vettelchannel.m3u"):
    """Vettel kanal listesini Vavoo'ya göre tvg-name bazında güncelle."""
    vettecl_data = parse_m3u(load_m3u(vettecl_file))
    vavoo_data = parse_m3u(load_m3u(vavoo_file))

    updated_lines = []
    current_name = None

    for line in load_m3u(vettecl_file):
        if "#EXTINF" in line:
            updated_lines.append(line)
            match = re.search(r'tvg-name="([^"]+)"', line)
            if match:
                current_name = normalize_text(match.group(1))
        elif line.startswith("http"):
            if current_name:
                best_match = find_best_match(current_name, vavoo_data)
                if best_match:
                    updated_lines.append(vavoo_data[best_match] + "\n")
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

if __name__ == "__main__":
    update_channels("vettelchannel.m3u", "vavoo.m3u")
    print("✅ Güncelleme tamamlandı! Yakın eşleşmeler baz alındı.")
