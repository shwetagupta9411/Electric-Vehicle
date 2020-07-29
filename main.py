from operator import itemgetter
import webapp2
import jinja2
from google.appengine.api import users
from electricVehicle import ElectricVehicle
from review import Review
import os
from google.appengine.ext import ndb
import logging
from webapp2_extras import sessions
from webapp2_extras import sessions_memcache
import time

JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(
    os.path.dirname(__file__)),extensions=["jinja2.ext.autoescape"], autoescape=True)

from webapp2_extras import sessions


class BasicReqHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def session(self):
        """Returns a session using the default cookie key"""
        # return self.session_store.get_session()
        return self.session_store.get_session(
            name='mc_session',
            factory=sessions_memcache.MemcacheSessionFactory)

    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    def add_message(self, message, level=None):
        self.session.add_flash(message, level, key='_messages')

    @webapp2.cached_property
    def messages(self):
        return self.session.get_flashes(key='_messages')

#Class to display the list of EV and apply the filters
class ElectricVehicleList(BasicReqHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/html"
        url = ""
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_string = "logout"
        else:
            url = users.create_login_url(self.request.uri)
            url_string = "login"
        name_param = self.request.get('name', None)
        manufacturer_param = self.request.get('manufacturer', None)
        from_year_param = self.request.get('from_year', None)
        to_year_param = self.request.get('to_year', None)
        cost_from_param = self.request.get('cost_from', None)
        cost_to_param = self.request.get('cost_to', None)
        battery_size_from_param = self.request.get('battery_size_from', None)
        battery_size_to_param = self.request.get('battery_size_to', None)
        wltp_from_param = self.request.get('wltp_from', None)
        wltp_to_param = self.request.get('wltp_to', None)
        power_from_param = self.request.get('power_from', None)
        power_to_param = self.request.get('power_to', None)
        filters = {
            "name" : name_param,
            "manufacturer": manufacturer_param,
            "from_year" : from_year_param,
            "to_year" : to_year_param,
            "cost_from": cost_from_param,
            "cost_to": cost_to_param,
            "battery_size_from": battery_size_from_param,
            "battery_size_to" : battery_size_to_param,
            "wltp_from": wltp_from_param,
            "wltp_to": wltp_to_param,
            "power_from": power_from_param,
            "power_to": power_to_param
        }
        if(name_param or manufacturer_param or from_year_param or to_year_param or cost_from_param or cost_to_param or
        battery_size_from_param or battery_size_to_param or wltp_from_param or wltp_to_param or power_from_param or power_to_param):
            filtered_query_stage1 = ElectricVehicle.query()
            if name_param:
                filtered_query_stage1 = filtered_query_stage1.filter(
                    ElectricVehicle.name_lower == str(name_param.lower()))
            if manufacturer_param:
                filtered_query_stage1 = filtered_query_stage1.filter(
                    ElectricVehicle.manufacturer_lower == str(manufacturer_param.lower()))
            # Filter year starts
            if from_year_param and (to_year_param is None or not to_year_param):
                filtered_query_year = ElectricVehicle.query()
                filtered_query_year = filtered_query_year.filter(
                    ElectricVehicle.year >= int(from_year_param))
                yearQuery = filtered_query_year.fetch()
            if to_year_param and (from_year_param is None or not from_year_param):
                filtered_query_year = ElectricVehicle.query()
                filtered_query_year = filtered_query_year.filter(
                    ElectricVehicle.year <= int(to_year_param))
                yearQuery = filtered_query_year.fetch()
            if to_year_param and from_year_param:
                filtered_query_year = ElectricVehicle.query(
                    ndb.AND(ElectricVehicle.year >= int(from_year_param),
                        ndb.AND(ElectricVehicle.year <= int(to_year_param))))
                yearQuery = filtered_query_year.fetch()
            first_filter_stage = filtered_query_stage1.fetch()
            # Filter cost starts
            if cost_from_param and (cost_to_param is None or not cost_to_param):
                filtered_query_cost = ElectricVehicle.query()
                filtered_query_cost = filtered_query_cost.filter(
                    ElectricVehicle.cost >= int(cost_from_param))
                costQuery = filtered_query_cost.fetch()
            if cost_to_param and (cost_from_param is None or not cost_from_param):
                filtered_query_cost = ElectricVehicle.query()
                filtered_query_cost = filtered_query_cost.filter(
                    ElectricVehicle.cost <= int(cost_to_param))
                costQuery = filtered_query_cost.fetch()
            if cost_to_param and cost_from_param:
                filtered_query_cost = ElectricVehicle.query(
                    ndb.AND(ElectricVehicle.cost >= int(cost_from_param),
                        ndb.AND(ElectricVehicle.cost <= int(cost_to_param))))
                costQuery = filtered_query_cost.fetch()
            # Filter battery Size
            if battery_size_from_param and (battery_size_to_param is None
                                            or not battery_size_to_param):
                filtered_query_battery = ElectricVehicle.query()
                filtered_query_battery = filtered_query_battery.filter(
                    ElectricVehicle.batterySize >= int(battery_size_from_param))
                batteryQuery = filtered_query_battery.fetch()
            if battery_size_to_param and (battery_size_from_param is None
                                          or not battery_size_from_param):
                filtered_query_battery = ElectricVehicle.query()
                filtered_query_battery = filtered_query_battery.filter(
                    ElectricVehicle.batterySize <= int(battery_size_to_param))
                batteryQuery = filtered_query_battery.fetch()
            if battery_size_to_param and battery_size_from_param:
                filtered_query_battery = ElectricVehicle.query(
                    ndb.AND(ElectricVehicle.batterySize >= int(battery_size_from_param),
                        ndb.AND(ElectricVehicle.batterySize <= int(battery_size_to_param))))
                batteryQuery = filtered_query_battery.fetch()
            # Filter wltp_to_param
            if wltp_from_param and (wltp_to_param is None or not wltp_to_param):
                filtered_query_wltp = ElectricVehicle.query()
                filtered_query_wltp = filtered_query_wltp.filter(
                    ElectricVehicle.rangeWltp >= int(wltp_from_param))
                wltpQuery = filtered_query_wltp.fetch()
            if wltp_to_param and (wltp_from_param is None or not wltp_from_param):
                filtered_query_wltp = ElectricVehicle.query()
                filtered_query_wltp = filtered_query_wltp.filter(
                    ElectricVehicle.rangeWltp <= int(wltp_to_param))
                wltpQuery = filtered_query_wltp.fetch()
            if wltp_to_param and wltp_from_param:
                filtered_query_wltp = ElectricVehicle.query(
                    ndb.AND(ElectricVehicle.rangeWltp >= int(wltp_from_param),
                        ndb.AND(ElectricVehicle.rangeWltp <= int(wltp_to_param))))
                wltpQuery = filtered_query_wltp.fetch()
            # Filter power_from_param
            if power_from_param and (power_to_param is None or not power_to_param):
                filtered_query_power = ElectricVehicle.query()
                filtered_query_power = filtered_query_power.filter(
                    ElectricVehicle.power >= int(power_from_param))
                powerQuery = filtered_query_power.fetch()
            if power_to_param and (power_from_param is None
                                   or not power_from_param):
                filtered_query_power = ElectricVehicle.query()
                filtered_query_power = filtered_query_power.filter(
                    ElectricVehicle.power <= int(power_to_param))
                powerQuery = filtered_query_power.fetch()
            if power_to_param and power_from_param:
                filtered_query_power = ElectricVehicle.query(
                    ndb.AND(ElectricVehicle.power >= int(power_from_param),
                        ndb.AND(ElectricVehicle.power <= int(power_to_param))))
                powerQuery = filtered_query_power.fetch()
            electric_vehicles = first_filter_stage
            temp_2 = []
            temp = []
            if(cost_from_param or cost_to_param):
                for ev_q1 in first_filter_stage:
                    for ev_q2 in costQuery:
                        if(ev_q1.key == ev_q2.key):
                            temp_2.append(ev_q1)
                electric_vehicles = temp_2
            if(battery_size_from_param or battery_size_to_param):
                for ev_q3 in batteryQuery:
                    for ev_q4 in electric_vehicles:
                        if(ev_q3.key == ev_q4.key):
                            temp.append(ev_q3)
                electric_vehicles = temp
            if(from_year_param or to_year_param):
                temp=[]
                for ev_q10 in yearQuery:
                    for ev_q14 in electric_vehicles:
                        if(ev_q10.key == ev_q14.key):
                            temp.append(ev_q10)
                electric_vehicles = temp
            if(wltp_from_param or wltp_to_param):
                temp_2 = []
                for ev_q5 in wltpQuery:
                    for ev_q6 in electric_vehicles:
                        if(ev_q5.key == ev_q6.key):
                            temp_2.append(ev_q5)
                electric_vehicles = temp_2
            if(power_from_param or power_to_param):
                temp = []
                for ev_q7 in powerQuery:
                    for ev_q8 in electric_vehicles:
                        if(ev_q7.key == ev_q8.key):
                            temp.append(ev_q7)
                electric_vehicles = temp
        else:
            filtered_query = ElectricVehicle.query()
            electric_vehicles = filtered_query.fetch()
        template_values = {
            "messages": self.messages,
            "electric_vehicles": electric_vehicles,
            "url": url,
            "url_string": url_string,
            "user": user,
            "filters": filters
        }
        template = JINJA_ENVIRONMENT.get_template(
            "electric_vehicles/list.html")
        self.response.write(template.render(template_values))

# class to delete the EV
class ElectricVehicleDelete(BasicReqHandler):
    def get(self, id=None):
        self.response.headers["Content-Type"] = "text/html"
        url = ""
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_string = "logout"
            if id:
                electric_vehicle = ElectricVehicle.get_by_id(int(id))
                electric_vehicle.key.delete()
                self.add_message('Electric Vehicle deleted successfully.',
                                 'success')
        else:
            url = users.create_login_url(self.request.uri)
            url_string = "login"
            self.add_message('Operation not allowed for guests.', 'danger')

        time.sleep(2)
        self.redirect('/electric_vehicles/', abort=False)
        return

#Class to compare the EVs
class ElectricVehicleCompare(BasicReqHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/html"
        url = ""
        user = users.get_current_user()
        ids = self.request.get('ids', None)
        if user:
            url = users.create_logout_url(self.request.uri)
            url_string = "logout"
        else:
            url = users.create_login_url(self.request.uri)
            url_string = "login"

        columns = [
            'Name', 'Manufacturer', 'Year', 'Battery Size', 'WLTP Range',
            'Cost', 'Power'
        ]
        names = []
        manufacturers = ['Manufacturer']
        years = []
        battery_sizes = []
        wltp_ranges = []
        costs = []
        powers = []
        reviews = []

        if ids:
            ids = ids.split(",")
            elec_key_ids = [ndb.Key(ElectricVehicle, int(id)) for id in ids]
            electric_vehicles = ndb.get_multi(elec_key_ids)
            for x in electric_vehicles:
                names.append({"name": x.name, "id": x.key.id()})
                manufacturers.append(x.manufacturer)
                years.append({"color": "", "value": x.year})
                battery_sizes.append({"color": "", "value": x.batterySize})
                wltp_ranges.append({"color": "", "value": x.rangeWltp})
                costs.append({"color": "", "value": x.cost})
                powers.append({"color": "", "value": x.power})

                reviews_res = Review.query(
                    Review.electric_vehicle == x.key).fetch()
                for_score = [rev.score for rev in reviews_res]
                avg_review = 0
                if len(for_score):
                    avg_review = sum(for_score) / len(for_score)
                reviews.append({"color": "", "value": avg_review})

            years_highest = max(years, key=lambda x: x['value'])
            years_lowest = min(years, key=lambda x: x['value'])
            for y in years:
                if y["value"] == years_lowest["value"]:
                    y["color"] = 'danger'
                if y["value"] == years_highest["value"]:
                    y["color"] = 'success'
            years.insert(0, {"color": "", "value": "Year"})
            battery_sizes_highest = max(battery_sizes,
                                        key=lambda x: x['value'])
            battery_sizes_lowest = min(battery_sizes, key=lambda x: x['value'])
            for y in battery_sizes:
                if y["value"] == battery_sizes_lowest["value"]:
                    y["color"] = 'danger'
                if y["value"] == battery_sizes_highest["value"]:
                    y["color"] = 'success'
            battery_sizes.insert(0, {"color": "", "value": "Battery Size"})

            wltp_ranges_highest = max(wltp_ranges, key=lambda x: x['value'])
            wltp_ranges_lowest = min(wltp_ranges, key=lambda x: x['value'])
            for y in wltp_ranges:
                if y["value"] == wltp_ranges_lowest["value"]:
                    y["color"] = 'danger'
                if y["value"] == wltp_ranges_highest["value"]:
                    y["color"] = 'success'
            wltp_ranges.insert(0, {"color": "", "value": "WLTP Range"})

            powers_highest = max(powers, key=lambda x: x['value'])
            powers_lowest = min(powers, key=lambda x: x['value'])
            for y in powers:
                if y["value"] == powers_lowest["value"]:
                    y["color"] = 'danger'
                if y["value"] == powers_highest["value"]:
                    y["color"] = 'success'
            powers.insert(0, {"color": "", "value": "Power"})

            costs_highest = max(costs, key=lambda x: x['value'])
            costs_lowest = min(costs, key=lambda x: x['value'])
            for y in costs:
                if y["value"] == costs_lowest["value"]:
                    y["color"] = 'success'
                if y["value"] == costs_highest["value"]:
                    y["color"] = 'danger'
            costs.insert(0, {"color": "", "value": "Cost"})

            reviews_highest = max(reviews, key=lambda x: x['value'])
            reviews_lowest = min(reviews, key=lambda x: x['value'])
            for y in reviews:
                if y["value"] == reviews_lowest["value"]:
                    y["color"] = 'danger'
                if y["value"] == reviews_highest["value"]:
                    y["color"] = 'success'
            reviews.insert(0, {
                "color": "",
                "value": "Review Score (out of 10)"
            })

        template_values = {
            "reviews": reviews,
            "names": names,
            "manufacturers": manufacturers,
            "years": years,
            "battery_sizes": battery_sizes,
            "wltp_ranges": wltp_ranges,
            "costs": costs,
            "powers": powers,
            "electric_vehicles": electric_vehicles,
            "url": url,
            "url_string": url_string,
            "user": user
        }
        template = JINJA_ENVIRONMENT.get_template(
            "electric_vehicles/compare.html")
        self.response.write(template.render(template_values))

# class to redirect to edit and update classes
class ElectricVehicleForm(BasicReqHandler):
    def get(self, id=None):
        self.response.headers["Content-Type"] = "text/html"
        url = ""
        user = users.get_current_user()
        form_method = 'post'
        if user:
            url = users.create_logout_url(self.request.uri)
            url_string = "logout"
        else:
            url = users.create_login_url(self.request.uri)
            url_string = "login"

        electric_vehicle = ElectricVehicle()
        form_url = '/electric_vehicles/save'
        if id:
            electric_vehicle = ElectricVehicle.get_by_id(int(id))
            form_url = '/electric_vehicles/{}/save'.format(id)

        template_values = {
            "form_method": form_method,
            "id": id,
            "electric_vehicle": electric_vehicle,
            "form_url": form_url,
            "url": url,
            "url_string": url_string,
            "user": user
        }
        template = JINJA_ENVIRONMENT.get_template(
            "electric_vehicles/_form.html")
        self.response.write(template.render(template_values))

# class to show the EV and review
class ElectricVehicleShow(BasicReqHandler):
    def get(self, id=None):
        self.response.headers["Content-Type"] = "text/html"
        url = ""
        user = users.get_current_user()
        review_form_url = '/electric_vehicles/review/'
        if user:
            url = users.create_logout_url(self.request.uri)
            url_string = "logout"
        else:
            url = users.create_login_url(self.request.uri)
            url_string = "login"

        if id:
            electric_vehicle = ElectricVehicle.get_by_id(int(id))
            reviews = Review.query(Review.electric_vehicle == electric_vehicle.
                                   key).order(-Review.date).fetch()
            for_score = [rev.score for rev in reviews]
            avg_review = 0
            if len(for_score):
                avg_review = sum(for_score) / len(for_score)

        template_values = {
            "avg_review": avg_review,
            "reviews": reviews,
            "review_form_url": review_form_url,
            "electric_vehicle": electric_vehicle,
            "url": url,
            "url_string": url_string,
            "user": user
        }
        template = JINJA_ENVIRONMENT.get_template(
            "electric_vehicles/show.html")
        self.response.write(template.render(template_values))

#Class to save the review
class ReviewSave(BasicReqHandler):
    def post(self):
        review = Review(electric_vehicle=ElectricVehicle.get_by_id(
            int(self.request.get('electric_vehicle_id'))).key)
        user = users.get_current_user()
        if user:
            review.content = self.request.get('content')
            review.score = int(self.request.get('score', None))
            review.put()
            self.add_message('Review submitted successfully.', 'success')
        logging.info(review)
        self.redirect('/electric_vehicles/')
        return

# class to save the EV
class ElectricVehicleSave(BasicReqHandler):
    def post(self):
        ev = ElectricVehicle()

        if users.get_current_user():
            ev.name = self.request.get('name')
            ev.manufacturer = self.request.get('manufacturer')
            ev.year = int(self.request.get('year'))
            ev.batterySize = int(self.request.get('batterySize'))
            ev.rangeWltp = int(self.request.get('rangeWltp'))
            ev.cost = int(self.request.get('cost'))
            ev.power = int(self.request.get('power'))
            rec = ElectricVehicle.query(
                ElectricVehicle.name_lower == self.request.get('name').lower(),
                ElectricVehicle.manufacturer_lower == self.request.get('manufacturer').lower(),
                ElectricVehicle.year == int(self.request.get('year'))).fetch(1)
            if len(rec):
                self.add_message('Record already exists.', 'danger')
            else:
                ev.put()
                self.add_message(
                    'Details saved successfully. Please refresh screen.',
                    'success')
                time.sleep(2)

        self.redirect('/electric_vehicles/', abort=False)
        return

# class to update the EV
class ElectricVehicleUpdate(BasicReqHandler):
    def post(self, id):
        if users.get_current_user():
            ev = ElectricVehicle.get_by_id(int(id))
            ev.name = self.request.get('name')
            ev.manufacturer = self.request.get('manufacturer')
            ev.year = int(self.request.get('year'))
            ev.batterySize = int(self.request.get('batterySize'))
            ev.rangeWltp = int(self.request.get('rangeWltp'))
            ev.cost = int(self.request.get('cost'))
            ev.power = int(self.request.get('power'))

            rec = ElectricVehicle.query(
                ElectricVehicle.name_lower == self.request.get('name').lower(),
                ElectricVehicle.manufacturer_lower == self.request.get('manufacturer').lower(),
                ElectricVehicle.year == int(self.request.get('year'))).fetch(1)
            if len(rec) and int(rec[0].key.id()) != int(id):
                self.add_message('Record already exists.', 'danger')
            else:
                ev.put()
                self.add_message(
                    'Details saved successfully. Please refresh screen.',
                    'success')
                time.sleep(2)
        self.redirect('/electric_vehicles/', abort=False)
        return

# welcome to application class
class MainPage(BasicReqHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/html"
        url = ""
        url_string = ""
        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_string = "Logout"
        else:
            url = users.create_login_url(self.request.uri)
            url_string = "Login"

        template_values = {"url": url, "url_string": url_string, "user": user}
        template = JINJA_ENVIRONMENT.get_template("ev.html")
        self.response.write(template.render(template_values))


config = {}
config["webapp2_extras.sessions"] = {
    "secret_key": "_session_key",
}

app = webapp2.WSGIApplication(
    [("/", MainPage), ("/electric_vehicles/save", ElectricVehicleSave),
     ("/electric_vehicles/", ElectricVehicleList),
     ("/electric_vehicles/new", ElectricVehicleForm),
     ("/electric_vehicles/(\d+)", ElectricVehicleForm),
     ("/electric_vehicles/delete/(\d+)", ElectricVehicleDelete),
     ("/electric_vehicles/compare", ElectricVehicleCompare),
     ("/electric_vehicles/show/(\d+)", ElectricVehicleShow),
     ("/electric_vehicles/review/", ReviewSave),
     ("/electric_vehicles/(\d+)/save", ElectricVehicleUpdate)],
    debug=True,
    config=config)
