from PySide6.QtCore import (
    QCoreApplication,
    QMetaObject,
    QSize,
    Qt,
)
from PySide6.QtWidgets import (
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QSizePolicy,
    QSpinBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow: QMainWindow) -> None:
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(518, 500)
        MainWindow.setMinimumSize(QSize(394, 500))
        self.mainWidget = QWidget(MainWindow)
        self.mainWidget.setObjectName("mainWidget")
        self.verticalLayout = QVBoxLayout(self.mainWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 12, -1, 12)
        self.settingsCluster = QWidget(self.mainWidget)
        self.settingsCluster.setObjectName("settingsCluster")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.settingsCluster.sizePolicy().hasHeightForWidth()
        )
        self.settingsCluster.setSizePolicy(sizePolicy)
        self.settingsCluster.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.horizontalLayout = QHBoxLayout(self.settingsCluster)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.crsCluster = QWidget(self.settingsCluster)
        self.crsCluster.setObjectName("crsCluster")
        sizePolicy1 = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum
        )
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.crsCluster.sizePolicy().hasHeightForWidth())
        self.crsCluster.setSizePolicy(sizePolicy1)
        self.horizontalLayout_4 = QHBoxLayout(self.crsCluster)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.crsClusterLabel = QLabel(self.crsCluster)
        self.crsClusterLabel.setObjectName("crsClusterLabel")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.crsClusterLabel.sizePolicy().hasHeightForWidth()
        )
        self.crsClusterLabel.setSizePolicy(sizePolicy2)

        self.horizontalLayout_4.addWidget(self.crsClusterLabel)

        self.crsClusterLineEdit = QLineEdit(self.crsCluster)
        self.crsClusterLineEdit.setObjectName("crsClusterLineEdit")
        sizePolicy3 = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(
            self.crsClusterLineEdit.sizePolicy().hasHeightForWidth()
        )
        self.crsClusterLineEdit.setSizePolicy(sizePolicy3)
        self.crsClusterLineEdit.setMinimumSize(QSize(150, 0))
        self.crsClusterLineEdit.setMaximumSize(QSize(16777215, 16777215))
        self.crsClusterLineEdit.setMaxLength(32767)

        self.horizontalLayout_4.addWidget(self.crsClusterLineEdit)

        self.horizontalLayout.addWidget(self.crsCluster)

        self.displayCluster = QWidget(self.settingsCluster)
        self.displayCluster.setObjectName("displayCluster")
        sizePolicy4 = QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(
            self.displayCluster.sizePolicy().hasHeightForWidth()
        )
        self.displayCluster.setSizePolicy(sizePolicy4)
        self.horizontalLayout_2 = QHBoxLayout(self.displayCluster)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.displayClusterLabel = QLabel(self.displayCluster)
        self.displayClusterLabel.setObjectName("displayClusterLabel")
        sizePolicy2.setHeightForWidth(
            self.displayClusterLabel.sizePolicy().hasHeightForWidth()
        )
        self.displayClusterLabel.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.displayClusterLabel)

        self.displayClusterSpinner = QSpinBox(self.displayCluster)
        self.displayClusterSpinner.setObjectName("displayClusterSpinner")
        sizePolicy2.setHeightForWidth(
            self.displayClusterSpinner.sizePolicy().hasHeightForWidth()
        )
        self.displayClusterSpinner.setSizePolicy(sizePolicy2)
        self.displayClusterSpinner.setMinimum(0)
        self.displayClusterSpinner.setValue(5)

        self.horizontalLayout_2.addWidget(self.displayClusterSpinner)

        self.horizontalLayout.addWidget(self.displayCluster)

        self.verticalLayout.addWidget(self.settingsCluster)

        self.graphicsView = QGraphicsView(self.mainWidget)
        self.graphicsView.setObjectName("graphicsView")

        self.verticalLayout.addWidget(self.graphicsView)

        MainWindow.setCentralWidget(self.mainWidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow: QMainWindow) -> None:
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.crsClusterLabel.setText(
            QCoreApplication.translate("MainWindow", "Station", None)
        )
        self.crsClusterLineEdit.setInputMask("")
        self.crsClusterLineEdit.setText("")
        self.displayClusterLabel.setText(
            QCoreApplication.translate("MainWindow", "Displays", None)
        )
