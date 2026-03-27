import psycopg2
import configparser
import os

class SyncEngine:
    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"No se encuentra el archivo {config_file}")
        self.config.read(config_file)

    def _get_params(self, section):
        """Extrae los parámetros usando tus nombres exactos del config.ini"""
        return {
            "host": self.config.get(section, 'lexicon_host'),
            "port": self.config.get(section, 'lexicon_port'),
            "dbname": self.config.get(section, 'lexicon_db'),
            "user": self.config.get(section, 'lexicon_user'),
            "password": self.config.get(section, 'lexicon_pass')
        }

    def ejecutar_sincronizacion(self):
        conn_loc = None
        conn_nub = None
        try:
            # Conexiones
            conn_loc = psycopg2.connect(**self._get_params('postgresql_lexicon_local'))
            conn_nub = psycopg2.connect(**self._get_params('postgresql_lexicon_nube'), sslmode='require')
            
            cur_loc = conn_loc.cursor()
            cur_nub = conn_nub.cursor()

            # 1. Leer datos de Local
            cur_loc.execute("SELECT termino, definicion, tipo, inicial, updated_at FROM palabras")
            loc_data = {r[0]: {
                'termino': r[0], 'definicion': r[1], 'tipo': r[2], 
                'inicial': r[3], 'updated_at': r[4]
            } for r in cur_loc.fetchall()}
            
            # 2. Leer datos de Nube
            cur_nub.execute("SELECT termino, definicion, tipo, inicial, updated_at FROM palabras")
            nub_data = {r[0]: {
                'termino': r[0], 'definicion': r[1], 'tipo': r[2], 
                'inicial': r[3], 'updated_at': r[4]
            } for r in cur_nub.fetchall()}

            subidas, bajadas = 0, 0
            todos_los_terminos = set(loc_data.keys()) | set(nub_data.keys())

            # SQL para insertar o actualizar (UPSERT)
            sql_upsert = """
                INSERT INTO palabras (termino, definicion, tipo, inicial, updated_at)
                VALUES (%(termino)s, %(definicion)s, %(tipo)s, %(inicial)s, %(updated_at)s)
                ON CONFLICT (termino) DO UPDATE SET
                    definicion = EXCLUDED.definicion,
                    tipo = EXCLUDED.tipo,
                    inicial = EXCLUDED.inicial,
                    updated_at = EXCLUDED.updated_at;
            """

            for term in todos_los_terminos:
                l = loc_data.get(term)
                n = nub_data.get(term)

                # REGLA: Si local es más nuevo o no existe en nube -> SUBIR
                if l and (not n or l['updated_at'] > n['updated_at']):
                    cur_nub.execute(sql_upsert, l)
                    subidas += 1
                
                # REGLA: Si nube es más nueva o no existe en local -> BAJAR
                elif n and (not l or n['updated_at'] > l['updated_at']):
                    cur_loc.execute(sql_upsert, n)
                    bajadas += 1

            conn_loc.commit()
            conn_nub.commit()
            
            return f"Sincronización OK:\n- {subidas} palabras subidas a la Nube.\n- {bajadas} palabras bajadas al PC."

        except Exception as e:
            if conn_loc: conn_loc.rollback()
            if conn_nub: conn_nub.rollback()
            raise e
        finally:
            if conn_loc: conn_loc.close()
            if conn_nub: conn_nub.close()