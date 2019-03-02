
from PyQt5.QtWidgets import *

class BiggerIconsStyle(QProxyStyle):
    pass
    def pixelMetric(self, QStyle_PixelMetric, option=None, widget=None):

        if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
            return 22
        else:
            return QProxyStyle.pixelMetric(self, QStyle_PixelMetric, option, widget)