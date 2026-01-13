import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "http://localhost:8080"

class DvdApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Renta DVD")
        self.root.geometry("600x500")

        # Tabs
        tab_control = ttk.Notebook(root)
        self.tab_rentar = ttk.Frame(tab_control)
        self.tab_reportes = ttk.Frame(tab_control)
        
        tab_control.add(self.tab_rentar, text='Gestión Rentas')
        tab_control.add(self.tab_reportes, text='Reportes')
        tab_control.pack(expand=1, fill="both")

        self.setup_rentar_tab()
        self.setup_reportes_tab()

    def setup_rentar_tab(self):
        frame = ttk.LabelFrame(self.tab_rentar, text="Nueva Renta")
        frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(frame, text="Cliente:").grid(row=0, column=0)
        self.entry_cliente = ttk.Entry(frame)
        self.entry_cliente.grid(row=0, column=1)

        ttk.Label(frame, text="DVD Título:").grid(row=1, column=0)
        self.entry_dvd = ttk.Entry(frame)
        self.entry_dvd.grid(row=1, column=1)

        ttk.Label(frame, text="Staff ID:").grid(row=2, column=0)
        self.entry_staff = ttk.Entry(frame)
        self.entry_staff.grid(row=2, column=1)

        ttk.Label(frame, text="Costo:").grid(row=3, column=0)
        self.entry_costo = ttk.Entry(frame)
        self.entry_costo.grid(row=3, column=1)

        btn_rentar = ttk.Button(frame, text="Rentar", command=self.rentar)
        btn_rentar.grid(row=4, column=1, pady=10)

        # Acciones Devolución
        frame_acc = ttk.LabelFrame(self.tab_rentar, text="Acciones por ID")
        frame_acc.pack(padx=10, pady=10, fill="x")
        
        ttk.Label(frame_acc, text="ID Renta:").grid(row=0, column=0)
        self.entry_id = ttk.Entry(frame_acc)
        self.entry_id.grid(row=0, column=1)
        
        ttk.Button(frame_acc, text="Devolver DVD", command=self.devolver).grid(row=1, column=0, pady=5)
        ttk.Button(frame_acc, text="Cancelar Renta", command=self.cancelar).grid(row=1, column=1, pady=5)

    def setup_reportes_tab(self):
        frame = ttk.Frame(self.tab_reportes)
        frame.pack(pady=10)

        ttk.Button(frame, text="Ver Pendientes", command=self.ver_pendientes).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Ganancia por Staff", command=self.ver_ganancias).pack(side=tk.LEFT, padx=5)
        
        self.text_area = tk.Text(self.tab_reportes, height=20, width=70)
        self.text_area.pack(pady=10)

    # --- Lógica de Conexión ---
    def rentar(self):
        data = {
            "id": 0, # El backend lo asigna
            "cliente": self.entry_cliente.get(),
            "dvd_titulo": self.entry_dvd.get(),
            "staff_id": self.entry_staff.get(),
            "costo": float(self.entry_costo.get()),
            "fecha_renta": "2023-01-01T00:00:00Z", # Placeholder, backend lo sobreescribe
            "devuelto": False
        }
        try:
            r = requests.post(f"{API_URL}/rentar", json=data)
            if r.status_code == 201:
                messagebox.showinfo("Éxito", "Renta realizada")
            else:
                messagebox.showerror("Error", "No se pudo rentar")
        except:
            messagebox.showerror("Error", "Backend no disponible")

    def devolver(self):
        rid = self.entry_id.get()
        requests.put(f"{API_URL}/devolver/{rid}")
        messagebox.showinfo("Info", "Solicitud enviada")

    def cancelar(self):
        rid = self.entry_id.get()
        requests.delete(f"{API_URL}/cancelar/{rid}")
        messagebox.showinfo("Info", "Solicitud enviada")

    def ver_pendientes(self):
        r = requests.get(f"{API_URL}/reporte/pendientes")
        data = r.json()
        self.mostrar_lista(data)

    def ver_ganancias(self):
        r = requests.get(f"{API_URL}/reporte/general") # Trae todo
        data = r.json()
        
        # Calculamos ganancia por staff en el cliente (Front)
        staff_ganancia = {}
        for renta in data:
            staff = renta['staff_id']
            costo = renta['costo']
            staff_ganancia[staff] = staff_ganancia.get(staff, 0) + costo
            
        texto = "Ganancia por Staff:\n"
        for s, g in staff_ganancia.items():
            texto += f"Staff {s}: ${g}\n"
        
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, texto)

    def mostrar_lista(self, data):
        self.text_area.delete(1.0, tk.END)
        for item in data:
            self.text_area.insert(tk.END, f"ID: {item['id']} | Cliente: {item['cliente']} | DVD: {item['dvd_titulo']} | Devuelto: {item['devuelto']}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = DvdApp(root)
    root.mainloop()
