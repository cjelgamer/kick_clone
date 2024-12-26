from datetime import datetime

class MongoOperations:
    def __init__(self, db, mysql_ops=None):
        self.db = db
        self.mensajes = db.mensajes_chat
        self.estados = db.estados_transmision
        self.mysql_ops = mysql_ops

    def crear_mensaje(self, id_canal, id_usuario, contenido, nombre_usuario=None):
        mensaje = {
            "id_canal": id_canal,
            "id_usuario": id_usuario,
            "nombre_usuario": nombre_usuario,
            "contenido": contenido,
            "timestamp": datetime.now(),
            "tipo": "mensaje"
        }
        
        # Si no se proporcionó nombre_usuario y tenemos mysql_ops, intentamos obtenerlo
        if nombre_usuario is None and self.mysql_ops:
            try:
                usuario = self.mysql_ops.obtener_usuario_por_id(id_usuario)
                if usuario:
                    mensaje["nombre_usuario"] = usuario["nombre_usuario"]
            except Exception as e:
                print(f"Error al obtener nombre de usuario: {e}")
                
        resultado = self.mensajes.insert_one(mensaje)
        return resultado.inserted_id

    def listar_mensajes(self, id_canal):
        mensajes = list(self.mensajes.find({"id_canal": id_canal}).sort("timestamp", 1))  # Orden ascendente por timestamp
        
        # Enriquecer mensajes que no tengan nombre_usuario y agregar hora formateada
        mensajes_enriquecidos = []
        if self.mysql_ops:
            for msg in mensajes:
                if 'nombre_usuario' not in msg:
                    try:
                        usuario = self.mysql_ops.obtener_usuario_por_id(msg['id_usuario'])
                        if usuario:
                            msg['nombre_usuario'] = usuario['nombre_usuario']
                    except Exception as e:
                        print(f"Error al obtener nombre de usuario: {e}")
                        msg['nombre_usuario'] = "Usuario Desconocido"
                
                # Formatear el timestamp a una cadena de hora legible
                if 'timestamp' in msg:
                    msg['hora'] = msg['timestamp'].strftime('%H:%M:%S')  # Formato HH:MM:SS

                mensajes_enriquecidos.append(msg)
        else:
            for msg in mensajes:
                if 'timestamp' in msg:
                    msg['hora'] = msg['timestamp'].strftime('%H:%M:%S')
                mensajes_enriquecidos.append(msg)

        return mensajes_enriquecidos
