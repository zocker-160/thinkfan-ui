# MODIFIED
from PyQt6.QtCore import QTextStream, pyqtSignal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtNetwork import (
    QHostAddress,
    QLocalSocket,
    QLocalServer,
    QTcpSocket,
    QTcpServer
)

ACTIVATE_SIGNAL = "activate"

class QSingleApplication(QApplication):

    onActivate = pyqtSignal()

    def __init__(self, id: str, *argv):
        super().__init__(*argv)

        self.aboutToQuit.connect(self.stopSockets)

        self.id = id
        self.server: QLocalServer = None
        self.dataStream: QTextStream = None

        self.localSocket = QLocalSocket(self)
        self.localSocket.connectToServer(self.id)

        self.isRunning = self.localSocket.waitForConnected()

        if self.isRunning:
            self.dataStream = QTextStream(self.localSocket)
            self.dataStream << ACTIVATE_SIGNAL
            self.dataStream.flush()
            self.localSocket.waitForBytesWritten()
        else:
            self.server = QLocalServer(self)
            self.server.listen(self.id)
            self.server.newConnection.connect(self.onNewConnection)

    def onNewConnection(self):
        inSocket = self.server.nextPendingConnection()
        if not inSocket: return

        inStream = QTextStream(inSocket)
        inSocket.readyRead.connect(lambda: self.onReadyRead(inStream))

    def onReadyRead(self, inStream: QTextStream):
        msg = inStream.readAll()

        if msg == ACTIVATE_SIGNAL:
            self.onActivate.emit()

    def stopSockets(self):
        self.localSocket.close()
        if self.server:
            self.server.close()

TCP_ADDR = "127.0.0.1"
TCP_PORT = 17999

class QSingleApplicationTCP(QApplication):

    onActivate = pyqtSignal()

    def __init__(self, id: str, *argv):
        super().__init__(*argv)

        self.aboutToQuit.connect(self.stopSockets)

        self.id = id
        self.tcpServer: QTcpServer = None

        self.tcpSocket = QTcpSocket(self)
        self.tcpSocket.connectToHost(TCP_ADDR, TCP_PORT)

        self.isRunning = self.tcpSocket.waitForConnected()
        if self.isRunning:
            data = QTextStream(self.tcpSocket)
            data << ACTIVATE_SIGNAL
            data.flush()
            self.tcpSocket.waitForBytesWritten()
        else:
            self.tcpServer = QTcpServer(self)
            self.tcpServer.listen(QHostAddress(TCP_ADDR), TCP_PORT)
            self.tcpServer.newConnection.connect(self.onNewConnection)

    def onNewConnection(self):
        inConn = self.tcpServer.nextPendingConnection()
        if not inConn: return

        inData = QTextStream(inConn)
        inConn.readyRead.connect(lambda: self.onReadyRead(inData))

    def onReadyRead(self, inStream: QTextStream):
        msg = inStream.readAll()

        if msg == ACTIVATE_SIGNAL:
            self.onActivate.emit()

    def stopSockets(self):
        self.tcpSocket.close()
        if self.tcpServer:
            self.tcpServer.close()
