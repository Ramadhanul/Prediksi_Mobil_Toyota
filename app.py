import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import requests
import json
import re
from fuzzywuzzy import process

# Load model dan scaler
model = joblib.load('model_prediksi_harga.pkl')
scaler_X = joblib.load('scaler_X.pkl')
scaler_y = joblib.load('scaler_y.pkl')
feature_columns = joblib.load('feature_columns.pkl')
nama_mobil_list = joblib.load('nama_mobil_list.pkl')
df_depresiasi_tahun = joblib.load('df_depresiasi_tahun.pkl')
df_bekas = joblib.load('df_bekas.pkl')
df_baru = joblib.load('df_baru.pkl')

# ============ TAMPILAN HEADER ============ #
st.set_page_config(page_title="Prediksi Harga Mobil Bekas", layout="wide", page_icon="🚗")
st.markdown("<h1 style='text-align: center; color: navy;'>🚗 Prediksi Harga Mobil Bekas Toyota</h1> <p style='text-align: center; color: gray;'>Ramadhanul Husna A.M</p>", unsafe_allow_html=True )

st.markdown("---")
st.markdown("""
    📊 **Prediksi Harga Mobil Bekas Toyota** untuk memprediksi harga pasar mobil bekas berdasarkan data harga baru, umur mobil, dan merk mobil. 
    Anda hanya perlu mengisi beberapa informasi mengenai mobil Anda dan akan diberikan estimasi harga bekas dari mobil tersebut.
""")

# ============ INPUT USER ============ #
st.subheader("🔍 Input Data Mobil")

col1, col2, col3 = st.columns(3)

with col1:
    nama_mobil = st.selectbox('Pilih Nama Mobil', sorted(nama_mobil_list))

with col2:
    tahun = st.number_input('Tahun Mobil (2005-2025)', min_value=2005, max_value=2025, value=2015)

with col3:
    harga_baru_str = st.text_input("Masukkan Harga Baru (Rp)", "490.000.000")

try:
    harga_baru = int(harga_baru_str.replace(".", "").replace(",", ""))
except ValueError:
    st.error("❌ Format harga tidak valid. Gunakan titik/koma sebagai pemisah ribuan.")
    harga_baru = None

# ============ PREDIKSI ============ #
if st.button('🔮 Prediksi Harga Bekas'):
    if not nama_mobil or not tahun or harga_baru is None:
        st.error("❗ Semua kolom wajib diisi.")
    else:
        umur = 2025 - tahun
        input_df = pd.DataFrame({
            'Mobil_Bekas': [nama_mobil.strip()],
            'Tahun': [tahun],
            'Harga_Baru': [harga_baru],
            'Umur_Mobil': [umur]
        })

        input_df = pd.get_dummies(input_df, columns=['Mobil_Bekas'], drop_first=False)
        input_df = input_df.reindex(columns=feature_columns, fill_value=0)

        input_scaled = scaler_X.transform(input_df)
        pred_scaled = model.predict(input_scaled)
        pred_rp = scaler_y.inverse_transform(pred_scaled)

        if pred_rp[0][0] > harga_baru:
            st.warning( f"⚠️ **Perhatian! Harga Baru Tidak Masuk Akal!**\n\n"
                f"Harga baru yang Anda masukkan **Rp {harga_baru:,.2f}** lebih rendah dari harga bekas yang wajar.\n"
                f"Misalnya, harga bekas mobil {nama_mobil} tahun {tahun} pada data kami adalah sekitar **Rp 160.000.000** namun Anda masukkan dengan harga **Rp 100.000.000**.\n\n"
                "Harap pastikan harga baru yang dimasukkan sesuai dengan kisaran harga pasar mobil tersebut.\n"
                "Harga baru yang terlalu rendah dapat menyebabkan prediksi yang tidak realistis.")
        else:
            st.success(f"💰 **Prediksi Harga Bekas: Rp {pred_rp[0][0]:,.2f}**")

st.markdown("---")

# ============ BUTTON UNTUK TAMPILKAN VISUALISASI DAN TENTANG ============ #
import streamlit as st

# Menggunakan st.session_state untuk menyimpan status tab
if 'tab' not in st.session_state:
    st.session_state.tab = 'Visualisasi'

# Atur layout dengan tiga kolom berukuran kecil dan merapat
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button('📊 Visualisasi Data', use_container_width=True):
        st.session_state.tab = 'Visualisasi'

with col2:
    if st.button('ℹ️ Tentang Data dan Model', use_container_width=True):
        st.session_state.tab = 'Tentang'

with col3:
    if st.button('🤖 Chatbot', use_container_width=True):
        st.session_state.tab = 'Chatbot'

st.markdown("---")

# Menampilkan konten berdasarkan tab yang dipilih
if st.session_state.tab == 'Visualisasi':
    # ============ VISUALISASI DEPRESIASI ============ #
    st.header("📉 Visualisasi Depresiasi Harga Mobil")
    st.markdown("""
        Grafik di bawah ini menunjukkan bagaimana harga mobil bekas mengalami depresiasi dari tahun ke tahun.
        Anda dapat menggunakan slider untuk memfilter rentang tahun dan melihat perbedaan yang terjadi pada harga mobil bekas.
    """)

    # Sidebar filter
    st.sidebar.header("🧮 Filter Rentang Tahun")
    tahun_min = int(df_depresiasi_tahun['Tahun'].min())
    tahun_max = int(df_depresiasi_tahun['Tahun'].max())
    range_tahun = st.sidebar.slider("Rentang Tahun", min_value=tahun_min, max_value=tahun_max, value=(2005, 2025), step=1)

    df_filtered = df_depresiasi_tahun[
        (df_depresiasi_tahun['Tahun'] >= range_tahun[0]) & 
        (df_depresiasi_tahun['Tahun'] <= range_tahun[1])
    ].copy()
    df_filtered_reversed = df_filtered[::-1].reset_index(drop=True)

    # Fungsi umum plotting untuk diagram garis dengan nilai pada setiap titik dan penyesuaian otomatis posisi nilai
    def plot_depresiasi(df, col, title, ylabel, color='blue', value_color='black'):
        fig, ax = plt.subplots(figsize=(10, 5))

        # Plot garis dengan penajaman warna garis
        ax.plot(df['Tahun'], df[col], marker='o', color=color, linestyle='-', linewidth=2, markersize=6, label=col)

        # Menambahkan nilai pada setiap titik di sepanjang garis dengan jarak yang cukup antara titik dan nilai
        for i, val in enumerate(df[col]):
            if i > 0 and abs(df[col].iloc[i] - df[col].iloc[i-1]) < 5:
                ax.annotate(f'{val:.2f}', (df['Tahun'].iloc[i], val), textcoords="offset points", xytext=(0, -12), ha='center', fontsize=10, color=value_color, fontweight='bold')
            else:
                ax.annotate(f'{val:.2f}', (df['Tahun'].iloc[i], val), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=10, color=value_color, fontweight='bold')

        # Menambahkan judul, label dan grid
        ax.set_title(title, fontsize=16, fontweight='bold', color='navy')
        ax.set_xlabel('Tahun', fontsize=14, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=14, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.7)

        # Menambahkan sumbu X yang terbalik dan label tahun secara jelas
        ax.set_xticks(df['Tahun'])
        ax.set_xticklabels([str(i) for i in df['Tahun']], rotation=45, ha='right', fontsize=12)
        ax.invert_xaxis()  # Membalikkan sumbu X agar dimulai dari 2025 ke 2005

        # Menambahkan garis grid horizontal untuk keterbacaan yang lebih baik
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)

        ax.legend(fontsize=12)
        plt.tight_layout()
        return fig

    # Tiga grafik yang ditampilkan dalam bentuk garis dengan desain profesional dan nilai di setiap titik
    st.subheader("📊 Grafik Depresiasi")
    st.markdown("""
        Depresiasi adalah penurunan nilai mobil seiring berjalannya waktu. Di bawah ini kami tunjukkan grafik depresiasi mobil bekas, 
        perbedaan nilai depresiasi tiap tahun, dan peningkatan depresiasi tahunan yang terjadi berdasarkan rentang tahun yang Anda pilih.
    """)

    # Grafik pertama
    st.pyplot(plot_depresiasi(df_filtered_reversed, 'Depresiasi_%', 'Depresiasi (%) per Tahun', 'Depresiasi (%)', color='royalblue', value_color='darkblue'))
    with st.expander("🔎 Deskripsi Grafik Depresiasi (%) per Tahun"):
        st.write("""
            Grafik ini menunjukkan bagaimana persentase depresiasi harga mobil bekas per tahun. Depresiasi harga adalah penurunan nilai mobil seiring bertambahnya umur.
            Pada grafik ini, Anda dapat melihat tren depresiasi mobil bekas dari tahun ke tahun berdasarkan data yang telah dikumpulkan. 
            Depresiasi akan semakin naik seiring meningkatnya umur kendaraan.Disini dapat dilihat juga pada tahun yang sama mobil bisa mengalami depresiasi sekitar 3% dan pada satu tahun pertama depresiasi bisa sekitar 16 %.
        """)

    # Grafik kedua
    st.pyplot(plot_depresiasi(df_filtered_reversed, 'Perbedaan_Depresiasi', 'Perbedaan Nilai Depresiasi per Tahun', 'Nilai', color='mediumseagreen', value_color='darkgreen'))
    with st.expander("🔎 Deskripsi Grafik Perbedaan Nilai Depresiasi per Tahun"):
        st.write("""
            Grafik ini menunjukkan selisih nilai depresiasi setiap tahun. Perbedaan nilai ini membantu Anda untuk memahami lebih dalam seberapa cepat nilai mobil bekas menurun 
            dari tahun ke tahun. Perhitungannya disini contohnya yaitu pada 2024 yaitu menunjukkan berapa perbedaan depresiasi dari tahun 2025 dan 2024. Disini dapat dilihat terjadi peningkatan depresiasi sekitar 12 untuk tahun pertama.
        """)

    # Grafik ketiga
    st.pyplot(plot_depresiasi(df_filtered_reversed, 'Peningkatan_Depresiasi_%', 'Peningkatan Depresiasi (%) per Tahun', 'Peningkatan (%)', color='orangered', value_color='darkred'))
    with st.expander("🔎 Deskripsi Grafik Peningkatan Depresiasi (%) per Tahun"):
        st.write("""
            Grafik ini menampilkan persentase peningkatan depresiasi per tahun. Ini berguna untuk mengetahui tren depresiasi dari tahun ke tahun.
            Peningkatan depresiasi menunjukkan seberapa besar perubahan dalam kecepatan penurunan harga mobil pada setiap tahunnya. Disini dapat dilihat bahwa pada tahun pertama akan terjadi peningkatan depresiasi sebanyak 76% dari depresiasi awal.
        """)

    # ============ TABEL DAN STATISTIK ============ #
    st.subheader("📄 Tabel Depresiasi Harga")
    st.markdown("""
        Tabel di bawah ini menunjukkan data depresiasi harga mobil bekas berdasarkan tahun. Anda dapat memfilter rentang tahun dan melihat 
        bagaimana harga mobil bekas berkurang seiring bertambahnya usia mobil.
    """)
    st.dataframe(df_filtered[['Tahun', 'Depresiasi_%', 'Perbedaan_Depresiasi', 'Peningkatan_Depresiasi_%']])

    rata2_depresiasi = df_filtered['Depresiasi_%'].mean()
    rata2_perbedaan = df_filtered['Perbedaan_Depresiasi'].mean()
    rata2_peningkatan = df_filtered['Peningkatan_Depresiasi_%'].mean()

    st.markdown("### 📌 Rata-Rata (Berdasarkan Rentang Tahun)")
    st.success(f"📉 **Depresiasi Rata-rata Selama Rentang Tahun:** {rata2_depresiasi:.2f}%")
    st.info(f"💸 **Rata-rata Perbedaan Depresiasi Tiap Tahun:** {rata2_perbedaan:,.2f}")
    st.warning(f"📈 **Rata-rata Peningkatan Depresiasi Tiap Tahun:** {rata2_peningkatan:.2f}%")

elif st.session_state.tab == 'Tentang':
    # Menampilkan konten Tentang Data dan Model
    st.header("ℹ️ Tentang Data dan Model")
    st.markdown("""
        Di bagian ini, kami akan memberikan penjelasan tentang dataset yang digunakan dan model yang diterapkan untuk menganalisis depresiasi harga mobil.
        Data diambil dari scraping data di mobil123.com dengan rincian sebagai berikut:
        - Data Mobil Bekas Toyota dari tahun 2005 hingga 2025 dengan jumlah data **26,267**.
        - Data Mobil Baru Toyota dari tahun 2021 hingga 2025 dengan jumlah data **4,981**.
    """)

    # Persebaran Data Mobil Bekas berdasarkan Tahun
    st.subheader("📊 Persebaran Data Mobil Bekas berdasarkan Tahun")
    st.markdown("""
        Grafik berikut menunjukkan persebaran data mobil bekas Toyota berdasarkan tahun. 
        Anda dapat melihat bagaimana data mobil bekas tersebar dari tahun 2005 hingga 2025.
    """)

    # Grafik Persebaran Data Mobil Bekas
    plt.figure(figsize=(10,5))
    df_bekas['Tahun'].value_counts().sort_index().plot(kind='bar', color='cornflowerblue')
    plt.title('Persebaran Data Mobil Bekas berdasarkan Tahun')
    plt.xlabel('Tahun')
    plt.ylabel('Jumlah Mobil')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt)

    # Persebaran Data Mobil Baru berdasarkan Tahun
    st.subheader("📊 Persebaran Data Mobil Baru berdasarkan Tahun")
    st.markdown("""
        Grafik berikut menunjukkan persebaran data mobil baru Toyota berdasarkan tahun. 
        Anda dapat melihat bagaimana data mobil baru tersebar dari tahun 2021 hingga 2025.
    """)

    # Grafik Persebaran Data Mobil Baru
    plt.figure(figsize=(10,5))
    df_baru['Tahun'].value_counts().sort_index().plot(kind='bar', color='cornflowerblue')
    plt.title('Persebaran Data Mobil Baru berdasarkan Tahun')
    plt.xlabel('Tahun')
    plt.ylabel('Jumlah Mobil')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    st.pyplot(plt)

    st.markdown("""
    ### 🧠 Persiapan Data untuk Model

    - **Fitur (Input)**: Umur mobil, nama mobil (one-hot encoding), harga baru.
    - **Target (Output)**: Harga bekas mobil.
    - **Pembagian data**:
        - X_train shape: (21.236, 310)
        - X_test shape : (5.309, 310)
        - y_train shape: (21.236, 1)
        - y_test shape : (5.309, 1)
    """)

    st.markdown("""
    ### 🤖 Arsitektur Model Neural Network

    ```python
    model = Sequential()
    model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')
    model.summary()
    ```

    """)

    st.markdown("""
    ### 📈 Evaluasi Model

    - Akurasi model diukur menggunakan MAPE (Mean Absolute Percentage Error).
    - Hasil: **MAPE = 5.82%** – menunjukkan model cukup akurat dalam memprediksi harga mobil bekas.

    """)

    st.markdown("""
    ### 🚀 Deployment Model

    - Model dilatih dan disimpan (.pkl)
    - Encoder nama mobil disimpan (.pkl)
    - Dibuat aplikasi interaktif dengan Streamlit
    - File requirements.txt disiapkan untuk environment deployment
    """)

    st.markdown("""
    ### ⚠️ Tantangan & Keterbatasan

    Walaupun model ini telah menunjukkan performa cukup baik, terdapat beberapa tantangan dan keterbatasan dalam proyek ini:

    1. **Data Mobil Baru Terbatas (2021–2025)**

    Perhitungan depresiasi untuk mobil dari tahun 2005 hingga 2020 menggunakan estimasi harga baru berdasarkan data tahun 2021–2025. Estimasi ini dilakukan dengan rumus:  
    `harga_baru = harga_bekas / ((1 - depresiasi_rata2) ** umur)`  
    Pendekatan ini tentu tidak setepat jika data harga baru langsung tersedia, sehingga bisa berdampak pada akurasi perhitungan depresiasi.

    2. **Persebaran Data Tidak Merata**

    Jumlah data mobil tidak seimbang tiap tahun. Tahun-tahun tertentu mendominasi data sehingga model bisa bias terhadap tahun-tahun tersebut.

    3. **Terbatas pada Merek Toyota**

    Dataset hanya mencakup mobil merek Toyota. Model tidak dapat digeneralisasikan ke merek lain tanpa pelatihan ulang menggunakan data tambahan.

    4. **Kondisi Mobil Tidak Dipertimbangkan**

    Harga mobil bekas sangat dipengaruhi oleh kondisi kendaraan, seperti kilometer tempuh, riwayat servis, dan kondisi fisik. Namun, variabel-variabel ini belum tersedia dalam dataset.

    5. **Depresiasi Dipengaruhi Banyak Faktor**

    Selain umur, depresiasi mobil juga dipengaruhi oleh inflasi, tren pasar, regulasi pemerintah, dan teknologi baru. Model ini belum mempertimbangkan faktor-faktor eksternal tersebut.
    """)

elif st.session_state.tab == 'Chatbot':
    # ====== Konfigurasi ======
    OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]  # Ganti dengan punyamu
    MODEL_NAME = "microsoft/mai-ds-r1:free"

    # ====== Load data ======
    st.title("🚗 Chatbot Data Mobil Bekas Toyota")

    try:
        df = pd.read_csv("data_mobil.csv")
        df['Mobil_Bekas'] = df['Mobil_Bekas'].str.lower().str.strip()
        st.success("✅ Data berhasil dimuat!")
    except:
        st.error("❌ Gagal memuat data CSV.")
        st.stop()
    with st.expander("📌 Catatan Tentang Chatbot"):
        st.markdown("""
        **Catatan Penggunaan Chatbot**  
        Chatbot bekerja berdasarkan hal berikut:

        ```python
        data_text = df.head(100).to_string(index=False) 
        prompt_awal_data = f"Saya memiliki data mobil bekas sebagai berikut:\\n\\n{data_text}\\n\\nSilakan jawab pertanyaan saya berdasarkan data di atas."
        🔹 Hanya 100 data teratas yang dibaca untuk menghindari performa lambat atau error, karena model memiliki batas jumlah token.
        🔹 Meski hanya membaca 100 data, pertanyaan tetap bebas karena chatbot mampu memprediksi dan mengestimasi jawaban berdasarkan pola.

        🔸 Model chatbot yang digunakan adalah microsoft/mai-ds-r1:free dari openrouter.ai.
        🔸 Model ini memiliki batas penggunaan harian. Jika chatbot error dan muncul pesan seperti "choice", berarti batas harian sudah tercapai dan bisa digunakan lagi keesokan harinya.

        🤖 Chatbot terhubung dengan model prediksi tambahan yang telah dilatih menggunakan seluruh data (26.000 baris) di Google Colab.
        Model tambahan tersebut adalah model yang sama dengan model yang digunakan pada fitur prediksi diatas.          
        Jika pertanyaan berkaitan dengan mobil yang tidak terdapat dalam 100 data teratas, chatbot akan mengirim input ke model prediksi dan menggunakan hasilnya sebagai jawaban.

        💬 Chatbot dapat menjawab berbagai pertanyaan, seperti:

        Harga bekas mobil tertentu

        Link terkait mobil tersebut

        Rekomendasi mobil terbaik

        Rekomendasi mobil dengan harga di bawah angka tertentu

        Dan pertanyaan lain yang relevan dengan data
        """)

    with st.expander("📊 Lihat Data Mobil"):
        st.dataframe(df)

    # ====== Load model & fitur ======
    try:
        model = joblib.load("model_prediksi_harga.pkl")
        feature_columns = joblib.load("feature_columns.pkl")
        scaler_X = joblib.load("scaler_X.pkl")
        scaler_y = joblib.load("scaler_y.pkl")
    except:
        st.error("❌ Gagal memuat model atau scaler.")
        st.stop()

    # ====== Fungsi prediksi ======
    def predict_price(mobil, tahun, harga_baru_override=None):
        mobil = mobil.lower().strip()
        df_filtered = df[df['Mobil_Bekas'] == mobil]

        if df_filtered.empty:
            return None, "TIDAK_ADA_MOBIL"

        harga_baru_rata2 = harga_baru_override if harga_baru_override else df_filtered['Harga_Baru'].mean()
        umur = 2025 - tahun

        df_input = pd.DataFrame({
            'Mobil_Bekas': [mobil],
            'Tahun': [tahun],
            'Harga_Baru': [harga_baru_rata2],
            'Umur_Mobil': [umur]
        })

        # Encoding
        df_input = pd.get_dummies(df_input, columns=['Mobil_Bekas'], drop_first=False)
        df_input = df_input.reindex(columns=feature_columns, fill_value=0)

        try:
            input_scaled = scaler_X.transform(df_input)
            pred_scaled = model.predict(input_scaled)
            harga = scaler_y.inverse_transform(pred_scaled)[0][0]
            return harga, None
        except Exception as e:
            return None, f"ERROR_MODEL: {str(e)}"

    # ====== Fungsi OpenRouter ======
    def ask_openrouter(prompt_awal, pertanyaan):
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-site.com",
            "X-Title": "Chatbot Mobil Bekas",
        }
        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": prompt_awal},
                {"role": "user", "content": pertanyaan}
            ]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ Error: {response.status_code} - {response.text}"

    # ====== Estimasi harga baru menggunakan OpenRouter ======
    def estimasi_harga_baru_dari_openrouter(nama_mobil, tahun):
        prompt_estimasi = (
            f"Berdasarkan data berikut:\n\n{data_text}\n\n"
            f"Tolong perkirakan *harga baru* dari mobil bekas '{nama_mobil}' tahun {tahun} "
            f"berdasarkan tren harga mobil serupa dalam data tersebut. Berikan hanya angka tanpa penjelasan tambahan."
        )
        jawaban = ask_openrouter(prompt_estimasi, f"Harga baru {nama_mobil} tahun {tahun} berapa?")
        
        # Ambil angka dari jawaban
        angka = re.findall(r"\d+", jawaban.replace(".", "").replace(",", ""))
        if angka:
            return int(angka[0])
        else:
            return None

    # ====== Prompt awal ======
    data_text = df.head(100).to_string(index=False)
    prompt_awal_data = f"Saya memiliki data mobil bekas sebagai berikut:\n\n{data_text}\n\nSilakan jawab pertanyaan saya berdasarkan data di atas."

    # ====== Fungsi fuzzy matching ======
    def fuzzy_match_mobil(mobil_name):
        choices = df['Mobil_Bekas'].unique()
        best_match = process.extractOne(mobil_name, choices, score_cutoff=80)
        if best_match:
            return best_match[0]
        return None

    # ====== Input pengguna ======
    pertanyaan = st.text_input("Tanyakan sesuatu tentang data mobil bekas:")

    # ====== Tombol Submit ======
    if st.button("💬 Tanya"):
        if pertanyaan.strip() == "":
            st.warning("Masukkan pertanyaan terlebih dahulu.")
        else:
            st.info("Sedang memproses...")

            # Case 1 & 2: Nama mobil dan tahun disebut langsung
            match = re.search(r"harga (bekas|baru) (.+?) tahun (\d{4})", pertanyaan.lower())
            if match:
                harga_type = match.group(1).strip()  # Bekas atau Baru
                nama_mobil = match.group(2).strip()
                tahun = int(match.group(3))

                nama_mobil_matched = fuzzy_match_mobil(nama_mobil) or nama_mobil
                df_matched = df[(df['Mobil_Bekas'] == nama_mobil_matched.lower()) & (df['Tahun'] == tahun)]

                if not df_matched.empty:
                    if harga_type == "baru":
                        # Jika yang ditanyakan adalah harga baru
                        harga_baru = df_matched['Harga_Baru'].mean()
                        st.success(f"📊 Berdasarkan data, *{nama_mobil_matched.title()}* tahun {tahun} memiliki harga baru sekitar **Rp {harga_baru:,.0f}**.")
                    else:
                        # Jika yang ditanyakan adalah harga bekas
                        harga_langsung = df_matched['Harga_Bekas'].mean()
                        st.success(f"📊 Berdasarkan data, *{nama_mobil_matched.title()}* tahun {tahun} memiliki harga bekas rata-rata sekitar **Rp {harga_langsung:,.0f}**.")
                else:
                    # Jika data tidak ditemukan di dataset
                    harga_pred, err = predict_price(nama_mobil_matched, tahun)
                    if harga_pred:
                        st.success(f"🧠 Prediksi harga bekas untuk *{nama_mobil_matched.title()}* tahun {tahun} adalah sekitar **Rp {harga_pred:,.0f}**.")
                    else:
                        st.error("❌ Gagal melakukan prediksi harga.")


            else:
            # Case 3 & 4: Tidak disebut tahun, atau hanya harga baru
                match_mobil = re.search(r"harga (bekas|baru) (.+?)", pertanyaan.lower())
                if match_mobil:
                    harga_type = match_mobil.group(1).strip()  # Bekas atau Baru
                    nama_mobil = match_mobil.group(2).strip()

                    if harga_type == "baru" and "tahun" not in pertanyaan.lower():
                        # Case 4: Harga baru disebutkan tapi tahun tidak disebutkan
                        st.info(f"📌 Tahun untuk mobil '{nama_mobil}' tidak ditemukan. Silakan masukkan tahun dalam prompt, contoh: 'harga baru {nama_mobil} tahun 2020'.")
                    elif harga_type == "bekas" and "tahun" not in pertanyaan.lower():
                        # Case 3: Harga bekas disebutkan tapi tahun tidak disebutkan
                        st.info(f"📌 Tahun untuk mobil '{nama_mobil}' tidak ditemukan. Silakan masukkan tahun ke dalam prompt, contoh: 'harga bekas {nama_mobil} tahun 2020'.")
                    else:
                        # Case 4: Ada "harga baru" → minta tahun & harga baru dari user
                        if harga_type == "baru":
                            st.info("📌 Tahun dan harga baru tidak disebutkan. Silakan masukkan tahun dan harga baru mobil ke dalam prompt, contoh: 'harga baru {nama_mobil} tahun 2020 harga baru 300000000'.")
                        else:
                            # Case 3: Harga bekas tanpa tahun → minta input manual
                            st.info(f"📌 Tahun untuk mobil '{nama_mobil}' tidak ditemukan. Silakan masukkan tahun ke dalam prompt, contoh: 'harga bekas {nama_mobil} tahun 2020'.")


                else:
                    # Case 5 & 6: Nama mobil tidak dikenali
                    jawaban = ask_openrouter(prompt_awal_data, pertanyaan)
                    st.markdown("### 💡 Jawaban")
                    st.write(jawaban)
