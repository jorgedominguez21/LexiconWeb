import customtkinter as ctk
from tkinter import messagebox, Canvas
from interfaz_utils import VentanaBase
import math

class VentanaAhorcado(VentanaBase):
    def __init__(self, maestro, engine, *args, **kwargs):
        super().__init__(maestro, "Lexicon - El Ahorcado")
        self.engine = engine
        
        self.palabra_secreta, self.pista = self.engine.obtener_palabra_azar()
        
        if not self.palabra_secreta:
            messagebox.showwarning("Aviso", "Añade palabras con definición al diccionario primero.")
            self.destroy()
            return
            
        self.intentos_restantes = 6
        self.letras_adivinadas = []
        self.letras_falladas = []
        self.game_over = False
        self.teclado_buttons = []
        
        self.setup_ui()
        self.set_dynamic_size()
        self.actualizar_pantalla()
        
        self.lift()                                 
        self.focus_force()                           
        self.attributes('-topmost', True)           
        self.after(500, lambda: self.attributes('-topmost', False))

    def set_dynamic_size(self):
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        ancho = min(900, int(screen_w * 0.85))
        alto = min(850, int(screen_h * 0.8))
        self.centrar(ancho, alto)

    def setup_ui(self):
        # Canvas ahorcado
        self.canvas_ahorcado = Canvas(self, width=280, height=420, bg='white', highlightthickness=0)
        self.canvas_ahorcado.pack(pady=(20,10))

        # Palabra
        self.lbl_palabra = ctk.CTkLabel(self, text="", font=("Arial", 32, "bold"), text_color="#1f538d")
        self.lbl_palabra.pack(pady=10)

        # Pista
        pista_limpia = self.pista.replace('\n', ' ') if self.pista else "Sin pista disponible"
        self.lbl_pista = ctk.CTkLabel(self, text=f"Pista: {pista_limpia[:120]}...", font=("Arial", 12, "italic"), wraplength=650)
        self.lbl_pista.pack(pady=(10,20))

        # Scrollable teclado
        self.scroll_teclado = ctk.CTkScrollableFrame(self, height=200)
        self.scroll_teclado.pack(fill="x", padx=40, pady=10)
        
        self.f_teclado = ctk.CTkFrame(self.scroll_teclado, fg_color="transparent")
        self.f_teclado.pack(pady=10, padx=10, fill="x")

        alfabeto = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
        for i, letra in enumerate(alfabeto):
            btn = ctk.CTkButton(self.f_teclado, text=letra, width=45, height=50,
                               font=("Arial", 14, "bold"),
                               command=lambda l=letra: self.probar_letra(l))
            btn.grid(row=i//9, column=i%9, padx=4, pady=4)
            self.teclado_buttons.append(btn)

        # Win frame overlay
        self.win_frame = ctk.CTkFrame(self, fg_color="#90EE90")
        self.canvas_win = Canvas(self.win_frame, width=500, height=300, bg="#90EE90", highlightthickness=0)
        self.canvas_win.pack(pady=20)
        ctk.CTkLabel(self.win_frame, text="¡GANASTE!", font=("Arial", 40, "bold"), text_color="#228B22").pack(pady=10)
        self.btn_cerrar_win = ctk.CTkButton(self.win_frame, text="Cerrar", width=200, fg_color="darkgreen", command=self.cerrar_juego)
        self.btn_cerrar_win.pack(pady=20)
        self.win_frame.place_forget()

        # Lose frame overlay
        self.lose_frame = ctk.CTkFrame(self, fg_color="#8B0000")
        self.canvas_lose = Canvas(self.lose_frame, width=500, height=300, bg="#8B0000", highlightthickness=0)
        self.canvas_lose.pack(pady=20)
        ctk.CTkLabel(self.lose_frame, text="¡PERDISTE!", font=("Arial", 40, "bold"), text_color="red").pack(pady=10)
        self.btn_cerrar_lose = ctk.CTkButton(self.lose_frame, text="Cerrar", width=200, fg_color="darkred", command=self.cerrar_juego)
        self.btn_cerrar_lose.pack(pady=20)
        self.lose_frame.place_forget()

    def actualizar_pantalla(self):
        self.canvas_ahorcado.delete("all")
        
        # Horca
        self.canvas_ahorcado.create_line(50, 50, 50, 100, width=8, fill='brown')
        self.canvas_ahorcado.create_line(50, 100, 140, 100, width=8, fill='brown')
        self.canvas_ahorcado.create_line(140, 100, 140, 130, width=8, fill='brown')
        self.canvas_ahorcado.create_line(140, 130, 110, 130, width=6, fill='brown')
        self.canvas_ahorcado.create_line(110, 130, 110, 350, width=8, fill='brown')
        self.canvas_ahorcado.create_line(80, 150, 110, 130, width=4, fill='sienna')

        errores = 6 - self.intentos_restantes
        if errores >= 1:
            self.canvas_ahorcado.create_oval(95, 135, 125, 165, fill='peachpuff', outline='black', width=4)
        if errores >= 2:
            self.canvas_ahorcado.create_line(110, 165, 110, 240, width=8, fill='black')
        if errores >= 3:
            self.canvas_ahorcado.create_line(110, 185, 135, 205, width=8, fill='black')
        if errores >= 4:
            self.canvas_ahorcado.create_line(110, 185, 85, 205, width=8, fill='black')
        if errores >= 5:
            self.canvas_ahorcado.create_line(110, 240, 95, 290, width=8, fill='black')
        if errores >= 6:
            self.canvas_ahorcado.create_line(110, 240, 125, 290, width=8, fill='black')

        mostrada = ""
        ganado = True
        for letra_p in self.palabra_secreta.upper():
            letra_check = letra_p.replace('Á','A').replace('É','E').replace('Í','I').replace('Ó','O').replace('Ú','U')
            if letra_check in self.letras_adivinadas or not letra_p.isalpha():
                mostrada += letra_p + " "
            else:
                mostrada += "_ "
                ganado = False
        self.lbl_palabra.configure(text=mostrada)

        if ganado and not self.game_over:
            self.mostrar_victoria()
        elif self.intentos_restantes == 0 and not self.game_over:
            self.mostrar_derrota()

    def probar_letra(self, letra):
        if self.game_over:
            return
        if letra in self.letras_adivinadas or letra in self.letras_falladas:
            return
            
        palabra_norm = self.palabra_secreta.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
        
        if letra.lower() in palabra_norm:
            self.letras_adivinadas.append(letra)
        else:
            self.letras_falladas.append(letra)
            self.intentos_restantes -= 1
            
        self.actualizar_pantalla()

    def cerrar_juego(self):
        self.destroy()

    def mostrar_victoria(self):
        self.game_over = True
        for btn in self.teclado_buttons:
            btn.configure(state="disabled")
        self.canvas_win.delete("all")
        self.canvas_win.create_oval(150, 80, 350, 280, fill="yellow", outline="orange", width=10)
        self.canvas_win.create_arc(190, 160, 310, 220, start=0, extent=-180, style="arc", outline="black", width=10)
        self.canvas_win.create_oval(200, 120, 230, 150, fill="black")
        self.canvas_win.create_oval(270, 120, 300, 150, fill="black")
        colors = ['red', 'blue', 'green', 'gold', 'purple', 'orange']
        for i in range(30):
            x = 30 + (i * 17) % 470
            y = 30 + (i * 13) % 250
            self.canvas_win.create_polygon(x, y, x+15, y, x+8, y+15, fill=colors[i % 6])
        self.canvas_win.create_text(250, 20, text=f"¡Ganaste! {self.palabra_secreta.upper()}", font=("Arial", 20, "bold"), fill="#228B22")
        self.win_frame.place(relx=0.5, rely=0.5, anchor="center")

    def mostrar_derrota(self):
        self.game_over = True
        for btn in self.teclado_buttons:
            btn.configure(state="disabled")
        self.canvas_lose.delete("all")
        self.canvas_lose.create_oval(150, 70, 350, 270, fill="#F5DEB3", outline="black", width=8)
        self.canvas_lose.create_arc(170, 130, 330, 240, start=0, extent=180, style="arc", outline="black", width=8)
        self.canvas_lose.create_oval(195, 115, 235, 155, fill="#8B4513")
        self.canvas_lose.create_oval(265, 115, 305, 155, fill="#8B4513")
        for i in range(7):
            x = 185 + i * 25
            self.canvas_lose.create_rectangle(x, 225, x + 18, 245, fill="white", outline="#696969")
        self.canvas_lose.create_text(250, 20, text=f"¡Perdiste! {self.palabra_secreta.upper()}", font=("Arial", 20, "bold"), fill="darkred")
        self.lose_frame.place(relx=0.5, rely=0.5, anchor="center")

