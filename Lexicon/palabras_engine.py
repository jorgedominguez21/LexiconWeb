import psycopg2
from database import Database
from collections import OrderedDict

class PalabrasEngine:
    def __init__(self):
        self.db = Database()
        self._cache = OrderedDict()

    def insertar(self, termino, definicion, tipo):
        """Inserta palabra y categoría. Limpia caché para reflejar cambios."""
        if not termino.strip(): return "Error: El término no puede estar vacío"
        
        termino = termino.strip().lower()
        self._cache.clear()
        
        sql = "INSERT INTO palabras (termino, definicion, tipo) VALUES (%s, %s, %s)"
        return self._ejecutar(sql, (termino, definicion, tipo))

    def actualizar(self, id_p, termino, definicion, tipo):
        """Actualiza ficha completa. Limpia caché para evitar datos obsoletos."""
        if not id_p: return "Error: ID no válido"
        if not termino.strip(): return "Error: El término no puede estar vacío"
        
        termino = termino.strip().lower()
        self._cache.clear()
        
        sql = "UPDATE palabras SET termino=%s, definicion=%s, tipo=%s WHERE id=%s"
        return self._ejecutar(sql, (termino, definicion, tipo, id_p))

    def eliminar(self, id_p):
        """Borra la palabra y limpia caché."""
        if not id_p: return "Error: ID no válido"
        self._cache.clear()
        return self._ejecutar("DELETE FROM palabras WHERE id = %s", (id_p,))

    def listar_rapido(self, filtro="", limit=100):
        """
        Buscador inteligente: 
        - En Nube: Usa la función inmutable para ignorar tildes.
        - En Local: Usa ILIKE estándar.
        """
        filtro = filtro.strip().lower()
        # El cache separa por entorno para no mostrar datos viejos al cambiar de pestaña
        cache_key = f"busq_{self.db.entorno}_{filtro}_{limit}"

        if cache_key in self._cache:
            return self._cache[cache_key]
        
        if not filtro:
            # Listado inicial (sin búsqueda)
            sql = "SELECT id, termino, tipo, definicion FROM palabras ORDER BY termino ASC LIMIT %s"
            params = (limit,)
        else:
            # --- LÓGICA DE BÚSQUEDA SEGÚN ENTORNO ---
            if self.db.entorno == 'nube':
                # IMPORTANTE: En la nube forzamos el uso de la función de acentos
                sql = """
                    SELECT id, termino, tipo, definicion
                    FROM palabras 
                    WHERE public.immutable_unaccent(termino) ILIKE public.immutable_unaccent(%s)
                    ORDER BY termino ASC
                    LIMIT %s
                """
                # Mandamos el filtro con los comodines % directamente
                params = (f"%{filtro}%", limit)
            else:
                # En local (Postgres normal o SQLite) usamos el ILIKE de toda la vida
                sql = """
                    SELECT id, termino, tipo, definicion
                    FROM palabras 
                    WHERE termino ILIKE %s
                    ORDER BY termino ASC
                    LIMIT %s
                """
                params = (f"%{filtro}%", limit)
            
        res = self._consultar(sql, params)
        self._cache[cache_key] = res
        return res

    def obtener_palabra_azar(self):
        """Retorna una palabra aleatoria para el juego del Ahorcado."""
        sql = "SELECT termino, definicion, tipo FROM palabras ORDER BY RANDOM() LIMIT 1"
        res = self._consultar(sql)
        return res[0] if res else (None, None, None)

    def contar_total(self):
        """Devuelve el número total de palabras para el contador del panel."""
        sql = "SELECT COUNT(*) FROM palabras"
        res = self._consultar(sql)
        if res and len(res) > 0:
            return res[0][0]
        return 0

    # --- MÉTODOS INTERNOS DE CONEXIÓN (NO TOCAR) ---
    def _ejecutar(self, sql, params):
        conn = None
        try:
            conn = self.db.obtener_conexion()
            if not conn: return "Error: No hay conexión"
            cur = conn.cursor()
            cur.execute(sql, params)
            conn.commit()
            cur.close()
            return "OK"
        except psycopg2.errors.UniqueViolation:
            return "EXISTE"
        except Exception as e:
            return f"Error DB: {str(e)}"
        finally:
            if conn:
                self.db.devolver_conexion(conn)

    def _consultar(self, sql, params=None):
        conn = None
        try:
            conn = self.db.obtener_conexion()
            if not conn: return []
            cur = conn.cursor()
            cur.execute(sql, params)
            res = cur.fetchall()
            cur.close()
            return res
        except Exception as e:
            print(f"Error en consulta ({self.db.entorno}): {e}")
            return []
        finally:
            if conn:
                self.db.devolver_conexion(conn)