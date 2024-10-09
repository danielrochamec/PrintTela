import pyautogui
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import geocoder
import subprocess
import tkinter as tk
from tkinter import messagebox

# Função para obter a geolocalização
def get_geolocation():
    g = geocoder.ip('me')
    if g.ok:
        return f"{g.city}, {g.country} (Lat: {g.latlng[0]}, Lon: {g.latlng[1]})"
    else:
        return "Location not found"

# Função para obter o nome da rede Wi-Fi
def get_wifi_name():
    try:
        # Executa o comando para obter as informações da rede
        result = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'], encoding='utf-8')
        for line in result.split('\n'):
            if 'SSID' in line and 'BSSID' not in line:
                # Extrai o nome da rede (SSID)
                ssid = line.split(':')[1].strip()
                return ssid
    except Exception as e:
        return "Wi-Fi network not found"

# Função para capturar e anotar a área selecionada
def capture_and_annotate(x1, y1, x2, y2):
    screenshot = pyautogui.screenshot(region=(x1, y1, x2 - x1, y2 - y1))
    
    # Formatar a data no formato brasileiro DD/MM/AAAA HH:MM:SS
    current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    
    geolocation = get_geolocation()
    wifi_name = get_wifi_name()

    img = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
    
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    # Incluindo a data/hora, geolocalização e nome da rede Wi-Fi no texto
    text = f"Date/Time: {current_time}\nGeo: {geolocation}"
    
    img_width, img_height = img.size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x, y = img_width - text_width - 10, 10
    draw.text((x, y), text, font=font, fill="white")

    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img.save(filename)

    messagebox.showinfo("Sucesso", f"Captura de tela salva como {filename}")
    img.show()

# Função para iniciar a captura de área
def start_selection():
    global cancel_selection
    cancel_selection = False  # Reiniciar o estado de cancelamento

    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-alpha', 0.3)

    global start_x, start_y, end_x, end_y
    start_x, start_y = 0, 0
    end_x, end_y = 0, 0

    def on_start_selection(event):
        global start_x, start_y
        if not cancel_selection:  # Verificar se a seleção não foi cancelada
            start_x, start_y = event.x, event.y

    def on_draw_selection(event):
        global end_x, end_y
        if not cancel_selection:  # Verificar se a seleção não foi cancelada
            end_x, end_y = event.x, event.y
            canvas.delete("selection")
            canvas.create_rectangle(start_x, start_y, end_x, end_y, outline='red', width=2, tags="selection")

    def on_finish_selection(event):
        if not cancel_selection:  # Verificar se a seleção não foi cancelada
            root.quit()
            root.destroy()
            capture_and_annotate(start_x, start_y, end_x, end_y)

    def on_cancel():
        global cancel_selection
        cancel_selection = True  # Marcar que a seleção foi cancelada
        root.quit()
        root.destroy()

    canvas = tk.Canvas(root, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)

    canvas.bind("<Button-1>", on_start_selection)
    canvas.bind("<B1-Motion>", on_draw_selection)
    canvas.bind("<ButtonRelease-1>", on_finish_selection)


    root.mainloop()

# Função para criar a interface gráfica
def create_gui():
    root = tk.Tk()
    root.title("Captura de Tela")
    root.geometry("300x150")

    label = tk.Label(root, text="Clique para selecionar uma área", font=("Arial", 14))
    label.pack(pady=20)

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    capture_button = tk.Button(button_frame, text="Selecionar Área", font=("Arial", 12), command=start_selection)
    capture_button.grid(row=0, column=0, padx=10)


    root.mainloop()

# Executar a interface gráfica
if __name__ == "__main__":
    create_gui()
