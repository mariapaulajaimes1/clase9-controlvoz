import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

# Variables iniciales
message_received = ""
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("mariapaulajaimesr")

# Funciones de MQTT
def on_publish(client, userdata, result):  
    st.success("✅ Dato publicado con éxito")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(f"📩 Mensaje recibido: {message_received}")

client1.on_message = on_message

# Configuración de la interfaz
st.set_page_config(page_title="Control por Voz MQTT", page_icon="🎤")
st.title("🎤 Control por Voz MQTT")

# Imágenes y subtítulos
st.subheader("Usa tu voz para controlar dispositivos")
image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)
st.write("Pulsa el botón y habla")

# Botón de inicio de reconocimiento de voz
stt_button = Button(label="Iniciar Reconocimiento de Voz", width=200)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

# Procesar resultado de voz
if result and "GET_TEXT" in result:
    st.write(f"🔊 Comando de voz recibido: {result.get('GET_TEXT')}")
    client1.on_publish = on_publish  
    client1.connect(broker, port)
    message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
    client1.publish("controlvoz", message)

    # Confirmación visual
    st.success("🚀 Comando enviado con éxito")

# Sección de ayuda y mensajes recibidos
st.sidebar.header("ℹ️ Ayuda y Estado")
st.sidebar.write("Usa comandos de voz para controlar dispositivos conectados por MQTT.")
st.sidebar.write("Ejemplos de comandos: 'Encender luz', 'Apagar luz'.")
if message_received:
    st.sidebar.write(f"📬 Último mensaje recibido: {message_received}")
else:
    st.sidebar.write("Esperando mensajes...")

# Crear directorio temporal si no existe
try:
    os.mkdir("temp")
except FileExistsError:
    pass
