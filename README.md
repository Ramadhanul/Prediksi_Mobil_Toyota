# 🚗 Prediksi Harga Mobil Toyota dengan AI

Aplikasi web interaktif yang memprediksi harga mobil Toyota berdasarkan input pengguna. Menggunakan model machine learning dan integrasi dengan API dari [OpenRouter.ai](https://openrouter.ai) untuk memberikan estimasi harga yang akurat.

## 🔗 Demo Aplikasi
Akses aplikasi secara langsung di:
👉 [https://your-app-name.streamlit.app](https://your-app-name.streamlit.app)

## 🧰 Fitur
- Input informasi mobil: tahun, tipe, transmisi, dll.
- Prediksi harga mobil menggunakan model machine learning.
- Integrasi dengan OpenRouter API untuk pemrosesan lanjutan.
- Antarmuka pengguna interaktif dengan Streamlit.

## 🛠 Teknologi yang Digunakan
- Python
- Streamlit
- Scikit-learn
- TensorFlow/Keras
- OpenRouter API
- Pandas
- NumPy

## 📁 Struktur Proyek
Prediksi_Mobil_Toyota/
├── app.py
├── data_mobil.csv
├── model_prediksi_harga.pkl
├── requirements.txt
├── .streamlit/
│ └── secrets.toml
└── README.md

bash
Salin
Edit

## 🚀 Panduan Instalasi dan Menjalankan Aplikasi

1. **Clone repositori:**
   ```bash
   git clone https://github.com/Ramadhanul/Prediksi_Mobil_Toyota.git
   cd Prediksi_Mobil_Toyota
Buat environment dan install dependensi:

bash
Salin
Edit
python -m venv env
source env/bin/activate  # Untuk Linux/Mac
env\Scripts\activate     # Untuk Windows
pip install -r requirements.txt
Tambahkan API key di .streamlit/secrets.toml:

toml
Salin
Edit
OPENROUTER_API_KEY = "sk-or-v1-xxxxxxxxxxxxxxxx"
Jalankan aplikasi:

bash
Salin
Edit
streamlit run app.py
🔐 Keamanan API Key
Jangan pernah menuliskan API key langsung dalam kode. Gunakan environment variable atau st.secrets untuk menyimpannya secara aman, terutama saat menggunakan platform seperti Streamlit Cloud.
