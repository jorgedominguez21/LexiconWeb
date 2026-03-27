import customtkinter as ctk

class VentanaBase(ctk.CTkToplevel):
    def __init__(self, maestro, titulo, ancho=None, alto=None, *args, **kwargs):
        super().__init__(maestro, *args, **kwargs)
        self.title(titulo)
        
        # --- MEJORA DE ENFOQUE Y JERARQUÍA ---
        if maestro:
            self.transient(maestro) # Indica que esta ventana "depende" de la principal
        
        # Si no le damos ancho/alto, intentamos calcularlo según el contenido
        if ancho and alto:
            self.centrar(ancho, alto)
        
        # Forzamos que se quede al frente y bloquee la de atrás
        self.after(100, self.forzar_frente)

    def centrar(self, ancho, alto):
        self.update_idletasks()
        # Evitamos que la ventana sea más grande que la pantalla
        ancho = min(ancho, self.winfo_screenwidth())
        alto = min(alto, self.winfo_screenheight())
        
        # Centramos respecto a la pantalla
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")

    def forzar_frente(self):
        """Hace que la ventana aparezca delante de todo y tome el control"""
        self.lift()                     # La eleva visualmente
        self.attributes("-topmost", True) # La pone encima de todas las apps
        self.focus_force()              # Pone el foco del teclado aquí
        self.grab_set()                 # BLOQUEA el menú principal (imprescindible)
        
        # Quitamos el 'topmost' tras medio segundo para que no bloquee 
        # a otros avisos del sistema (como un mensaje de Windows), 
        # pero el grab_set mantendrá la ventana por encima de tu Main.
        self.after(500, lambda: self.attributes("-topmost", False))