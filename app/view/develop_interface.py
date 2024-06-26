# coding:utf-8
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import Action
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (RoundMenu)

from app.common.config import cfg
from .Ui_DevelopInterface import Ui_DevelopInterface
from .components.crypto import QuizCrypto
from .components.customBoxBase import UserNameBox, NotifyBox
from .test_interface import TestInterface


class DevelopInterface(Ui_DevelopInterface, QWidget):

    def __init__(self, parent=None,):
        self.parent = parent
        super().__init__(parent=parent)
        self.setObjectName('developInterface')
        self.setupUi(self)
        self.nameWindow = UserNameBox(self.window())
        self.name = None
        self._initInterface()
        self.createdFileInterfaces = []

    def _initInterface(self):

        self.ChooseFileIcon.setIcon(FIF.SHARE)
        self.ChooseFileButton.clicked.connect(self.ChooseFileButtonAction)

        self.ChooseFileButton.setIcon(FIF.FOLDER)
        self.ChooseFileDrop.setIcon(FIF.SEND)


        self.LastSeenFill()


    def LastSeenFill(self):
        self.lastSeen = cfg.get(cfg.lastViewTest)

        menu = RoundMenu(parent=self)
        menu.setMaxVisibleItems(4)
        for filePath in self.lastSeen:
            action = Action(FIF.DOCUMENT, filePath)
            action.triggered.connect(self.showCustomDialog)
            action.triggered.connect(lambda _=None, button=action: self.createNewTestInterface(_, button))
            menu.addAction(action)

        self.ChooseFileDrop.setMenu(menu)

    def showCustomDialog(self):
        if not self.name:
            w = UserNameBox(self.window())
            if w.exec():
                self.name = w.userNameEdit.text()
                newCompleterNames = cfg.get(cfg.userHistory)
                if isinstance(newCompleterNames, list):
                    if self.name in newCompleterNames:
                        newCompleterNames.remove(self.name)
                newCompleterNames.insert(0, self.name)
                cfg.set(cfg.userHistory, newCompleterNames)
                cfg.save()
    def createNewTestInterface(self, _, button):
        if self.name:
            if isinstance(button, str):
                filePath = button
            else:
                filePath = button.text()

            for i in self.createdFileInterfaces:
                if i['name'] == filePath:
                    self.refill(filePath)
                    self.parent.switchTo(i['interface'])
                    return
            crypto = QuizCrypto()
            try:
                self.data = crypto.decryptFromFile(filePath)
                newTestInterface = TestInterface(self, filePath=filePath, userName=self.name, data=self.data)
                newTestInterface.setObjectName(filePath)
                self.addInterfaceToSuperview(newTestInterface, filePath)
                self.parent.switchTo(newTestInterface)
                self.createdFileInterfaces.append({
                    'name': filePath,
                    'interface': newTestInterface
                })
                self.refill(filePath)
            except Exception as e:
                NotifyBox(self.parent, title='Ошибка', message=f'Возникла ошибка при чтении файла. Вероятнее всего файл теста повреждён.').exec()


    def addInterfaceToSuperview(self, newInterface, filePath):
        self.parent.stackedWidget.addWidget(newInterface)
        self.parent.addSubInterface(icon=FIF.DOCUMENT, text=filePath, interface=newInterface)

    def ChooseFileButtonAction(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseCustomDirectoryIcons
        filePath, _ = QFileDialog.getOpenFileName(self, "Testify", "",
                                                  "Тест Testify (*.tstf)", options=options)
        if filePath:
            self.loadQuiz(filePath)

    def loadQuiz(self, filePath):
        self.refill(filePath)
        self.showCustomDialog()
        self.createNewTestInterface(None, filePath)

    def refill(self, filePath):
        lastSeen = cfg.get(cfg.lastViewTest)
        if isinstance(lastSeen, list):
            if filePath in lastSeen:
                lastSeen.remove(filePath)
            lastSeen.insert(0, filePath)  # Вставляем filePath в начало списка
            cfg.set(cfg.lastViewTest, lastSeen)
            cfg.save()
            self.LastSeenFill()