# Copyright (c) Alexander Borgerth 2010
# See LICENSE for details.

class PirateException(Exception):
    pass

class TableError(PirateException):
    pass

class InvalidTable(TableError):
    pass

class InvalidRow(TableError):
    pass

class ElementNotFound(PirateException):
    pass