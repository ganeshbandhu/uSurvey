import json

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist

from rapidsms.contrib.locations.models import *
from survey.forms.householdHead import *
from survey.forms.children import *
from survey.forms.women import *
from survey.forms.household import *
from survey.views.views_helper import initialize_location_type, update_location_type, get_posted_location
from survey.models import *


CREATE_HOUSEHOLD_DEFAULT_SELECT = ''


def _add_error_response_message(householdform, request):
    error_message = "Household not registered. "
    messages.error(request, error_message + "See errors below.")

    for key in householdform.keys():
        form = householdform[key]
        if form.non_field_errors():
            for err in form.non_field_errors():
                messages.error(request, error_message + str(err))


def validate_investigator(request, householdform, posted_locations):
    investigator_form = {'value': '', 'text': '', 'error': '',
                         'options': Investigator.objects.filter(location__in=posted_locations)}
    investigator = None
    try:
        investigator = Investigator.objects.get(id=int(request.POST['investigator']))
        investigator_form['text'] = investigator.name
        investigator_form['value'] = investigator.id
    except MultiValueDictKeyError:
        message = "No investigator provided."
        investigator_form['error'] = message
        householdform.errors['__all__'] = householdform.error_class([message])
    except (ObjectDoesNotExist, ValueError):
        investigator_form['text'] = request.POST['investigator']
        investigator_form['value'] = request.POST['investigator']
        message = "You provided an unregistered investigator."
        investigator_form['error'] = message
        householdform.errors['__all__'] = householdform.error_class([message])
    return investigator, investigator_form

def create_household(householdform, investigator, valid):
    is_valid_household = householdform['household'].is_valid()
    if investigator and is_valid_household:
        householdform['household'].instance.investigator = investigator
        householdform['household'].save()
        valid['household'] = True
    return valid

def create_remaining_modelforms(householdform, valid):
    if valid['household']:
        remaining_keys = ['children','householdHead',  'women']
        for key in remaining_keys:
            householdform[key].instance.household = householdform['household'].instance
            is_valid_form = householdform[key].is_valid()
            if is_valid_form:
                householdform[key].save()
                valid[key] = True
    return valid

def delete_created_modelforms(householdform, valid):
    for key in valid.keys():
        householdform[key].instance.delete()

def _process_form(householdform, investigator, request):
    valid = {}
    valid = create_household(householdform, investigator, valid)
    valid = create_remaining_modelforms(householdform, valid)

    if valid.values().count(True) == len(householdform.keys()):
        messages.success(request, "Household successfully registered.")
        return HttpResponseRedirect("/households/new")

    delete_created_modelforms(householdform, valid)
    _add_error_response_message(householdform, request)
    return None

def set_household_form(data):
    householdform = {}
    householdform['householdHead'] = HouseholdHeadForm(data=data, auto_id='household-%s', label_suffix='')
    householdform['children'] = ChildrenForm(data=data, auto_id='household-children-%s', label_suffix='')
    householdform['women'] = WomenForm(data=data, auto_id='household-women-%s', label_suffix='')
    householdform['household'] = HouseholdForm(data=data, auto_id='household-%s', label_suffix='')
    return householdform

def create(request, location_type):
    defaults = {"aged_between_0_5_months": 0, "aged_between_6_11_months": 0,
                "aged_between_12_23_months": 0, "aged_between_24_59_months": 0,
                'aged_between_5_12_years':0, 'aged_between_13_17_years':0,
                'aged_between_15_19_years': 0, 'aged_between_20_49_years': 0}
    params = dict(defaults.items() + request.POST.items())
    householdform = set_household_form(data=params)
    location_id = get_posted_location(request.POST)
    location_type = update_location_type(location_type, location_id)
    posted_locations = Location.objects.get(id=int(location_id)).get_descendants(include_self=True)
    investigator, investigator_form = validate_investigator(request, householdform['household'], posted_locations)
    response = _process_form(householdform, investigator, request)

    return response, householdform, investigator, investigator_form

def new(request):
    location_type = initialize_location_type(default_select=CREATE_HOUSEHOLD_DEFAULT_SELECT)
    response = None
    householdform = set_household_form(data=None)
    investigator_form = {'value': '', 'text': '', 'options': Investigator.objects.all(), 'error': ''}
    month_choices= {'selected_text':'', 'selected_value':''}
    year_choices= {'selected_text':'', 'selected_value':''}


    if request.method == 'POST':
        response, householdform, investigator, investigator_form = create(request, location_type)
        month_choices={'selected_text':MONTHS[int(request.POST['resident_since_month'])][1],
                        'selected_value':request.POST['resident_since_month']    }
        year_choices={'selected_text':request.POST['resident_since_year'],
                        'selected_value':request.POST['resident_since_year']    }


    householdHead = householdform['householdHead']
    del householdform['householdHead']
    return response or render(request, 'households/new.html', {'location_type': location_type,
                                                               'investigator_form': investigator_form,
                                                               'headform': householdHead,
                                                               'householdform': householdform,
                                                               'months_choices': householdHead.resident_since_month_choices(month_choices),
                                                               'years_choices': householdHead.resident_since_year_choices(year_choices),
                                                               'action': "/households/new/",
                                                               'id': "create-household-form",
                                                               'button_label': "Create Household",
                                                               'loading_text': "Creating..."})

def get_investigators(request):
    location = request.GET['location'] if request.GET.has_key('location') and request.GET['location'] else None
    investigators = Investigator.objects.filter(location=location)
    investigator_hash = {}
    for investigator in investigators:
        investigator_hash[investigator.name] = investigator.id
    return HttpResponse(json.dumps(investigator_hash), content_type="application/json")

