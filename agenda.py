from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5 import uic
import sqlite3


class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("agenda.ui", self)
        # Conexiones de botones.
        self.lista.itemClicked.connect(self.on_click)
        self.editar.clicked.connect(self.on_edit)
        self.cancelar.clicked.connect(self.on_cancelar)
        self.eliminar.clicked.connect(self.on_eliminar)
        self.nuevo.clicked.connect(self.on_agregar)
        self.guardar.clicked.connect(self.on_guardar)
        self.peso.textEdited.connect(self.actived)
        # Listas de Base de Datos
        self.flag = ''
        self.status = "cargado"
        self.baseDatos = []
        # Conexion a Base de Datos
        self.conexion = sqlite3.connect("usuarios")
        self.cursor = self.conexion.cursor()
        self.on_cargarBD()

        self.msg = QMessageBox()
        self.msg.setWindowTitle('Laboratorio')
        self.msg.setIcon(QMessageBox.Information)

    def actived(self):
        if len(self.peso.text()) > 2:
            self.aceptar.setEnabled(True)

    def where(self, check):
        for i in range(len(self.baseDatos)):
            if self.baseDatos[i][0] == check:
                posicion = i
                break
        return posicion

    def on_aceptar(self):
        # automatiza activbacion lineedit
        labels = self.nombre, self.apellido, self.email, self.telefono, self.direccion, self.fechanac, self.estatura, self.peso

        if self.flag == "editar":
            click = self.lista.currentItem().text().split()
            index_ = int(click[0])
            posicion = self.where(index_)
            # Recorremos labels/editando listas
            for num, label in enumerate(labels):
                self.baseDatos[posicion][num+1] = label.text()

            formatoDeLaListaQt = f'{click[0]} {labels[0].text()} {labels[1].text()}'
            self.lista.currentItem().setText(formatoDeLaListaQt)

            self.baseDatos[posicion][9] = 'edit'
            self.on_click()
        elif self.flag == "agregar":
            status = 'add'
            indexUltimate = self.baseDatos[-1][0] + 1
            formatoDeLaLista = [indexUltimate, labels[0].text(), labels[1].text(), labels[2].text(), labels[3].text(
            ), labels[4].text(), labels[5].text(), labels[6].text(), labels[7].text(), labels[7].text()]
            formatoDeLaListaQt = f'{indexUltimate} {labels[0].text()} {labels[1].text()}'
            self.baseDatos.append(formatoDeLaLista)
            self.lista.addItem(formatoDeLaListaQt)
            self.lista.setCurrentRow(self.lista.count() - 1)
            self.baseDatos[-1][9] = 'add'
            self.guardar.setEnabled(True)
            self.on_click()

        self.flag = ""

    def on_cancelar(self):
        self.on_click()

    def on_cargarBD(self):
        # Selecciona usuarios dentro de la base de datos
        self.cursor.execute('select * from usuarios')
        usuarios = self.cursor.fetchall()

        # Cargamos las listas
        for usuario in usuarios:
            formatoDeLaListaQt = f'{usuario[0]} {usuario[1]} {usuario[2]}'
            formatoDeLaLista = [usuario[0], usuario[1], usuario[2], usuario[3],
                                usuario[4], usuario[5], usuario[6], usuario[7], usuario[8], self.status]
            self.lista.addItem(formatoDeLaListaQt)
            self.baseDatos.append(formatoDeLaLista)

    def on_click(self):
        # Obtenemos el index que cargamos de la base de datos
        # Le restamos para volverlo compatible con los index de la lista
        click = self.lista.currentItem().text().split()
        index_ = int(click[0])
        posicion = self.where(index_)

        labels = self.nombre, self.apellido, self.email, self.telefono, self.direccion, self.fechanac, self.estatura, self.peso

        # Recorre labels para rellenarlos con datos de lista BaseDatos
        for num, label in enumerate(labels):
            label.setText(str(self.baseDatos[posicion][num+1]))
            label.setEnabled(False)
        self.editar.setEnabled(True)
        self.eliminar.setEnabled(True)

    def on_edit(self):
        # Automatizar activacion de Lineedit
        self.flag = 'editar'
        labels = self.nombre, self.apellido, self.email, self.telefono, self.direccion, self.fechanac, self.estatura, self.peso
        click = self.lista.currentItem().text().split()

        for label in labels:
            label.setEnabled(True)

        self.nombre.setFocus(True)

        self.aceptar.clicked.connect(self.on_aceptar)

    def on_eliminar(self):
        click = self.lista.currentItem().text().split()
        index_ = int(click[0])
        posicion = self.where(index_)

        self.msg.setText(
            f'¿Eliminar el usuario {click[0]} {click[1]} {click[2]}')
        self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        mensaje = self.msg.exec()
        if mensaje == QMessageBox.Yes:
            self.baseDatos[posicion][9] = 'delete'
            self.lista.takeItem(self.lista.currentRow())
            self.guardar.setEnabled(True)

    def on_agregar(self):
        self.flag = 'agregar'
        labels = self.nombre, self.apellido, self.email, self.telefono, self.direccion, self.fechanac, self.estatura, self.peso
        click = self.lista.currentItem().text().split()

        for num, label in enumerate(labels):
            label.setText("")
            label.setEnabled(True)

        self.nombre.setFocus(True)
        self.cancelar.setEnabled(True)
        self.aceptar.clicked.connect(self.on_aceptar)

    def on_guardar(self):
        for i in self.baseDatos:
            if i[9] == 'delete':
                self.cursor.execute(
                    F'DELETE FROM usuarios WHERE id = ("{i[0]}")')
                self.conexion.commit()
            elif i[9] == 'add':
                self.cursor.execute(
                    f"insert into usuarios (nombre, apellido, mail, telefono, direccion, nacimiento, altura, peso) values ('{i[1]}','{i[2]}','{i[3]}','{i[4]}','{i[5]}','{i[6]}','{i[7]}','{i[8]}')")
                self.conexion.commit()
            elif i[9] == 'edit':
                self.cursor.execute(f"""UPDATE usuarios set nombre = 
                    ('{i[1]}'), apellido = ('{i[2]}'), mail = ('{i[3]}'), 
                    telefono = ('{i[4]}'), direccion = ('{i[5]}'),
                    nacimiento = ('{i[5]}'), altura  = ('{i[6]}'),
                    peso = ('{i[7]}')
                    WHERE id = ('{i[0]}')""")
                self.conexion.commit()


app = QApplication([])

win = MiVentana()
win.show()

app.exec_()
