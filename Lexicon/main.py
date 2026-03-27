import customtkinter as ctk
from gestion_palabras import VentanaGestionPalabras
from palabras_engine import PalabrasEngine
from mnto_engine import MntoEngine
from tkinter import messagebox
from juego_ahorcado import VentanaAhorcado
import threading

ctk.set_appearance_mode("light")

class EscritorioLexicon(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.engine_m = MntoEngine()
        self.engine_p = PalabrasEngine() 
        
        self.title("Lexicon Studio - Panel de Control")
        w, h = 1000, 650 
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2) - 50
        self.geometry(f"{w}x{h}+{x}+{y}")

        # --- Barra de Navegación ---
        self.nav = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.nav.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.nav, text="MÓDULOS", font=("Arial", 16, "bold")).pack(pady=30)
        
        self.btn_pal = ctk.CTkButton(self.nav, text="Gestión de Palabras", 
                                    height=40, command=self.abrir_modulo_palabras)
        self.btn_pal.pack(pady=10, padx=20, fill="x")
        
        self.btn_refresh = ctk.CTkButton(self.nav, text="🔄 Actualizar Contador", 
                                        fg_color="#2c6e49", hover_color="#1e4a32",
                                        command=self.actualizar_contador)
        self.btn_refresh.pack(pady=10, padx=20, fill="x")

        self.btn_juego = ctk.CTkButton(self.nav, text="🎮 Jugar Ahorcado", 
                                       fg_color="#d35400", hover_color="#a04000",
                                       command=self.abrir_juego)
        self.btn_juego.pack(pady=30, padx=20, fill="x")

        self.btn_indices = ctk.CTkButton(self.nav, text="⚡ Optimizar Índices DB", 
                                        fg_color="#27ae60", hover_color="#229954",
                                        command=self.optimizar_indices)
        self.btn_indices.pack(pady=10, padx=20, fill="x")

        self.btn_sync = ctk.CTkButton(self.nav, text="🔄 Sincronizar DBs Local ↔ Nube", 
                                     fg_color="#9b59b6", hover_color="#8e44ad",
                                     command=self.sincronizar_dbs)
        self.btn_sync.pack(pady=10, padx=20, fill="x")

        # --- Zona de Bienvenida (Derecha) ---
        self.canvas = ctk.CTkFrame(self, fg_color="transparent")
        self.canvas.pack(side="right", fill="both", expand=True)

        self.lbl_titulo = ctk.CTkLabel(self.canvas, text="LEXICON STUDIO", 
                                      font=("Century Gothic", 60, "bold"), text_color="#1f538d")
        self.lbl_titulo.place(relx=0.5, rely=0.35, anchor="center")
        
        self.lbl_user = ctk.CTkLabel(self.canvas, text="Jorge Domínguez", 
                                    font=("Century Gothic", 28), text_color="gray")
        self.lbl_user.place(relx=0.5, rely=0.47, anchor="center")

        self.lbl_contador = ctk.CTkLabel(self.canvas, text="", 
                                        font=("Segoe UI", 18, "italic"), text_color="#285da1")
        self.lbl_contador.place(relx=0.5, rely=0.6, anchor="center")
        
        self.lbl_copy = ctk.CTkLabel(self.canvas, text="© 2026 Lexicon Studio | v1.0", 
                                    font=("Arial", 10), text_color="#777")
        self.lbl_copy.pack(side="bottom", pady=15)

        self.actualizar_contador()

    def actualizar_contador(self):
        try:
            total = self.engine_p.contar_total() 
            self.lbl_contador.configure(text=f"📊 Total de palabras: {total}", text_color="#1f538d")
        except:
            self.lbl_contador.configure(text="⚠️ Error al conectar con el contador", text_color="red")
    
    def abrir_modulo_palabras(self):
        VentanaGestionPalabras(master=self)

    def sincronizar_dbs(self):
        """Lanza la sincronización inteligente en un hilo separado"""
        self.btn_sync.configure(state="disabled", text="🔄 Sincronizando...")
        
        progress = ctk.CTkToplevel(self)
        progress.title("Sync DB")
        progress.geometry("350x150")
        progress.attributes("-topmost", True)
        
        lbl = ctk.CTkLabel(progress, text="Sincronizando Local ↔ Nube...\nEsto puede tardar unos segundos.", font=("Arial", 12))
        lbl.pack(expand=True)

        def run_sync():
            try:
                from sync_engine import SyncEngine
                engine = SyncEngine()
                resultado = engine.ejecutar_sincronizacion()
                messagebox.showinfo("Éxito", resultado)
            except Exception as e:
                messagebox.showerror("Error", f"Fallo en la sincronización:\n{str(e)}")
            finally:
                self.btn_sync.configure(state="normal", text="🔄 Sincronizar DBs Local ↔ Nube")
                progress.destroy()
                self.actualizar_contador()

        threading.Thread(target=run_sync, daemon=True).start()

    def optimizar_indices(self):
        from database import Database
        db = Database()
        res = db.optimizar_indices()
        messagebox.showinfo("Índices", res)
        self.actualizar_contador()

    def abrir_juego(self):
        VentanaAhorcado(self, self.engine_p)

if __name__ == "__main__":
    app = EscritorioLexicon()
    app.mainloop()