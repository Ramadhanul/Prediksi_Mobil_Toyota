# 🚗 Prediksi Harga Mobil Toyota dengan AI

Aplikasi web berbasis **Streamlit** yang memprediksi harga mobil Toyota berdasarkan input pengguna. Model ini dibangun menggunakan machine learning dan mengintegrasikan kemampuan LLM dari **OpenRouter.ai** untuk membantu memberikan analisis atau feedback tambahan terkait prediksi dengan menggunakan chatbot.

## 🔗 Demo Aplikasi
Akses aplikasi online di:  
> [https://prediksimobiltoyota.streamlit.app/](https://prediksimobiltoyota.streamlit.app/) 

## 🧰 Deskripsi Proyek
Aplikasi ini membantu pengguna memperkirakan harga mobil Toyota bekas berdasarkan beberapa fitur kendaraan seperti:
- Model mobil
- Tahun pembuatan
- Perkiraan Harga Bekas Kendaraan

Scraping diambil dari website [https://www.mobil123.com/](https://www.mobil123.com/) 
Prediksi harga dilakukan oleh model machine learning yang telah dilatih sebelumnya dan disimpan dalam format `.pkl`.  
Selain itu, aplikasi dapat terkoneksi dengan **OpenRouter.ai API** untuk membuat chatbot dan terkoneksi juga dengan model prediksi.

## 🛠 Fitur Utama
- Input data mobil secara interaktif
- Prediksi harga mobil berdasarkan model yang telah di training
- Chatbot dengan menggunakan API OpenRouter dan terhubung ke model prediksi
- Grafik dan data depresiasi yang bisa di filter sesuai tahun

## 🧪 Teknologi yang Digunakan
- Python
- Streamlit
- Scikit-learn
- TensorFlow / Keras
- OpenRouter API
- Pandas, NumPy, Matplotlib

## 📁 Struktur Folder
Prediksi_Mobil_Toyota/
- Pengelohan Data
-- Project_Assignment_LEGOAS.ipynb -- Termasuk Training Model
- Scraping
-- mobil123_bekas.py dan mobil123_baru.py serta hasil scraping
- app.py # Aplikasi utama
- data_mobil.csv # Dataset referensi
- model_prediksi_harga.pkl # Model ML tersimpan
- scaler_X.pkl, scaler_y.pkl # Scaler input dan output
- feature_columns.pkl # Fitur yang digunakan saat pelatihan
- requirements.txt # Daftar dependensi
- .streamlit/
-- secrets.toml # File rahasia untuk API key
- README.md # Dokumentasi proyek

## 🚀 Cara Menjalankan Aplikasi Secara Lokal

### 1. Clone Repositori
```bash
git clone https://github.com/Ramadhanul/Prediksi_Mobil_Toyota.git
cd Prediksi_Mobil_Toyota

2. Buat Virtual Environment & Install Requirements

python -m venv env
source env/bin/activate        # Linux/macOS
env\Scripts\activate           # Windows
pip install -r requirements.txt

3. Tambahkan API Key secara Aman
Buat key sendiri di [https://openrouter.ai/](https://openrouter.ai/) 
Edit
OPENROUTER_API_KEY = "Key Sendiri"

4. Jalankan Aplikasinya
streamlit run app.py
