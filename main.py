import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QListWidget, QTabWidget, QMessageBox, QDialog, QGroupBox, QTextEdit,QComboBox)
from PyQt6.QtCore import Qt, QTimer
from config.database import DatabaseConnector
from models.mysql_ops import MySQLOperations
from models.mongo_ops import MongoOperations
from datetime import datetime


class RegistroDialog(QDialog):
    def __init__(self, mysql_ops, parent=None):
        super().__init__(parent)
        self.mysql_ops = mysql_ops
        self.setWindowTitle("Registro de Usuario")
        self.setModal(True)
        

        layout = QVBoxLayout()
        
        # Campos del formulario
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre de usuario")
        self.correo_input = QLineEdit()
        self.correo_input.setPlaceholderText("Correo electrónico")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pais_input = QLineEdit()
        self.pais_input.setPlaceholderText("Ingrese su país")
        
        btn_registrar = QPushButton("Registrar")
        btn_registrar.clicked.connect(self.registrar)
        
        layout.addWidget(QLabel("Registro de Usuario"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(self.correo_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.pais_input)
        layout.addWidget(btn_registrar)
        
        self.setLayout(layout)
    
    def registrar(self):
        nombre = self.nombre_input.text()
        correo = self.correo_input.text()
        password = self.password_input.text()
        pais = self.pais_input.text()
        
        if nombre and correo and password:
            try:
                id_usuario = self.mysql_ops.crear_usuario(nombre, correo, password, pais)
                QMessageBox.information(self, "Éxito", "Usuario registrado correctamente")
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al registrar: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")

class CrearCanalDialog(QDialog):
    def __init__(self, mysql_ops, id_usuario, parent=None):
        super().__init__(parent)
        self.mysql_ops = mysql_ops
        self.id_usuario = id_usuario
        self.setWindowTitle("Crear Canal")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del canal")
        self.descripcion_input = QLineEdit()
        self.descripcion_input.setPlaceholderText("Descripción")
        
        btn_crear = QPushButton("Crear Canal")
        btn_crear.clicked.connect(self.crear_canal)
        
        layout.addWidget(QLabel("Crear Nuevo Canal"))
        layout.addWidget(self.nombre_input)
        layout.addWidget(self.descripcion_input)
        layout.addWidget(btn_crear)
        
        self.setLayout(layout)
    
    def crear_canal(self):
        nombre = self.nombre_input.text()
        descripcion = self.descripcion_input.text()
        
        if nombre:
            try:
                id_canal = self.mysql_ops.crear_canal(self.id_usuario, nombre, descripcion)
                QMessageBox.information(self, "Éxito", "Canal creado correctamente")
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al crear canal: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Por favor ingrese un nombre para el canal")

class IniciarTransmisionDialog(QDialog):
    def __init__(self, mysql_ops, id_canal, parent=None):
        super().__init__(parent)
        self.mysql_ops = mysql_ops
        self.id_canal = id_canal
        self.id_transmision = None
        self.setWindowTitle("Iniciar Transmisión")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        self.titulo_input = QLineEdit()
        self.titulo_input.setPlaceholderText("Título de la transmisión")
        
        # Agregar selector de categoría
        categoria_label = QLabel("Categoría:")
        self.categoria_combo = QComboBox()
        self.cargar_categorias()
        
        btn_iniciar = QPushButton("Iniciar Transmisión")
        btn_iniciar.clicked.connect(self.iniciar_transmision)
        
        layout.addWidget(QLabel("Nueva Transmisión"))
        layout.addWidget(self.titulo_input)
        layout.addWidget(categoria_label)
        layout.addWidget(self.categoria_combo)
        layout.addWidget(btn_iniciar)
        
        self.setLayout(layout)
    
    def cargar_categorias(self):
        try:
            categorias = self.mysql_ops.listar_categorias()
            self.categoria_combo.clear()
            for categoria in categorias:
                if isinstance(categoria, dict) and 'nombre' in categoria and 'id_categoria' in categoria:
                    self.categoria_combo.addItem(categoria['nombre'], categoria['id_categoria'])
        except Exception as e:
            print(f"Error al cargar categorías: {e}")

    def iniciar_transmision(self):
        titulo = self.titulo_input.text()
        id_categoria = self.categoria_combo.currentData()
        
        if titulo:
            try:
                self.id_transmision = self.mysql_ops.iniciar_transmision(
                    self.id_canal, 
                    titulo,
                    id_categoria
                )
                QMessageBox.information(self, "Éxito", "Transmisión iniciada")
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al iniciar transmisión: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Por favor ingrese un título")

class PerfilDialog(QDialog):
    def __init__(self, mysql_ops, usuario_actual, parent=None):
        super().__init__(parent)
        self.mysql_ops = mysql_ops
        self.usuario_actual = usuario_actual
        self.setWindowTitle("Perfil de Usuario")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Información de solo lectura
        info_group = QGroupBox("Información de Usuario")
        info_layout = QVBoxLayout()
        
        self.nombre_label = QLabel(f"Nombre: {usuario_actual['nombre_usuario']}")
        self.correo_label = QLabel(f"Correo: {usuario_actual['correo']}")
        self.fecha_label = QLabel(f"Miembro desde: {usuario_actual['fecha_creacion']}")
        self.streamer_label = QLabel("Tipo: Streamer" if usuario_actual.get('es_streamer') else "Tipo: Usuario")
        
        info_layout.addWidget(self.nombre_label)
        info_layout.addWidget(self.correo_label)
        info_layout.addWidget(self.fecha_label)
        info_layout.addWidget(self.streamer_label)
        info_group.setLayout(info_layout)
        
        # Información editable
        edit_group = QGroupBox("Editar Perfil")
        edit_layout = QVBoxLayout()
        
        self.pais_input = QLineEdit(usuario_actual.get('pais', ''))
        self.pais_input.setPlaceholderText("País")
        
        self.biografia_input = QTextEdit()
        self.biografia_input.setPlaceholderText("Escribe tu biografía")
        self.biografia_input.setText(usuario_actual.get('biografia', ''))
        self.biografia_input.setMaximumHeight(100)
        
        btn_guardar = QPushButton("Guardar Cambios")
        btn_guardar.clicked.connect(self.guardar_cambios)
        
        edit_layout.addWidget(QLabel("País:"))
        edit_layout.addWidget(self.pais_input)
        edit_layout.addWidget(QLabel("Biografía:"))
        edit_layout.addWidget(self.biografia_input)
        edit_layout.addWidget(btn_guardar)
        edit_group.setLayout(edit_layout)
        
        layout.addWidget(info_group)
        layout.addWidget(edit_group)
        self.setLayout(layout)
    
    def guardar_cambios(self):
        try:
            pais = self.pais_input.text()
            biografia = self.biografia_input.toPlainText()
            
            self.mysql_ops.actualizar_perfil(
                self.usuario_actual['id_usuario'],
                pais,
                biografia
            )
            QMessageBox.information(self, "Éxito", "Perfil actualizado correctamente")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al actualizar perfil: {str(e)}")



class KickApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kick Clone")
        self.setGeometry(100, 100, 1200, 800)
        self.transmision_actual = None

        # Inicializar conexiones DB
        db_connector = DatabaseConnector()
        self.mysql_conn = db_connector.get_mysql_connection()
        self.mongo_db = db_connector.get_mongo_db()
        self.mysql_ops = MySQLOperations(self.mysql_conn)
        self.mongo_ops = MongoOperations(self.mongo_db, self.mysql_ops)

        # Usuario actual
        self.usuario_actual = None
        self.canal_seleccionado = None

        # Configurar UI principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Panel izquierdo (menú)
        self.setup_left_panel()
        
        # Panel central (contenido principal)
        self.setup_main_panel()
        
        # Panel derecho (chat/detalles)
        self.setup_right_panel()

    def setup_left_panel(self):
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Botones de navegación
        btn_inicio = QPushButton("Inicio")
        btn_inicio.clicked.connect(self.mostrar_inicio)
        btn_seguidos = QPushButton("Seguidos")
        btn_seguidos.clicked.connect(self.mostrar_seguidos)
        btn_categorias = QPushButton("Categorías")
        btn_categorias.clicked.connect(self.mostrar_categorias)
        
        self.btn_cerrar_sesion = QPushButton("Cerrar Sesión")
        self.btn_cerrar_sesion.clicked.connect(self.cerrar_sesion)
        self.btn_cerrar_sesion.hide()


        self.btn_perfil = QPushButton("Mi Perfil")
        self.btn_perfil.clicked.connect(self.mostrar_perfil)
        self.btn_perfil.hide()

        left_layout.addWidget(self.btn_perfil)
        
        self.btn_seguir = QPushButton("Seguir Canal")
        self.btn_seguir.clicked.connect(self.seguir_canal)
        self.btn_seguir.hide()
        
        left_layout.addWidget(btn_inicio)
        left_layout.addWidget(btn_seguidos)
        left_layout.addWidget(btn_categorias)
        left_layout.addWidget(self.btn_cerrar_sesion)
        left_layout.addWidget(self.btn_seguir)
        left_layout.addStretch()
        
        left_panel.setFixedWidth(200)
        self.layout.addWidget(left_panel)

    def setup_main_panel(self):
        self.main_panel = QTabWidget()
        
        # Tab de Inicio
        self.tab_inicio = QWidget()
        inicio_layout = QVBoxLayout(self.tab_inicio)
        
        # Lista de transmisiones y canales
        self.lista_transmisiones = QListWidget()
        self.lista_transmisiones.itemClicked.connect(self.seleccionar_transmision)
        self.lista_canales = QListWidget()
        self.lista_canales.itemClicked.connect(self.seleccionar_canal)
        
        inicio_layout.addWidget(QLabel("Transmisiones en Vivo"))
        inicio_layout.addWidget(self.lista_transmisiones)
        inicio_layout.addWidget(QLabel("Canales Disponibles"))
        inicio_layout.addWidget(self.lista_canales)
        
        self.main_panel.addTab(self.tab_inicio, "Inicio")
        
        # Tab de Usuario
        self.tab_usuario = QWidget()
        usuario_layout = QVBoxLayout(self.tab_usuario)
        
        # Botones de acciones
        self.btn_crear_canal = QPushButton("Crear Canal")
        self.btn_crear_canal.clicked.connect(self.mostrar_crear_canal)
        self.btn_iniciar_trans = QPushButton("Iniciar Transmisión")
        self.btn_iniciar_trans.clicked.connect(self.mostrar_iniciar_transmision)
        self.btn_finalizar_trans = QPushButton("Finalizar Transmisión")
        self.btn_finalizar_trans.clicked.connect(self.finalizar_transmision)
        
        self.btn_crear_canal.hide()
        self.btn_iniciar_trans.hide()
        self.btn_finalizar_trans.hide()
        
        usuario_layout.addWidget(self.btn_crear_canal)
        usuario_layout.addWidget(self.btn_iniciar_trans)
        usuario_layout.addWidget(self.btn_finalizar_trans)
        
        # Formulario de login
        self.setup_login_form(usuario_layout)
        
        self.main_panel.addTab(self.tab_usuario, "Usuario")
        self.layout.addWidget(self.main_panel)

    def setup_right_panel(self):
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Chat
        self.chat_label = QLabel("Seleccione una transmisión para ver el chat")
        self.chat_list = QListWidget()
        self.mensaje_input = QLineEdit()
        self.btn_enviar = QPushButton("Enviar")
        self.btn_enviar.clicked.connect(self.enviar_mensaje)
        
        # Ocultar inicialmente los componentes del chat
        self.chat_list.hide()
        self.mensaje_input.hide()
        self.btn_enviar.hide()
        
        right_layout.addWidget(self.chat_label)
        right_layout.addWidget(self.chat_list)
        right_layout.addWidget(self.mensaje_input)
        right_layout.addWidget(self.btn_enviar)
        
        right_panel.setFixedWidth(300)
        self.layout.addWidget(right_panel)
    
        # Timer para actualizar el chat
        self.chat_timer = QTimer()
        self.chat_timer.timeout.connect(self.actualizar_chat)
        self.chat_timer.setInterval(2000)  # Actualizar cada 2 segundos

    def setup_login_form(self, layout):
        self.correo_input = QLineEdit()
        self.correo_input.setPlaceholderText("Correo")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        btn_login = QPushButton("Iniciar Sesión")
        btn_login.clicked.connect(self.login)
        
        btn_registro = QPushButton("Registrarse")
        btn_registro.clicked.connect(self.mostrar_registro)
        
        layout.addWidget(self.correo_input)
        layout.addWidget(self.password_input)
        layout.addWidget(btn_login)
        layout.addWidget(btn_registro)
        layout.addStretch()

    def login(self):
        correo = self.correo_input.text()
        password = self.password_input.text()
        
        try:
            usuario = self.mysql_ops.obtener_usuario_por_correo(correo)
            if usuario and usuario['contrasena_hash'] == password:
                self.usuario_actual = usuario
                transmision_activa = self.mysql_ops.obtener_transmision_activa_por_usuario(usuario['id_usuario'])
                if transmision_activa:
                    self.transmision_actual = transmision_activa['id_transmision']
                    self.btn_finalizar_trans.show()
                
                QMessageBox.information(self, "Éxito", f"Bienvenido {usuario['nombre_usuario']}")
                self.actualizar_ui_usuario_logueado()
            else:
                QMessageBox.warning(self, "Error", "Credenciales incorrectas")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al iniciar sesión: {str(e)}")

    def cerrar_sesion(self):
        self.usuario_actual = None
        self.canal_seleccionado = None
        
        # Ocultar botones
        self.btn_crear_canal.hide()
        self.btn_iniciar_trans.hide()
        self.btn_finalizar_trans.hide()
        self.btn_cerrar_sesion.hide()
        self.btn_seguir.hide()
        
        # Limpiar campos
        self.correo_input.clear()
        self.password_input.clear()
        
        # Mostrar tab de usuario
        self.main_panel.setCurrentIndex(1)


        # Detener el timer del chat
        self.chat_timer.stop()
        # Ocultar componentes del chat
        self.chat_list.hide()
        self.mensaje_input.hide()
        self.btn_enviar.hide()
        self.chat_label.setText("Seleccione una transmisión para ver el chat")    
        
        QMessageBox.information(self, "Éxito", "Sesión cerrada correctamente")
        self.actualizar_listas()

    def actualizar_ui_usuario_logueado(self):
        if self.usuario_actual:
            self.btn_perfil.show()
            self.btn_crear_canal.show()
            self.btn_cerrar_sesion.show()
            
            # Obtener todos los canales del usuario
            canales = self.mysql_ops.obtener_canales_por_usuario(self.usuario_actual['id_usuario'])
            if canales:
                # Verificar si hay transmisiones activas en cualquiera de los canales
                for canal in canales:
                    transmision_activa = self.mysql_ops.obtener_transmision_activa_por_usuario(
                        self.usuario_actual['id_usuario']
                    )
                    if transmision_activa:
                        self.transmision_actual = transmision_activa['id_transmision']
                        self.btn_finalizar_trans.show()
                        self.btn_iniciar_trans.hide()
                        break
                else:  # Si no hay transmisiones activas
                    self.btn_iniciar_trans.show()
                    
            self.actualizar_listas()
            self.main_panel.setCurrentIndex(0)

    def mostrar_registro(self):
        dialog = RegistroDialog(self.mysql_ops, self)
        dialog.exec()

    def mostrar_crear_canal(self):
        if self.usuario_actual:
            dialog = CrearCanalDialog(self.mysql_ops, self.usuario_actual['id_usuario'], self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.actualizar_listas()

    def mostrar_iniciar_transmision(self):
        if self.usuario_actual:
            # Obtener todos los canales del usuario
            canales = self.mysql_ops.obtener_canales_por_usuario(self.usuario_actual['id_usuario'])
            if not canales:
                QMessageBox.warning(self, "Error", "Necesitas crear un canal primero")
                return
                
            if len(canales) == 1:
                # Si solo tiene un canal, usar ese
                canal = canales[0]
            else:
                # Si tiene múltiples canales, mostrar diálogo de selección
                dialogo = QDialog(self)
                dialogo.setWindowTitle("Seleccionar Canal")
                layout = QVBoxLayout()
                
                combo = QComboBox()
                for canal in canales:
                    combo.addItem(canal['nombre_canal'], canal['id_canal'])
                
                layout.addWidget(QLabel("Seleccione el canal para transmitir:"))
                layout.addWidget(combo)
                
                btn_ok = QPushButton("Seleccionar")
                btn_ok.clicked.connect(dialogo.accept)
                layout.addWidget(btn_ok)
                
                dialogo.setLayout(layout)
                
                if dialogo.exec() == QDialog.DialogCode.Accepted:
                    canal_id = combo.currentData()
                    canal = next(c for c in canales if c['id_canal'] == canal_id)
                else:
                    return
    
            # Iniciar transmisión con el canal seleccionado
            dialog = IniciarTransmisionDialog(self.mysql_ops, canal['id_canal'], self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.transmision_actual = dialog.id_transmision
                self.btn_finalizar_trans.show()
                self.btn_iniciar_trans.hide()
                self.actualizar_listas()

    def finalizar_transmision(self):
        if self.transmision_actual:
            try:
                self.mysql_ops.finalizar_transmision(self.transmision_actual)
                self.transmision_actual = None
                self.btn_finalizar_trans.hide()
                self.btn_iniciar_trans.show()
                QMessageBox.information(self, "Éxito", "Transmisión finalizada")
                self.actualizar_listas()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al finalizar transmisión: {str(e)}")

    def seleccionar_transmision(self, item):
        nombre_canal = item.text().split(" - ")[0]
        try:
            canal = self.mysql_ops.obtener_canal_por_nombre(nombre_canal)
            if canal:
                self.canal_seleccionado = canal['id_canal']
                # Mostrar componentes del chat
                self.chat_label.setText(f"Chat de {nombre_canal}")
                self.chat_list.show()
                self.mensaje_input.show()
                self.btn_enviar.show()
                self.actualizar_chat()
                # Iniciar el timer
                self.chat_timer.start()
        except Exception as e:
            print(f"Error al seleccionar transmisión: {e}")

    def seleccionar_canal(self, item):
        nombre_canal = item.text().split(" (")[0]

            # Detener el timer del chat
        self.chat_timer.stop()
        # Ocultar componentes del chat
        self.chat_list.hide()
        self.mensaje_input.hide()
        self.btn_enviar.hide()
        self.chat_label.setText("Seleccione una transmisión para ver el chat")

        try:
            canal = self.mysql_ops.obtener_canal_por_nombre(nombre_canal)
            if canal:
                self.canal_seleccionado = canal['id_canal']
                if self.usuario_actual and canal['id_usuario'] != self.usuario_actual['id_usuario']:
                    self.btn_seguir.show()
                    if self.mysql_ops.esta_siguiendo(self.usuario_actual['id_usuario'], canal['id_canal']):
                        self.btn_seguir.setText("Dejar de Seguir")
                    else:
                        self.btn_seguir.setText("Seguir")
        except Exception as e:
            print(f"Error al seleccionar canal: {e}")

    def seguir_canal(self):
        if not self.usuario_actual:
            QMessageBox.warning(self, "Error", "Debe iniciar sesión para seguir canales")
            return
        
        if not self.canal_seleccionado:
            QMessageBox.warning(self, "Error", "Seleccione un canal para seguir")
            return
            
        try:
            if self.btn_seguir.text() == "Seguir":
                self.mysql_ops.seguir_canal(
                    self.usuario_actual['id_usuario'],
                    self.canal_seleccionado
                )
                QMessageBox.information(self, "Éxito", "Ahora sigues este canal")
                self.btn_seguir.setText("Dejar de Seguir")
            else:
                self.mysql_ops.dejar_seguir_canal(
                    self.usuario_actual['id_usuario'],
                    self.canal_seleccionado
                )
                QMessageBox.information(self, "Éxito", "Has dejado de seguir este canal")
                self.btn_seguir.setText("Seguir")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al actualizar seguimiento: {str(e)}")

    def enviar_mensaje(self):
        if not self.usuario_actual:
            QMessageBox.warning(self, "Error", "Debe iniciar sesión para chatear")
            return
            
        if not self.canal_seleccionado:
            QMessageBox.warning(self, "Error", "Seleccione una transmisión para chatear")
            return
            
        mensaje = self.mensaje_input.text()
        if mensaje:
            try:
                self.mongo_ops.crear_mensaje(
                    self.canal_seleccionado,
                    self.usuario_actual['id_usuario'],
                    mensaje,
                    self.usuario_actual['nombre_usuario']
                )
                self.mensaje_input.clear()
                self.actualizar_chat()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al enviar mensaje: {str(e)}")

    def actualizar_chat(self):
        if self.canal_seleccionado:
            self.chat_list.clear()
            mensajes = self.mongo_ops.listar_mensajes(self.canal_seleccionado)
            for msg in mensajes:
                nombre = msg.get('nombre_usuario', 'Usuario Desconocido')
                contenido = msg.get('contenido', '')
                timestamp = msg.get('timestamp')
    
                # Formatear la hora si el timestamp está presente
                if timestamp:
                    if isinstance(timestamp, datetime):  # Si es un objeto datetime
                        hora = timestamp.strftime('%H:%M:%S')
                    else:  # Si viene como string o en otro formato
                        try:
                            hora = datetime.fromisoformat(str(timestamp)).strftime('%H:%M:%S')
                        except Exception:
                            hora = "Hora desconocida"
                else:
                    hora = "Hora desconocida"
    
                # Añadir el mensaje con la hora al chat
                self.chat_list.addItem(f"[{hora}] {nombre}: {contenido}")


    def mostrar_inicio(self):
        self.main_panel.setCurrentIndex(0)
        self.actualizar_listas()

    def mostrar_seguidos(self):
        if not self.usuario_actual:
            QMessageBox.warning(self, "Error", "Debe iniciar sesión para ver seguidos")
            return
        try:
            canales_seguidos = self.mysql_ops.obtener_canales_seguidos(self.usuario_actual['id_usuario'])
            self.lista_canales.clear()
            if not canales_seguidos:
                self.lista_canales.addItem("No sigues ningún canal")
                return
            for canal in canales_seguidos:
                # Verificar que los campos necesarios existen
                nombre_canal = canal.get('nombre_canal', 'Canal sin nombre')
                nombre_usuario = canal.get('nombre_usuario', 'Usuario desconocido')
                self.lista_canales.addItem(f"{nombre_canal} ({nombre_usuario})")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar canales seguidos: {str(e)}")
            print(f"Error en mostrar_seguidos: {e}")  # Para debugging

    def actualizar_listas(self):
        self.actualizar_lista_transmisiones()
        self.actualizar_lista_canales()

    def actualizar_lista_transmisiones(self):
        self.lista_transmisiones.clear()
        try:
            transmisiones = self.mysql_ops.obtener_transmisiones_activas()
            if transmisiones:
                for trans in transmisiones:
                    if isinstance(trans, dict) and 'nombre_canal' in trans and 'titulo' in trans:
                        self.lista_transmisiones.addItem(
                            f"{trans['nombre_canal']} - {trans['titulo']}"
                        )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar transmisiones: {str(e)}")
    
    def actualizar_lista_canales(self):
            self.lista_canales.clear()
            try:
                canales = self.mysql_ops.listar_canales()
                for canal in canales:
                    self.lista_canales.addItem(
                        f"{canal['nombre_canal']} ({canal['nombre_usuario']})"
                    )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error al cargar canales: {str(e)}")
    
    def mostrar_categorias(self):
       try:
           categorias = self.mysql_ops.listar_categorias()
           self.lista_transmisiones.clear()
           self.lista_canales.clear()
           
           if not categorias:
               # Insertar algunas categorías por defecto si no existen
               categorias_default = [
                   "Videojuegos", "Just Chatting", "IRL", "Música", 
                   "Deportes", "Eventos", "Arte", "Educación"
               ]
               for cat in categorias_default:
                   self.mysql_ops.crear_categoria(cat)
               categorias = self.mysql_ops.listar_categorias()
           
           # Mostrar transmisiones por categoría
           for categoria in categorias:
               if isinstance(categoria, dict) and 'nombre' in categoria and 'id_categoria' in categoria:
                   self.lista_transmisiones.addItem(f"=== {categoria['nombre']} ===")
                   transmisiones = self.mysql_ops.obtener_transmisiones_por_categoria(
                       categoria['id_categoria']
                   )
                   if transmisiones:
                       for trans in transmisiones:
                           if isinstance(trans, dict) and 'nombre_canal' in trans and 'titulo' in trans:
                               self.lista_transmisiones.addItem(
                                   f"  {trans['nombre_canal']} - {trans['titulo']}"
                               )
                   else:
                       self.lista_transmisiones.addItem("  No hay transmisiones activas en esta categoría")
           
           # Si no hay categorías o transmisiones en ninguna categoría
           if self.lista_transmisiones.count() == len(categorias):
               self.lista_transmisiones.addItem("No hay transmisiones activas en ninguna categoría")
                   
       except Exception as e:
           QMessageBox.warning(self, "Error", f"Error al cargar categorías: {str(e)}")
    
    def closeEvent(self, event):
        try:
            if self.transmision_actual and self.usuario_actual:
                respuesta = QMessageBox.question(
                    self,
                    "Finalizar Transmisión",
                    "¿Desea finalizar la transmisión actual antes de salir?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if respuesta == QMessageBox.Yes:
                    self.finalizar_transmision()
                
            if hasattr(self, 'mysql_conn'):
                self.mysql_conn.close()
            if hasattr(self, 'mongo_db'):
                self.mongo_db.client.close()
            event.accept()
        except Exception as e:
            print(f"Error al cerrar aplicación: {str(e)}")
            event.accept()

    def mostrar_perfil(self):
        if self.usuario_actual:
            # Actualizar datos del usuario para tener la info más reciente
            self.usuario_actual = self.mysql_ops.obtener_usuario_por_id(self.usuario_actual['id_usuario'])
            dialog = PerfilDialog(self.mysql_ops, self.usuario_actual, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Actualizar el usuario_actual con los nuevos datos
                self.usuario_actual = self.mysql_ops.obtener_usuario_por_id(self.usuario_actual['id_usuario'])



def main():
    app = QApplication(sys.argv)
    window = KickApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
