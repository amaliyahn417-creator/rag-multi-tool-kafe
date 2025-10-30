import streamlit as st
import requests
import json
import time

# GANTI DENGAN URL NGROK AKTIF ANDA
OLLAMA_API_URL = "https://subarchesorial-hildred-subsyndic.ngrok-free.dev"

# Judusl Aplikasi
st.title("☕ Analis Pasar Kafe (Llama 3 RAG)")
st.caption("Berinteraksi dengan model Llama 3 Anda melalui NGROK.")

# Inisialisasi Riwayat Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tampilkan Riwayat Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Fungsi untuk memanggil Ollama API (menggunakan streaming)
def query_ollama_stream(prompt):
    url = f"{OLLAMA_API_URL}/api/generate"

    # Payload yang dikirim ke Ollama
    data = {
        "model": "llama3",
        "prompt": prompt,
        "stream": True # Menggunakan streaming untuk output real-time
    }

    try:
        # Panggil API
        with requests.post(url, json=data, stream=True) as response:
            if response.status_code == 200:
                full_response = ""
                # Memproses respons streaming
                for chunk in response.iter_lines(decode_unicode=True):
                    if chunk:
                        try:
                            data = json.loads(chunk)
                            content = data.get("response", "")
                            full_response += content
                            yield content # Mengirimkan output secara bertahap
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
                return full_response
            else:
                st.error(f"Error dari Ollama API: {response.status_code} - Mohon periksa server Ollama Anda di Colab.")
                return ""
    except requests.exceptions.RequestException as e:
        st.error(f"Koneksi NGROK/Ollama Gagal: {e}")
        return ""

# Logika Input Chat
if prompt := st.chat_input("Tanyakan analisis Anda..."):
    # Tambahkan input pengguna ke riwayat
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Tampilkan pesan pengguna
    with st.chat_message("user"):
        st.markdown(prompt)

    # Dapatkan respons dari Ollama API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        # Gunakan fungsi streaming
        for response_chunk in query_ollama_stream(prompt):
            full_response += response_chunk
            message_placeholder.markdown(full_response + "▌") # Menampilkan dengan kursor
            time.sleep(0.01) # Jeda kecil

        message_placeholder.markdown(full_response) # Final response

    # Tambahkan respons asisten ke riwayat
    st.session_state.messages.append({"role": "assistant", "content": full_response})
