from electricVehicle import ElectricVehicle
from google.appengine.ext import ndb


class Review(ndb.Model):
    electric_vehicle = ndb.KeyProperty(ElectricVehicle)
    content = ndb.StringProperty(indexed=False)
    score = ndb.IntegerProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)
