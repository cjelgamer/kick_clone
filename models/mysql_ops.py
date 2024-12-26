import uuid

class MySQLOperations:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor(dictionary=True)

    def crear_usuario(self, nombre, correo, contrasena, pais):
        id_usuario = str(uuid.uuid4())
        query = """
        INSERT INTO usuarios (id_usuario, nombre_usuario, correo, contrasena_hash, pais)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (id_usuario, nombre, correo, contrasena, pais))
            self.connection.commit()
            return id_usuario
        except Exception as e:
            self.connection.rollback()
            raise e

    def crear_canal(self, id_usuario, nombre_canal, descripcion=""):
        try:
            id_canal = str(uuid.uuid4())
            query = """
            INSERT INTO canales (id_canal, id_usuario, nombre_canal, descripcion)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(query, (id_canal, id_usuario, nombre_canal, descripcion))
            self.connection.commit()
            return id_canal
        except Exception as e:
            self.connection.rollback()
            raise e

    def iniciar_transmision(self, id_canal, titulo, id_categoria=None):
        try:
            id_transmision = str(uuid.uuid4())
            query = """
            INSERT INTO transmisiones (id_transmision, id_canal, id_categoria, titulo, estado)
            VALUES (%s, %s, %s, %s, 'en_vivo')
            """
            self.cursor.execute(query, (id_transmision, id_canal, id_categoria, titulo))
            self.connection.commit()
            return id_transmision
        except Exception as e:
            self.connection.rollback()
            raise e

    def obtener_canal_por_usuario(self, id_usuario):
        query = "SELECT * FROM canales WHERE id_usuario = %s"
        try:
            self.cursor.execute(query, (id_usuario,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener canal: {e}")
            return None

    def finalizar_transmision(self, id_transmision):
        query = """
        UPDATE transmisiones 
        SET estado = 'finalizado', fin = CURRENT_TIMESTAMP
        WHERE id_transmision = %s
        """
        try:
            self.cursor.execute(query, (id_transmision,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e

    def listar_canales(self):
        query = """
        SELECT c.*, u.nombre_usuario
        FROM canales c
        JOIN usuarios u ON c.id_usuario = u.id_usuario
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def listar_usuarios(self):
        self.cursor.execute("SELECT * FROM usuarios")
        return self.cursor.fetchall()

    def obtener_usuario_por_correo(self, correo):
        try:
            query = "SELECT * FROM usuarios WHERE correo = %s"
            self.cursor.execute(query, (correo,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None

    def obtener_transmisiones_activas(self):
        try:
            query = """
            SELECT t.*, c.nombre_canal, u.nombre_usuario
            FROM transmisiones t
            JOIN canales c ON t.id_canal = c.id_canal
            JOIN usuarios u ON c.id_usuario = u.id_usuario
            WHERE t.estado = 'en_vivo'
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener transmisiones: {e}")
            return []
        
    def seguir_canal(self, id_usuario, id_canal):
        try:
            query = """
            INSERT INTO seguidores (id_usuario, id_canal)
            VALUES (%s, %s)
            """
            self.cursor.execute(query, (id_usuario, id_canal))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
    
    def dejar_seguir_canal(self, id_usuario, id_canal):
        try:
            query = "DELETE FROM seguidores WHERE id_usuario = %s AND id_canal = %s"
            self.cursor.execute(query, (id_usuario, id_canal))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
    
    def obtener_transmision_activa_por_usuario(self, id_usuario):
        try:
            query = """
            SELECT t.*
            FROM transmisiones t
            JOIN canales c ON t.id_canal = c.id_canal
            WHERE c.id_usuario = %s AND t.estado = 'en_vivo'
            """
            self.cursor.execute(query, (id_usuario,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener transmisión activa: {e}")
        return None    
    

    def esta_siguiendo(self, id_usuario, id_canal):
        try:
            query = "SELECT * FROM seguidores WHERE id_usuario = %s AND id_canal = %s"
            self.cursor.execute(query, (id_usuario, id_canal))
            return self.cursor.fetchone() is not None
        except Exception as e:
            print(f"Error al verificar seguimiento: {e}")
            return False
    
    def obtener_canal_por_nombre(self, nombre_canal):
        try:
            query = "SELECT * FROM canales WHERE nombre_canal = %s"
            self.cursor.execute(query, (nombre_canal,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener canal: {e}")
            return None
        
    def obtener_usuario_por_id(self, id_usuario):
        try:
            query = "SELECT * FROM usuarios WHERE id_usuario = %s"
            self.cursor.execute(query, (id_usuario,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
        


    def actualizar_perfil(self, id_usuario, pais, biografia):
        try:
            query = """
            UPDATE usuarios 
            SET pais = %s, biografia = %s
            WHERE id_usuario = %s
            """
            self.cursor.execute(query, (pais, biografia, id_usuario))
            
            # Actualizar es_streamer si tiene canal
            query_canal = "SELECT id_canal FROM canales WHERE id_usuario = %s"
            self.cursor.execute(query_canal, (id_usuario,))
            tiene_canal = self.cursor.fetchone() is not None
            
            if tiene_canal:
                query_streamer = "UPDATE usuarios SET es_streamer = TRUE WHERE id_usuario = %s"
                self.cursor.execute(query_streamer, (id_usuario,))
            
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        

    def crear_categoria(self, nombre, imagen=""):
        try:
            id_categoria = str(uuid.uuid4())
            query = """
            INSERT INTO categorias (id_categoria, nombre, imagen)
            VALUES (%s, %s, %s)
            """
            self.cursor.execute(query, (id_categoria, nombre, imagen))
            self.connection.commit()
            return id_categoria
        except Exception as e:
            self.connection.rollback()
            raise e
    
    def listar_categorias(self):
        try:
            query = "SELECT * FROM categorias"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al listar categorías: {e}")
            return []
    
    def obtener_transmisiones_por_categoria(self, id_categoria):
        try:
            query = """
            SELECT t.*, c.nombre_canal, u.nombre_usuario, cat.nombre as categoria
            FROM transmisiones t
            JOIN canales c ON t.id_canal = c.id_canal
            JOIN usuarios u ON c.id_usuario = u.id_usuario
            JOIN categorias cat ON t.id_categoria = cat.id_categoria
            WHERE t.id_categoria = %s AND t.estado = 'en_vivo'
            """
            self.cursor.execute(query, (id_categoria,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener transmisiones por categoría: {e}")
            return []
        
    def obtener_canales_seguidos(self, id_usuario):
        try:
            query = """
            SELECT c.*, u.nombre_usuario
            FROM seguidores s
            JOIN canales c ON s.id_canal = c.id_canal
            JOIN usuarios u ON c.id_usuario = u.id_usuario
            WHERE s.id_usuario = %s
            """
            self.cursor.execute(query, (id_usuario,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener canales seguidos: {e}")
            return []