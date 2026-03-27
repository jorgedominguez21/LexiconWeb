import customtkinter as ctk
import webbrowser
from palabras_engine import PalabrasEngine
from tkinter import messagebox
from interfaz_utils import VentanaBase
from constantes import CATEGORIAS_GRAMATICALES, CATEGORIAS_INVERSAS

class VentanaGestionPalabras(VentanaBase):
    def __init__(self, *args, **kwargs):
        super().__init__(kwargs.get('master'), "Mantenimiento de Diccionario - Lexicon Pro", ancho=1200, alto=750)

        self.engine_p = PalabrasEngine()
        self.id_sel = None
        self.debounce_id = None
        self.is_loading = False

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- PANEL IZQUIERDO: FICHA DE EDICIÓN ---
        self.f_form = ctk.CTkFrame(self, width=320)
        self.f_form.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.f_form, text="FICHA DE EDICIÓN", font=("Arial", 20, "bold")).pack(pady=10)

        self.e_word = ctk.CTkEntry(self.f_form, placeholder_text="Escribe la palabra...", width=280, height=35, justify="center")
        self.e_word.pack(pady=(10, 5))

        ctk.CTkLabel(self.f_form, text="Categoría Gramatical:", font=("Arial", 12)).pack(pady=(5, 0))
        self.combo_tipo = ctk.CTkComboBox(self.f_form, values=list(CATEGORIAS_GRAMATICALES.keys()), width=280, height=35)
        self.combo_tipo.set("Sustantivo")
        self.combo_tipo.pack(pady=5)
        
        ctk.CTkLabel(self.f_form, text="Definición propia / Nota:", font=("Arial", 12, "bold"), text_color="#2c6e49").pack(pady=(10, 0))
        self.t_def = ctk.CTkTextbox(self.f_form, width=280, height=250, font=("Arial", 13))
        self.t_def.pack(pady=10)
        
        self.btn_save = ctk.CTkButton(self.f_form, text="GUARDAR CAMBIOS", fg_color="#285da1", command=self.ejecutar_guardado)
        self.btn_save.pack(pady=10)
        
        ctk.CTkButton(self.f_form, text="Nueva / Limpiar", fg_color="#666", command=self.limpiar_campos).pack(pady=5)
        
        self.btn_delete = ctk.CTkButton(self.f_form, text="BORRAR FICHA", fg_color="#922b21", command=self.confirmar_borrado)
        self.btn_delete.pack(pady=25) 

        # --- PANEL DERECHO: LISTADO ---
        self.f_list = ctk.CTkFrame(self)
        self.f_list.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Cabecera
        self.f_header = ctk.CTkFrame(self.f_list, fg_color="transparent")
        self.f_header.pack(fill="x", padx=20, pady=(15, 5))

        self.ent_busqueda = ctk.CTkEntry(self.f_header, placeholder_text="🔍 Buscar término...", height=35)
        self.ent_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.lbl_db = ctk.CTkLabel(self.f_header, text=f"🌐 DB: {self.engine_p.db.entorno.upper()}", font=("Arial", 11, "bold"))
        self.lbl_db.pack(side="right")

        # Sub-Cabecera con Atajos en Negrita
        self.f_sub_header = ctk.CTkFrame(self.f_list, fg_color="transparent")
        self.f_sub_header.pack(fill="x", padx=20, pady=(0, 10))

        self.lbl_help = ctk.CTkLabel(self.f_sub_header, text="F2 / CTRL+L: LIMPIAR BÚSQUEDA", font=("Arial", 10, "bold"), text_color="#d35400")
        self.lbl_help.pack(side="left")

        self.btn_toggle_db = ctk.CTkButton(self.f_sub_header, text="🔄 Cambiar Local/Nube", width=140, height=28, fg_color="#555", command=self.toggle_db)
        self.btn_toggle_db.pack(side="right")

        # Scroll de palabras
        self.scroll = ctk.CTkScrollableFrame(self.f_list, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # --- BINDINGS CORREGIDOS ---
        self.ent_busqueda.bind("<KeyRelease>", self.on_key_release)
        self.bind_all("<F2>", lambda e: self.limpiar_busqueda())
        self.bind_all("<Control-l>", lambda e: self.limpiar_busqueda())
        self.bind_all("<Control-L>", lambda e: self.limpiar_busqueda()) # Para mayúsculas

        self.actualizar_tabla()

    def limpiar_busqueda(self):
        """Limpia el cuadro de texto de forma atómica"""
        # 1. Borramos el texto
        self.ent_busqueda.delete(0, 'end')
        
        # 2. Cancelamos cualquier búsqueda pendiente del debounce
        if self.debounce_id:
            self.after_cancel(self.debounce_id)
            self.debounce_id = None
            
        # 3. Forzamos una ÚNICA actualización limpia
        self.actualizar_tabla()
        self.ent_busqueda.focus()

    def actualizar_tabla(self):
        if self.is_loading: return
        self.is_loading = True
        
        # LIMPIEZA TOTAL DEL PANEL ANTES DE CARGAR
        for w in self.scroll.winfo_children(): 
            w.destroy()
        
        try:
            # Buscamos ignorando mayúsculas/minúsculas
            busqueda = self.ent_busqueda.get().strip().lower()
            
            # --- CAMBIO AQUÍ: Usamos 'listar_rapido' que es el nombre real ---
            datos = self.engine_p.listar_rapido(busqueda) 
            
            # Usamos un set para evitar duplicados visuales si la BD falla
            vistos = set()

            for p in datos:
                if p[0] in vistos: continue # p[0] es el ID
                vistos.add(p[0])

                tipo_str = f"({p[2]})" if len(p) > 2 else ""
                
                fila = ctk.CTkFrame(self.scroll, fg_color=("#ebebeb", "#2b2b2b"))
                fila.pack(fill="x", pady=2, padx=5)
                
                # Palabra y Tipo
                ctk.CTkButton(fila, text=f"{p[1].upper()}  {tipo_str}", anchor="w", fg_color="transparent", 
                              text_color=("black", "white"), font=("Arial", 13, "bold"), height=35,
                              command=lambda d=p: self.cargar_datos(d)).pack(side="left", fill="x", expand=True, padx=10)
                
                # Botones de Acción
                ctk.CTkButton(fila, text="📖 DÍA", width=55, fg_color="#2c6e49",
                              command=lambda d=p: self.mostrar_palabra_dia(d)).pack(side="left", padx=2)
                
                ctk.CTkButton(fila, text="🌐 RAE", width=55, fg_color="#1f538d",
                              command=lambda d=p: webbrowser.open(f"https://dle.rae.es/{d[1].lower()}")).pack(side="left", padx=2)

                # BOTÓN WIKI
                ctk.CTkButton(fila, text="📚 WIKI", width=55, fg_color="#7d3c98",
                              command=lambda d=p: webbrowser.open(f"https://es.wiktionary.org/wiki/{d[1].lower()}")).pack(side="left", padx=2)
        except Exception as e:
            print(f"Error cargando tabla: {e}")
        finally:
            self.is_loading = False
            
    def on_key_release(self, event):
        # Si la tecla pulsada es F2 o Ctrl, no hacemos nada aquí 
        # porque ya tienen su propia función asignada
        if event.keysym in ("F2", "Control_L", "Control_R"):
            return
            
        if self.debounce_id: 
            self.after_cancel(self.debounce_id)
        
        # Aumentamos un pelín el margen (400ms) para que sea más suave
        self.debounce_id = self.after(400, self.actualizar_tabla)

    def ejecutar_guardado(self):
        pal = self.e_word.get().strip()
        if not pal: return
        label_tipo = self.combo_tipo.get()
        codigo_tipo = CATEGORIAS_GRAMATICALES.get(label_tipo, "sust")
        contenido = self.t_def.get("1.0", "end-1c")

        if not self.id_sel:
            res = self.engine_p.insertar(pal, contenido, codigo_tipo)
        else:
            res = self.engine_p.actualizar(self.id_sel, pal, contenido, codigo_tipo)

        if res == "OK":
            messagebox.showinfo("Éxito", "Guardado correctamente")
            self.actualizar_tabla()
            self.limpiar_campos()

    def cargar_datos(self, d):
        self.id_sel = d[0]
        self.e_word.delete(0, 'end')
        self.e_word.insert(0, d[1])
        codigo_bd = d[2] if len(d) > 2 else "sust"
        self.combo_tipo.set(CATEGORIAS_INVERSAS.get(codigo_bd, "Sustantivo"))
        self.t_def.delete("1.0", "end")
        self.t_def.insert("1.0", d[3] if d[3] else "")
        self.btn_save.configure(text="ACTUALIZAR FICHA", fg_color="#e67e22")

    def limpiar_campos(self):
        self.id_sel = None
        self.e_word.delete(0, 'end')
        self.t_def.delete("1.0", 'end')
        self.combo_tipo.set("Sustantivo")
        self.btn_save.configure(text="GUARDAR CAMBIOS", fg_color="#285da1")

    def toggle_db(self):
        import configparser
        from database import Database  # <--- IMPORTANTE: para poder resetear
        from tkinter import messagebox
        
        try:
            # 1. Cambiamos el valor en el archivo config.ini
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            
            actual = config.get('SETTINGS', 'entorno', fallback='local').lower()
            nuevo = 'nube' if actual == 'local' else 'local'
            
            config.set('SETTINGS', 'entorno', nuevo)
            with open('config.ini', 'w', encoding='utf-8') as f:
                config.write(f)
            
            # 2. EL PASO CLAVE: Cerramos el grifo de la conexión vieja
            Database.reset_pool() 
            
            # 3. Creamos el nuevo motor (que leerá el nuevo entorno del .ini)
            self.engine_p = PalabrasEngine() 
            
            # 4. Refrescamos la interfaz
            self.lbl_db.configure(text=f"🌐 DB: {nuevo.upper()}")
            self.actualizar_tabla() 
            
            messagebox.showinfo("Conexión", f"Cambiado con éxito a: {nuevo.upper()}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar de base de datos: {e}")
    
    def mostrar_palabra_dia(self, d):
        VentanaPalabraDia(d[1], d[3], master=self)

    def confirmar_borrado(self):
        if not self.id_sel: return
        if messagebox.askyesno("Borrar", f"¿Eliminar '{self.e_word.get()}'?"):
            if self.engine_p.eliminar(self.id_sel) == "OK":
                self.limpiar_campos()
                self.actualizar_tabla()

# CLASE EMERGENTE (Asegúrate de que esté al final del archivo)
class VentanaPalabraDia(VentanaBase):
    def __init__(self, titulo, contenido, *args, **kwargs):
        super().__init__(kwargs.get('master'), f"Consulta: {titulo.upper()}", ancho=800, alto=600)
        ctk.CTkLabel(self, text=titulo.upper(), font=("Arial", 30, "bold"), text_color="#1f538d").pack(pady=20)
        self.txt = ctk.CTkTextbox(self, width=740, height=400, font=("Verdana", 16)) 
        self.txt.pack(padx=20, pady=10)
        self.txt.insert("1.0", f"DEFINICIÓN:\n\n{contenido if contenido else 'Sin datos.'}")
        self.txt.configure(state="disabled")
        ctk.CTkButton(self, text="Cerrar", command=self.destroy, fg_color="#555").pack(pady=20)
        self.forzar_frente()