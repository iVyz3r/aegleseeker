# aeglemain.py
import sys
import ctypes
import pymem
import pymem.process
import threading
import time
from ctypes import wintypes
from dearpygui import dearpygui as dpg
from pypresence import Presence

# ------------------ RPC CONFIG ------------------
DISCORD_CLIENT_ID = "1401732095977586688"
rpc = None

def start_discord_rpc():
    global rpc
    try:
        rpc = Presence(DISCORD_CLIENT_ID)
        rpc.connect()
        rpc.update(
            details="In the game",
            state="Minecraft: Windows 10 Edition Beta: Reach Modifiable",
            large_image="aegleseeker",
            large_text="Aegleseeker Client",
            start=time.time()
        )
        log_info("Discord RPC started.")
    except Exception as e:
        log_error(f"Error starting RPC: {e}")

def stop_discord_rpc():
    global rpc
    try:
        if rpc:
            rpc.clear()
            rpc.close()
            log_info("Discord RPC stopped.")
    except Exception as e:
        log_error(f"Error stopping RPC: {e}")

# ------------------ ADMIN CHECK ------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    params = ' '.join([f'"{x}"' for x in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)

PROCESS_NAME = "Minecraft.Win10.DX11.exe"
OFFSET_REACH = 0xB52A70

pm = None
process_base = None
reach_address = None
auto_refresh = True

process_found = False
fade_alpha = 1.0
log_lines = []
logs_visible = True

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

PAGE_EXECUTE_READWRITE = 0x40
old_protect = wintypes.DWORD()

# ------------------ DARK PURPLE THEME ------------------
def apply_theme():
    with dpg.theme() as purple_theme:
        with dpg.theme_component(dpg.mvAll):
            # Ventana principal
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (50, 30, 90, 255))  # morado oscuro
            
            # Botones
            dpg.add_theme_color(dpg.mvThemeCol_Button, (110, 80, 180, 255))          
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (140, 110, 220, 255))   
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (160, 130, 240, 255))    
            
            # Frames y sliders
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (90, 60, 150, 255))          
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (150, 110, 220, 255))      
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (180, 140, 240, 255)) 
            
            # Checkboxes
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (200, 160, 255, 255))       
            
            # Texto
            dpg.add_theme_color(dpg.mvThemeCol_Text, (230, 220, 255, 255))            
    
            # Headers
            dpg.add_theme_color(dpg.mvThemeCol_Header, (120, 90, 200, 255))          
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (150, 120, 230, 255))   
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (170, 140, 240, 255))    
            
            # Bordes y detalles
            dpg.add_theme_color(dpg.mvThemeCol_Border, (160, 120, 220, 255))
            dpg.add_theme_color(dpg.mvThemeCol_Separator, (170, 130, 230, 255))
            
    return purple_theme

# ------------------ GRADIENT FADE ------------------
def fade_in_gradient_viewport(steps=60, delay=0.01):
    top_color = (40, 20, 80)    # morado oscuro arriba
    bottom_color = (70, 40, 120) # morado más claro abajo
    for i in range(steps):
        t = i / steps
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        dpg.set_viewport_clear_color((r, g, b, 255))
        time.sleep(delay)

# ------------------ LOGGING ------------------
def log_info(message):
    log_lines.append(f"Info -> {message}")
    if len(log_lines) > 20:
        log_lines.pop(0)
    update_log_widget()

def log_error(message):
    log_lines.append(f"Error -> {message}")
    if len(log_lines) > 20:
        log_lines.pop(0)
    update_log_widget()
    MB_ICONERROR = 0x10
    MB_OK = 0x0
    ctypes.windll.user32.MessageBoxW(0, message, "Error", MB_OK | MB_ICONERROR)

def update_log_widget():
    if dpg.does_item_exist("log_text"):
        dpg.set_value("log_text", "\n".join(log_lines))

# ------------------ PROCESS MEMORY ------------------
def open_process():
    global pm, process_base, reach_address, process_found
    try:
        pm = pymem.Pymem(PROCESS_NAME)
        process_base = pymem.process.module_from_name(pm.process_handle, PROCESS_NAME).lpBaseOfDll
        reach_address = process_base + OFFSET_REACH
        process_found = True
        log_info(f"Process opened. Direct Reach address: 0x{reach_address:X}")
        threading.Thread(target=fade_out_message, daemon=True).start()
        return True
    except Exception as e:
        process_found = False
        log_error(f"Error opening process: {e}")
        return False

def write_memory(address, value):
    size = ctypes.sizeof(ctypes.c_float)
    if not kernel32.VirtualProtectEx(pm.process_handle, ctypes.c_void_p(address), size, PAGE_EXECUTE_READWRITE, ctypes.byref(old_protect)):
        log_error(f"VirtualProtectEx failed for 0x{address:X}")
        return False
    try:
        pm.write_float(address, value)
        return True
    except Exception as e:
        log_error(f"Error writing memory: {e}")
        return False
    finally:
        kernel32.VirtualProtectEx(pm.process_handle, ctypes.c_void_p(address), size, old_protect.value, ctypes.byref(old_protect))

def get_reach():
    try:
        val = pm.read_float(reach_address)
        return val
    except Exception as e:
        log_error(f"Error reading Reach: {e}")
        return 0.0

def set_reach(sender, app_data, user_data):
    input_val_str = dpg.get_value("reach_input")
    try:
        val = float(input_val_str)
        if val < 3.0 or val > 15.0:
            log_error("Value must be between 3.0 and 15.0")
            return
        dpg.set_value("reach_slider", val)
    except ValueError:
        log_error("Invalid value")
        return

    if not write_memory(reach_address, val):
        log_error(f"Error writing Reach at 0x{reach_address:X}")
    else:
        log_info(f"Reach value set to: {val:.2f}")

def set_reach_from_slider(sender, app_data, user_data):
    val = dpg.get_value("reach_slider")
    dpg.set_value("reach_input", f"{val:.2f}")
    if not write_memory(reach_address, val):
        log_error(f"Error writing Reach at 0x{reach_address:X}")
    else:
        log_info(f"Reach value set to: {val:.2f}")

def refresh_reach():
    val = get_reach()
    if val != dpg.get_value("reach_slider"):
        dpg.set_value("reach_slider", val)
        dpg.set_value("reach_input", f"{val:.2f}")

def auto_refresh_thread():
    global process_found
    while auto_refresh:
        if pm is None:
            try:
                pm_temp = pymem.Pymem(PROCESS_NAME)
                pm_temp.close_process()
                del pm_temp
                process_found = open_process()
            except:
                process_found = False
        else:
            refresh_reach()
        update_status_text()
        time.sleep(1)

def update_status_text():
    global process_found, fade_alpha
    if not dpg.does_item_exist("status_text"):
        return
    if not process_found:
        dpg.configure_item("status_text", default_value=f"Waiting for the process {PROCESS_NAME}...", color=(255, 255, 255, 255), show=True)
        fade_alpha = 1.0
    else:
        color = (0, 255, 0, int(255 * fade_alpha))
        dpg.configure_item("status_text", default_value="Process Found!", color=color, show=True)

def fade_out_message():
    global fade_alpha
    time.sleep(3)
    steps = 30
    for _ in range(steps):
        fade_alpha -= 1.0 / steps
        if fade_alpha < 0:
            fade_alpha = 0
        time.sleep(0.05)
    if dpg.does_item_exist("status_text"):
        dpg.configure_item("status_text", show=False)

def toggle_logs_visibility():
    global logs_visible
    logs_visible = not logs_visible
    dpg.configure_item("log_text", show=logs_visible)

def self_destruct():
    global auto_refresh, pm, reach_address
    auto_refresh = False
    try:
        if pm is not None and reach_address is not None:
            write_memory(reach_address, 3.0)
            log_info("Reach restored to 3.0 before shutting down.")
    except Exception as e:
        log_error(f"Error in self-destruct: {e}")
    stop_discord_rpc()
    log_info("Self-destruct activated. Closing GUI...")
    dpg.stop_dearpygui()
    sys.exit(0)

# ------------------ START GUI ------------------
def start_gui():
    global fade_alpha

    dpg.create_context()

    with dpg.window(label="Aegleseeker Config", tag="main_window", width=460, height=520):
        dpg.add_text("Connect and modify Reach")
        dpg.add_button(label="Open process", callback=lambda: open_process())

        with dpg.group(horizontal=True):
            dpg.add_slider_float(label="Reach Slider", tag="reach_slider", min_value=3.0, max_value=15.0, default_value=3.0, callback=set_reach_from_slider, width=300)
            dpg.add_input_text(tag="reach_input", default_value="3.00", width=60)

        dpg.add_button(label="Set value", callback=set_reach)
        dpg.add_button(label="Update value", callback=refresh_reach)
        dpg.add_button(label="Self Destruct", callback=self_destruct)
        dpg.add_separator()
        dpg.add_text("", tag="status_text")
        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_checkbox(label="Show logs", tag="show_logs", default_value=True, callback=lambda s,a,u: toggle_logs_visibility())
            dpg.add_button(label="Hide / Show logs", callback=toggle_logs_visibility)
            with dpg.tooltip("show_logs"):
                dpg.add_text("Toggle the visibility of the logs panel")

        dpg.add_input_text(tag="log_text", multiline=True, readonly=True, height=120, width=430, show=True)

    dpg.create_viewport(title='Aegleseeker Client', width=480, height=540)
    dpg.setup_dearpygui()
    dpg.bind_theme(apply_theme())  # Aplicar tema
    dpg.show_viewport()

    start_discord_rpc()
    threading.Thread(target=auto_refresh_thread, daemon=True).start()
    threading.Thread(target=fade_in_gradient_viewport, daemon=True).start()

    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    start_gui()
