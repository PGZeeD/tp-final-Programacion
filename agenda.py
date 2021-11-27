from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QInputDialog
from PyQt5 import uic
import sqlite3


class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("agenda.ui", self)
        self.lista.itemClicked.connect(self.selector)
        self.btn_editar.clicked.connect(self.editar)
        self.btn_cancelar.clicked.connect(self.cancelar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_nuevo.clicked.connect(self.agregar)
        self.btn_guardar.clicked.connect(self.guardar)
        self.estatura.textEdited.connect(self.desblockear)
        self.peso.textEdited.connect(self.desblockear)

        self.flag = ''
        self.status = "cargado"
        self.BD = []

        self.conexion = sqlite3.connect("usuarios")
        self.cursor = self.conexion.cursor()
        self.loadDataBase()

        self.msg = QMessageBox()
        self.msg.setWindowTitle('Eliminar')
        self.msg.setIcon(QMessageBox.Information)
        self.stp = 0

    def loadDataBase(self):

        self.cursor.execute('select * from usuarios')
        usuarios = self.cursor.fetchall()

        for usuario in usuarios:
            formatoDeLaListaQt = f'{usuario[0]} {usuario[1]} {usuario[2]}'
            formatoDeLaLista = [usuario[0], usuario[1], usuario[2], usuario[3],
                                usuario[4], usuario[5], usuario[6], usuario[7], usuario[8], self.status]
            self.lista.addItem(formatoDeLaListaQt)
            self.BD.append(formatoDeLaLista)

    def desblockear(self):
        if self.peso.text().isdigit() and len(self.peso.text()) >= 2:
            self.btn_aceptar.setEnabled(True)
        elif self.estatura.text().isdigit() and len(self.peso.text()) >= 2:
            pass
        else:
            if self.estatura.text().isalpha():
                self.getint()
                self.estatura.setText(self.var)
            elif self.peso.text().isalpha():
                self.getint()
                self.peso.setText(self.var)
                self.btn_aceptar.setEnabled(True)
                self.peso.textEdited.connect(self.desblockear)
            else:
                pass

    def getint(self):
        num, ok = QInputDialog.getInt(
            self, "Atencion", "Debe Ingresar un 'Numero Entero'")
        if ok:
            self.var = (str(num))
        else:
            exit
        return self.var

    def where(self, check):
        for i in range(len(self.BD)):
            if self.BD[i][0] == check:
                posicion = i
                break
        return posicion

    def cancelar(self):
        self.selector()

    def on_aceptar(self):

        labels = self.nombre, self.apellido, self.email, self.telefono, self.direccion, self.fechanac, self.estatura, self.peso

        if self.flag == "editar":
            cursor = self.lista.currentItem().text().split()
            index_ = int(cursor[0])
            posicion = self.where(index_)

            for num, label in enumerate(labels):
                self.BD[posicion][num+1] = label.text()

            formatoDeLaListaQt = f'{cursor[0]} {labels[0].text()} {labels[1].text()}'
            self.lista.currentItem().setText(formatoDeLaListaQt)

            self.BD[posicion][9] = 'edit'
            self.selector()
        elif self.flag == "agregar":
            status = 'add'
            indexUltimate = self.BD[-1][0] + 1
            formatoDeLaLista = [indexUltimate, labels[0].text(), labels[1].text(), labels[2].text(), labels[3].text(
            ), labels[4].text(), labels[5].text(), labels[6].text(), labels[7].text(), labels[7].text()]
            formatoDeLaListaQt = f'{indexUltimate} {labels[0].text()} {labels[1].text()}'
            self.BD.append(formatoDeLaLista)
            self.lista.addItem(formatoDeLaListaQt)
            self.lista.setCurrentRow(self.lista.count() - 1)
            self.BD[-1][9] = 'add'
            self.btn_guardar.setEnabled(True)
            self.selector()

        self.flag = ""

    def selector(self):

        cursor = self.lista.currentItem().text().split()
        index_ = int(cursor[0])
        posicion = self.where(index_)

        labels = self.nombre, self.apellido, self.email, self.telefono, self.direccion, self.fechanac, self.estatura, self.peso

        for num, label in enumerate(labels):
            label.setText(str(self.BD[posicion][num+1]))
            label.setEnabled(False)
        self.btn_editar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)

    def guardar(self):
        for i in self.BD:
            if i[9] == 'delete':
                self.cursor.execute(
                    F'DELETE FROM usuarios WHERE id = ("{i[0]}")')
                self.conexion.commit()
            elif i[9] == 'add':
                self.cursor.execute(
                    f"insert into usuarios (nombre, apellido, mail, telefono, direccion, nacimiento, estatura, peso) values ('{i[1]}','{i[2]}','{i[3]}','{i[4]}','{i[5]}','{i[6]}','{i[7]}','{i[8]}')")
                self.conexion.commit()
            elif i[9] == 'edit':
                self.cursor.execute(f"""UPDATE usuarios set nombre = 
                    ('{i[1]}'), apellido = ('{i[2]}'), mail = ('{i[3]}'), 
                    telefono = ('{i[4]}'), direccion = ('{i[5]}'),
                    nacimiento = ('{i[5]}'), estatura  = ('{i[6]}'),
                    peso = ('{i[7]}')
                    WHERE id = ('{i[0]}')""")
                self.conexion.commit()

    def editar(self):

        self.flag = 'editar'
        labels = self.nombre, self.apellido, self.email, self.telefono, self.direccion, self.fechanac, self.estatura, self.peso
        cursor = self.lista.currentItem().text().split()

        for label in labels:
            label.setEnabled(True)

        self.nombre.setFocus(True)

        self.btn_aceptar.clicked.connect(self.on_aceptar)

    def eliminar(self):
        cursor = self.lista.currentItem().text().split()
        index_ = int(cursor[0])
        posicion = self.where(index_)

        self.msg.setText(
            f'¿Desea borrar el usuario {cursor[0]} {cursor[1]} {cursor[2]}?')
        self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        mensaje = self.msg.exec()
        if mensaje == QMessageBox.Yes:
            self.BD[posicion][9] = 'delete'
            self.lista.takeItem(self.lista.currentRow())
            self.btn_guardar.setEnabled(True)

    def agregar(self):
        self.flag = 'agregar'
        labels = self.nombre, self.apellido, self.email, self.telefono, self.direccion, self.fechanac, self.estatura, self.peso
        cursor = self.lista.currentItem().text().split()

        for num, label in enumerate(labels):
            label.setText("")
            label.setEnabled(True)

        self.nombre.setFocus(True)
        self.btn_cancelar.setEnabled(True)
        self.btn_aceptar.clicked.connect(self.on_aceptar)


app = QApplication([])

win = MiVentana()
win.show()

app.exec_()
