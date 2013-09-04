from lettuce import *
from random import randint
from survey.models import GroupCondition, HouseholdMemberGroup
from survey.features.page_objects.household_member_groups import GroupConditionListPage, GroupsListingPage, AddConditionPage, AddGroupPage, GroupConditionModalPage


@step(u'And I have 10 conditions')
def and_i_have_10_conditions(step):
    for _ in xrange(10):
        random_number = str(randint(1, 99999))
        try:
            GroupCondition.objects.create(value=random_number, attribute=str(random_number), condition="EQUALS")
        except Exception:
            pass


@step(u'And I visit conditions listing page')
def and_i_visit_conditions_listing_page(step):
    world.page = GroupConditionListPage(world.browser)
    world.page.visit()


@step(u'And I should see the conditions list')
def and_i_should_see_the_conditions_list(step):
    world.page.validate_fields()


@step(u'And I have a condition')
def and_i_have_a_condition(step):
    world.condition = GroupCondition.objects.create(value=5, attribute="male", condition="EQUALS")


@step(u'And I have 100 groups with that condition')
def and_i_have_100_groups_with_that_condition(step):
    for _ in xrange(100):
        random_number = randint(1, 99999)
        try:
            HouseholdMemberGroup.objects.create(order=random_number, name="group %d" % random_number)
        except Exception:
            pass


@step(u'And I visit groups listing page')
def and_i_visit_groups_listing_page(step):
    world.page = GroupsListingPage(world.browser)
    world.page.visit()


@step(u'Then I should see the groups list paginated')
def then_i_should_see_the_groups_list_paginated(step):
    world.page.validate_fields()
    world.page.validate_pagination()


@step(u'When I click the add button')
def when_i_click_the_add_button(step):
    world.page.click_link_by_text(" Add Condition")


@step(u'Then I should see the new condition form')
def then_i_should_see_the_new_condition_form(step):
    world.page.is_text_present("New condition")


@step(u'And I visit the new condition page')
def and_i_visit_the_new_condition_page(step):
    world.page = AddConditionPage(world.browser)
    world.page.visit()


@step(u'When I fill in the condition details')
def when_i_fill_in_the_condition_details(step):
    data = {'attribute': 'rajni',
            'value': 'kant'}
    world.page.fill_valid_values(data)


@step(u'And I click save button')
def and_i_click_save_button(step):
    world.page.submit()


@step(u'Then I should see that the condition was saved successfully')
def then_i_should_see_that_the_condition_was_saved_successfully(step):
    world.page.see_success_message('Condition', 'added')


@step(u'And I visit the new group page')
def and_i_visit_the_new_group_page(step):
    world.page = AddGroupPage(world.browser)
    world.page.visit()


@step(u'When I fill in the group details')
def when_i_fill_in_the_group_details(step):
    data = {'name': 'aged between 15 and 49',
            'order': 1,
            'condition': world.condition.id}
    world.page.fill_valid_values(data)


@step(u'Then I should see that the group was saved successfully')
def then_i_should_see_that_the_group_was_saved_successfully(step):
    world.page.see_success_message('Group', 'added')


@step(u'When I click the add new condition')
def when_i_click_the_add_new_condition(step):
    world.page.click_link_by_text("Add condition ")


@step(u'Then I should see the modal open')
def then_i_should_see_the_modal_open(step):
    world.page = GroupConditionModalPage(world.browser)
    world.page.validate_contents()


@step(u'And I click the save button')
def and_i_click_the_save_button(step):
    world.page.click_button("save_condition_button")


@step(u'Then I should see the condition was saved successfully')
def then_i_should_see_the_condition_was_saved_successfully(step):
    world.page.see_success_message("Condition", "added")


@step(u'And I should see the new condition in the groups form')
def and_i_should_see_the_new_condition_in_the_groups_form(step):
    latest_condition = GroupCondition.objects.get(value='kant', attribute="rajni", condition="EQUALS")
    world.page.validate_latest_condition(latest_condition)


@step(u'And I have 2 conditions')
def and_i_have_2_conditions(step):
    world.condition_1 = GroupCondition.objects.create(value='True', attribute="male", condition="EQUALS")
    world.condition_2 = GroupCondition.objects.create(value=35, attribute="age", condition="EQUALS")


@step(u'When I fll name and order')
def when_i_fll_name_and_order(step):
    data = {'name': 'aged between 15 and 49',
            'order': 1}
    world.page.fill_valid_values(data)


@step(u'And I select conditions')
def and_i_select_conditions(step):
    world.page.select_multiple('#condition',world.condition_1, world.condition_2)