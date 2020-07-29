from google.appengine.ext import ndb


class ElectricVehicle(ndb.Model):
    name = ndb.StringProperty()
    name_lower = ndb.ComputedProperty(lambda self: self.name.lower())
    manufacturer = ndb.StringProperty()
    manufacturer_lower = ndb.ComputedProperty(lambda self: self.manufacturer.lower())
    year = ndb.IntegerProperty()
    batterySize = ndb.IntegerProperty()
    rangeWltp = ndb.IntegerProperty()
    cost = ndb.IntegerProperty()
    power = ndb.IntegerProperty()
