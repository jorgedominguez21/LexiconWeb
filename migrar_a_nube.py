import psycopg2

# 1. TUS DATOS LOCALES (Donde tienes las 20 palabras ahora)
config_local = {
    "dbname": "lexicon", 
    "user": "postgres",
    "password": "postgres", # <--- CAMBIA ESTO
    "host": "localhost"
}

# TUS DATOS DE SUPABASE CORREGIDOS
config_nube = {
    "host": "aws-1-eu-west-1.pooler.supabase.com", # <--- CAMBIADO A aws-1 e irlanda
    "port": "6543",
    "user": "postgres.kkfyyedgtiqfkxqniuxg",
    "password": "Token..21$2006", 
    "dbname": "postgres",
    "sslmode": "require"
}

def migrar():
    conn_loc = None
    conn_nub = None
    
    try:
        print("--- Iniciando migración de Lexicon Studio ---")
        
        # Conectar a local
        conn_loc = psycopg2.connect(**config_local)
        cur_loc = conn_loc.cursor()
        
        # Leer las palabras
        print("🔎 Leyendo palabras del PC local...")
        cur_loc.execute("SELECT termino, inicial, definicion FROM palabras")
        filas = cur_loc.fetchall()
        total = len(filas)
        print(f"✅ Se han encontrado {total} palabras.")

        # Conectar a la nube
        print("🚀 Conectando a Supabase...")
        conn_nub = psycopg2.connect(**config_nube)
        cur_nub = conn_nub.cursor()

        # Insertar en la nube
        print("📤 Subiendo datos...")
        for i, fila in enumerate(filas, 1):
            cur_nub.execute(
                "INSERT INTO palabras (termino, inicial, definicion) VALUES (%s, %s, %s)",
                fila
            )
            if i % 5 == 0: print(f"   Procesadas {i}/{total}...")

        conn_nub.commit()
        print("-" * 40)
        print(f"✨ ¡MIGRACIÓN COMPLETADA! {total} palabras ya están en la nube.")
        print("-" * 40)

    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        if conn_loc: conn_loc.close()
        if conn_nub: conn_nub.close()

if __name__ == "__main__":
    migrar()