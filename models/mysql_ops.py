import uuid

class MySQLOperations:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = None
        self.crear_cursor()

    def crear_cursor(self):
        if self.cursor:
            try:
                self.cursor.close()
            except:
                pass
        self.cursor = self.connection.cursor(dictionary=True)

    def ejecutar_consulta(self, query, params=None):
        try:
            self.crear_cursor()
            self.cursor.execute(query, params)
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.connection.commit()
                return None
            resultado = self.cursor.fetchall()
            return resultado[0] if query.strip().upper().startswith('SELECT') and len(resultado) == 1 else resultado
        except Exception as e:
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                self.connection.rollback()
            raise e

    def crear_usuario(self, nombre, correo, contrasena, pais):
        id_usuario = str(uuid.uuid4())
        query = """
        INSERT INTO usuarios (id_usuario, nombre_usuario, correo, contrasena_hash, pais)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.ejecutar_consulta(query, (id_usuario, nombre, correo, contrasena, pais))
        return id_usuario

    def crear_canal(self, id_usuario, nombre_canal, descripcion=""):
        id_canal = str(uuid.uuid4())
        query = """
        INSERT INTO canales (id_canal, id_usuario, nombre_canal, descripcion)
        VALUES (%s, %s, %s, %s)
        """
        self.ejecutar_consulta(query, (id_canal, id_usuario, nombre_canal, descripcion))
        return id_canal

    def iniciar_transmision(self, id_canal, titulo, id_categoria=None):
        id_transmision = str(uuid.uuid4())
        query = """
        INSERT INTO transmisiones (id_transmision, id_canal, id_categoria, titulo, estado)
        VALUES (%s, %s, %s, %s, 'en_vivo')
        """
        self.ejecutar_consulta(query, (id_transmision, id_canal, id_categoria, titulo))
        return id_transmision

    def obtener_canal_por_usuario(self, id_usuario):
        query = "SELECT * FROM canales WHERE id_usuario = %s"
        return self.ejecutar_consulta(query, (id_usuario,))

    def finalizar_transmision(self, id_transmision):
        query = """
        UPDATE transmisiones 
        SET estado = 'finalizado', fin = CURRENT_TIMESTAMP
        WHERE id_transmision = %s
        """
        self.ejecutar_consulta(query, (id_transmision,))

    def listar_canales(self):
        query = """
        SELECT c.*, u.nombre_usuario
        FROM canales c
        JOIN usuarios u ON c.id_usuario = u.id_usuario
        """
        return self.ejecutar_consulta(query)

    def listar_usuarios(self):
        return self.ejecutar_consulta("SELECT * FROM usuarios")

    def obtener_usuario_por_correo(self, correo):
        query = "SELECT * FROM usuarios WHERE correo = %s"
        return self.ejecutar_consulta(query, (correo,))

    def obtener_transmisiones_activas(self):
        query = """
        SELECT t.*, c.nombre_canal, u.nombre_usuario
        FROM transmisiones t
        JOIN canales c ON t.id_canal = c.id_canal
        JOIN usuarios u ON c.id_usuario = u.id_usuario
        WHERE t.estado = 'en_vivo'
        """
        return self.ejecutar_consulta(query)

    def seguir_canal(self, id_usuario, id_canal):
        query = """
        INSERT INTO seguidores (id_usuario, id_canal)
        VALUES (%s, %s)
        """
        self.ejecutar_consulta(query, (id_usuario, id_canal))

    def dejar_seguir_canal(self, id_usuario, id_canal):
        query = "DELETE FROM seguidores WHERE id_usuario = %s AND id_canal = %s"
        self.ejecutar_consulta(query, (id_usuario, id_canal))

    def obtener_transmision_activa_por_usuario(self, id_usuario):
        query = """
        SELECT t.*
        FROM transmisiones t
        JOIN canales c ON t.id_canal = c.id_canal
        WHERE c.id_usuario = %s AND t.estado = 'en_vivo'
        """
        return self.ejecutar_consulta(query, (id_usuario,))

    def esta_siguiendo(self, id_usuario, id_canal):
        query = "SELECT * FROM seguidores WHERE id_usuario = %s AND id_canal = %s"
        resultado = self.ejecutar_consulta(query, (id_usuario, id_canal))
        return resultado is not None and len(resultado) > 0

    def obtener_canal_por_nombre(self, nombre_canal):
        query = "SELECT * FROM canales WHERE nombre_canal = %s"
        return self.ejecutar_consulta(query, (nombre_canal,))

    def obtener_usuario_por_id(self, id_usuario):
        query = "SELECT * FROM usuarios WHERE id_usuario = %s"
        return self.ejecutar_consulta(query, (id_usuario,))

    def actualizar_perfil(self, id_usuario, pais, biografia):
        query = """
        UPDATE usuarios 
        SET pais = %s, biografia = %s
        WHERE id_usuario = %s
        """
        self.ejecutar_consulta(query, (pais, biografia, id_usuario))
        
        # Actualizar es_streamer si tiene canal
        query_canal = "SELECT id_canal FROM canales WHERE id_usuario = %s"
        tiene_canal = self.ejecutar_consulta(query_canal, (id_usuario,))
        
        if tiene_canal:
            query_streamer = "UPDATE usuarios SET es_streamer = TRUE WHERE id_usuario = %s"
            self.ejecutar_consulta(query_streamer, (id_usuario,))

    def crear_categoria(self, nombre, imagen=""):
        id_categoria = str(uuid.uuid4())
        query = """
        INSERT INTO categorias (id_categoria, nombre, imagen)
        VALUES (%s, %s, %s)
        """
        self.ejecutar_consulta(query, (id_categoria, nombre, imagen))
        return id_categoria

    def listar_categorias(self):
        query = "SELECT * FROM categorias"
        try:
            resultado = self.ejecutar_consulta(query)
            if isinstance(resultado, dict):  # Si es un solo resultado
                return [resultado]
            elif isinstance(resultado, list):  # Si son múltiples resultados
                return resultado
            return []  # Si no hay resultados
        except Exception as e:
            print(f"Error al listar categorías: {e}")
            return []

    def obtener_transmisiones_por_categoria(self, id_categoria):
        query = """
        SELECT t.*, c.nombre_canal, u.nombre_usuario, cat.nombre as categoria
        FROM transmisiones t
        JOIN canales c ON t.id_canal = c.id_canal
        JOIN usuarios u ON c.id_usuario = u.id_usuario
        JOIN categorias cat ON t.id_categoria = cat.id_categoria
        WHERE t.id_categoria = %s AND t.estado = 'en_vivo'
        """
        try:
            resultado = self.ejecutar_consulta(query, (id_categoria,))
            if isinstance(resultado, dict):  # Si es un solo resultado
                return [resultado]
            elif isinstance(resultado, list):  # Si son múltiples resultados
                return resultado
            return []  # Si no hay resultados
        except Exception as e:
            print(f"Error al obtener transmisiones por categoría: {e}")
            return []

    def obtener_canales_seguidos(self, id_usuario):
        query = """
        SELECT c.*, u.nombre_usuario
        FROM seguidores s
        JOIN canales c ON s.id_canal = c.id_canal
        JOIN usuarios u ON c.id_usuario = u.id_usuario
        WHERE s.id_usuario = %s
        """
        try:
            resultado = self.ejecutar_consulta(query, (id_usuario,))
            if isinstance(resultado, dict):  # Si es un solo resultado
                return [resultado]
            elif isinstance(resultado, list):  # Si son múltiples resultados
                return resultado
            return []  # Si no hay resultados
        except Exception as e:
            print(f"Error al obtener canales seguidos: {e}")
            return []
    
    def obtener_canales_por_usuario(self, id_usuario):
        query = """
        SELECT * FROM canales WHERE id_usuario = %s
        """
        resultado = self.ejecutar_consulta(query, (id_usuario,))
        return resultado if isinstance(resultado, list) else [resultado] if resultado else []
    

    def obtener_transmisiones_activas(self):
        query = """
        SELECT t.*, c.nombre_canal, u.nombre_usuario
        FROM transmisiones t
        JOIN canales c ON t.id_canal = c.id_canal
        JOIN usuarios u ON c.id_usuario = u.id_usuario
        WHERE t.estado = 'en_vivo'
        """
        try:
            resultado = self.ejecutar_consulta(query)
            return resultado if isinstance(resultado, list) else []
        except Exception as e:
            print(f"Error al obtener transmisiones: {e}")
            return []