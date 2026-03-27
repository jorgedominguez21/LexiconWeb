import customtkinter as ctk

class VentanaLecturaGrande(ctk.CTkToplevel):
    def __init__(self, parent, titulo, contenido):
        super().__init__(parent)
        self.title(titulo)
        
        # Tamaño y centrado
        ancho, alto = 800, 600
        px = (self.winfo_screenwidth() // 2) - (ancho // 2)
        py = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{px}+{py}")
        self.configure(fg_color="#f0f0f0")

        ctk.CTkLabel(self, text=titulo, font=("Helvetica", 24, "bold"), text_color="#2c3e50").pack(pady=20)

        self.txt = ctk.CTkTextbox(self, font=("Helvetica", 18), wrap="word", fg_color="white", text_color="black", border_width=2)
        self.txt.pack(expand=True, fill="both", padx=30, pady=(0, 30))
        
        self.txt.insert("1.0", contenido)
        self.txt.configure(state="disabled")
        
        ctk.CTkButton(self, text="CERRAR", command=self.destroy, fg_color="#e74c3c", hover_color="#c0392b").pack(pady=10)
        self.grab_set()