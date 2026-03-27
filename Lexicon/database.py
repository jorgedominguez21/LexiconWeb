import psycopg2
import psycopg2.pool
from psycopg2.pool import ThreadedConnectionPool
import configparser
import os
import sys

class Database:
    # El pool es una variable de clase (compartida) para no abrir mil conexiones
    pool = None 
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        
        # --- LÓGICA DE RUTA PARA EL .EXE ---
        if getattr(sys, 'frozen', False):
            ruta_base = os.path.dirname(sys.executable)
        else:
            ruta_base = os.path.dirname(os.path.abspath(__file__))
            
        ruta_config = os.path.join(ruta_base, 'config.ini')
        
        # Intentar leer el archivo
        leido = self.config.read(ruta_config, encoding='utf-8')
        
        if not leido:
            print(f"⚠️ Alerta: No se pudo leer el archivo config.ini en {ruta_config}")

        # 1. Miramos qué entorno hemos elegido en [SETTINGS]
        self.entorno = self.config.get('SETTINGS', 'entorno', fallback='local')
        
        # 2. Elegimos la sección correspondiente
        seccion = f'postgresql_lexicon_{self.entorno}'

        # 3. Cargamos los datos de esa sección
        try:
            self.host = self.config[seccion]['lexicon_host']
            self.port = self.config[seccion]['lexicon_port']
            self.dbname = self.config[seccion]['lexicon_db']
            self.user = self.config[seccion]['lexicon_user']
            self.password = self.config[seccion]['lexicon_pass']
            print(f"🔌 Configuración cargada para entorno: {self.entorno}")
        except KeyError:
            print(f"❌ Error Crítico: No se encontró la sección [{seccion}] en el config.ini")
            self.host = "127.0.0.1"

        # Inicializar pool si no existe (con el entorno actual)
        if Database.pool is None:
            self._crear_pool()

    def _crear_pool(self):
        """Crea el pool de conexiones"""
        try:
            sslmode = 'require' if self.entorno == 'nube' else 'prefer'
            dsn = f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password} sslmode={sslmode}"
            Database.pool = ThreadedConnectionPool(1, 20, dsn)
            print(f"✅ Pool de conexiones iniciado ({self.entorno})")
        except Exception as e:
            print(f"❌ Error creando el pool: {e}")

    @classmethod
    def reset_pool(cls):
        """
        CIERRA todas las conexiones actuales. 
        Es vital para que el botón LOCAL/NUBE funcione de verdad.
        """
        if cls.pool:
            try:
                cls.pool.closeall()
                print("🔄 Conexiones cerradas para cambio de entorno.")
            except:
                pass
            cls.pool = None

    def obtener_conexion(self):
        try:
            return Database.pool.getconn()
        except Exception as e:
            print(f"❌ Error obteniendo conexión: {e}")
            return None

    def devolver_conexion(self, conn):
        if conn and Database.pool:
            Database.pool.putconn(conn)

    def optimizar_indices(self):
        """Configura la DB para búsquedas rápidas e INSENSIBLES A ACENTOS"""
        conn = None
        try:
            conn = self.obtener_conexion()
            conn.autocommit = True
            cur = conn.cursor()
            
            # 1. Habilitar extensiones necesarias
            cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
            cur.execute("CREATE EXTENSION IF NOT EXISTS unaccent;") # PARA LOS ACENTOS
            
            # 2. Índice para búsquedas rápidas con ILIKE
            cur.execute("""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_palabras_unaccent_trgm 
                ON palabras USING gin(unaccent(termino) gin_trgm_ops);
            """)
            
            print("✅ Base de datos optimizada para tildes y velocidad.")
            return "OK"
            
        except Exception as e:
            print(f"❌ Error optimizando: {e}")
            return str(e)
        finally:
            if conn:
                conn.autocommit = False
                self.devolver_conexion(conn)