from database import Database
import os

class MntoEngine:
    def __init__(self):
        self.db = Database()

    def verificar_y_optimizar(self):
        sql = """
        CREATE TABLE IF NOT EXISTS palabras (
            id SERIAL PRIMARY KEY,
            termino VARCHAR(100) UNIQUE NOT NULL,
            definicion TEXT NOT NULL,
            inicial CHAR(1)
        );
        CREATE INDEX IF NOT EXISTS idx_inicial ON palabras (inicial);
        """
        try:
            conn = self.db.obtener_conexion()
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            self.db.devolver_conexion(conn)
            return "✅ Base de Datos vinculada correctamente."
        except Exception as e: 
            return f"❌ Error: {e}"

    def optimizar_indices_avanzado(self):
        """Llama a optimización trigram para búsquedas rápidas"""
        return self.db.optimizar_indices()
