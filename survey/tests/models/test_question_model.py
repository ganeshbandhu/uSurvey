from datetime import date
from django.core.exceptions import ValidationError

from django.test import TestCase
from rapidsms.contrib.locations.models import Location
from survey.models import BatchQuestionOrder, GroupCondition

from survey.models.batch import Batch
from survey.models.backend import Backend
from survey.models.households import Household, HouseholdMember
from survey.models.investigator import Investigator
from survey.models.question import Question, QuestionOption
from survey.models.householdgroups import HouseholdMemberGroup


class QuestionTest(TestCase):
    def setUp(self):
        self.batch = Batch.objects.create(order=1)

    def test_unicode_representation_of_question(self):
        question = Question.objects.create(text="This is a question", answer_type=Question.NUMBER)
        self.assertEqual("%s: (%s)" % (question.text, question.answer_type.upper()), str(question))

    def test_numerical_question(self):
        question = Question.objects.create(text="This is a question", answer_type=Question.NUMBER)
        self.failUnless(question.id)

    def test_text_question(self):
        question = Question.objects.create(text="This is a question", answer_type=Question.TEXT)
        self.failUnless(question.id)

    def test_multichoice_question(self):
        question = Question.objects.create(text="This is a question",
                                           answer_type=Question.MULTICHOICE)
        question.batches.add(self.batch)
        self.failUnless(question.id)

    def test_order(self):
        question_2 = Question.objects.create(text="This is a question", answer_type="number", order=2)
        question_1 = Question.objects.create(text="This is another question", answer_type="number",
                                             order=1)
        question_1.batches.add(self.batch)
        question_2.batches.add(self.batch)
        questions = self.batch.questions.order_by('order').all()
        self.assertEqual(questions[0], question_1)
        self.assertEqual(questions[1], question_2)

    def test_get_next_question_in_batch(self):
        kampala = Location.objects.create(name="Kampala")
        question_2 = Question.objects.create(text="This is a question", answer_type="number", order=2)
        question_1 = Question.objects.create(text="This is another question", answer_type="number",
                                             order=1)
        self.batch.open_for_location(kampala)
        question_1.batches.add(self.batch)
        question_2.batches.add(self.batch)

        self.assertEqual(question_2, question_1.next_question(kampala))

    def test_get_next_question_in_batch_if_sub_question_is_provided(self):
        kampala = Location.objects.create(name="Kampala")
        question_2 = Question.objects.create(text="This is a question", answer_type="number", order=2)
        question_1 = Question.objects.create(text="This is another question", answer_type="number",
                                             order=1)
        sub_question_1 = Question.objects.create(text="This is another question", answer_type="number",
                                                 parent=question_1, subquestion=True)
        self.batch.open_for_location(kampala)
        question_1.batches.add(self.batch)
        question_2.batches.add(self.batch)

        self.assertEqual(question_2, sub_question_1.next_question(kampala))

    def test_cannot_save_subquestion_if_order_given(self):
        question_2 = Question.objects.create(text="This is a question", answer_type="number", order=2)
        subquestion = Question(text="Specify others", answer_type=Question.TEXT, subquestion=True, parent=question_2,
                               order=1)
        self.assertRaises(ValidationError, subquestion.save)

    def test_cannot_save_subquestion_if_parent_not_given(self):
        subquestion = Question(text="Specify others", answer_type=Question.TEXT, subquestion=True)
        self.assertRaises(ValidationError, subquestion.save)

    def test_question_is_subquestion_if_parent_is_given(self):
        question_2 = Question.objects.create(text="This is a question", answer_type="number", order=2)
        subquestion = Question(text="Specify others", answer_type=Question.TEXT, parent=question_2)
        subquestion.save()

        self.assertEqual(False, question_2.subquestion)
        self.assertEqual(True, subquestion.subquestion)

    def test_question_should_know_it_all_question_fields(self):
        question = Question()

        fields = [str(item.attname) for item in question._meta.fields]

        for field in ['id', 'identifier', 'group_id', 'text', 'answer_type', 'order', 'subquestion',
                      'parent_id', 'created', 'modified', 'module_id']:
            self.assertIn(field, fields)

        self.assertEqual(len(fields), 11)

    def test_knows_what_group_question_belongs_to_when_successfully_created(self):
        household_member_group = HouseholdMemberGroup.objects.create(name='Age 4-5', order=1)

        data = {'identifier': 'question',
                'text': "This is a question",
                'answer_type': 'number',
                'order': 1,
                'subquestion': False,
                'group': household_member_group}

        question = Question.objects.create(**data)

        self.assertEqual(household_member_group, question.group)

    def test_knows_has_been_answered_by_member(self):
        backend = Backend.objects.create(name='something')
        kampala = Location.objects.create(name="Kampala")
        investigator = Investigator.objects.create(name="", mobile_number="123456789",
                                                   location=kampala,
                                                   backend=backend)
        household_member_group = HouseholdMemberGroup.objects.create(name='Age 4-5', order=1)

        household = Household.objects.create(investigator=investigator, uid=0)

        household_member = HouseholdMember.objects.create(surname="Member",
                                                          date_of_birth=date(1980, 2, 2), male=False,
                                                          household=household)
        household_member_1 = HouseholdMember.objects.create(surname="Member",
                                                            date_of_birth=date(1980, 2, 2), male=False,
                                                            household=household)

        question_1 = Question.objects.create(identifier="identifier1",
                                             text="Question 1", answer_type='number',
                                             order=1, subquestion=False, group=household_member_group)
        self.batch.questions.add(question_1)
        self.assertFalse(question_1.has_been_answered(household_member, self.batch))
        investigator.member_answered(question_1, household_member, answer=1, batch=self.batch)
        self.assertTrue(question_1.has_been_answered(household_member, self.batch))
        self.assertFalse(question_1.has_been_answered(household_member_1, self.batch))

    def test_knows_subquestions_for_a_question(self):
        question_1 = Question.objects.create(text="question1", answer_type="number", order=1)
        sub_question1 = Question.objects.create(text='sub1', answer_type=Question.NUMBER,
                                                subquestion=True, parent=question_1)
        sub_question2 = Question.objects.create(text='sub2', answer_type=Question.NUMBER,
                                                subquestion=True, parent=question_1)

        self.batch.questions.add(question_1)
        self.batch.questions.add(sub_question1)
        self.batch.questions.add(sub_question2)
        subquestions = question_1.get_subquestions()
        self.assertIn(sub_question1, subquestions)
        self.assertIn(sub_question2, subquestions)

    def test_question_knows_de_associate_self_from_batch(self):
        batch = Batch.objects.create(order=1, name="Test")
        batch_question = Question.objects.create(text="This is a test question", answer_type="multichoice")
        another_batch_question = Question.objects.create(text="This is another test question",
                                                         answer_type=Question.MULTICHOICE)
        batch_question.batches.add(batch)
        another_batch_question.batches.add(batch)

        BatchQuestionOrder.objects.create(question=batch_question, batch=batch, order=1)
        BatchQuestionOrder.objects.create(question=another_batch_question, batch=batch, order=2)

        batch_question.de_associate_from(batch)

        batch_question_order = BatchQuestionOrder.objects.filter(batch=batch, question=batch_question)
        self.failIf(batch_question_order)
        updated_question = Question.objects.filter(text="This is a test question", answer_type="multichoice",
                                                   batches=batch)
        self.failIf(updated_question)

        remaining_batch_order_questions = BatchQuestionOrder.objects.filter(batch=batch,
                                                                            question=another_batch_question)
        self.failUnless(remaining_batch_order_questions)
        self.assertEqual(1, remaining_batch_order_questions[0].order)

    def test_question_knows_it_belongs_to_agroup(self):
        another_group = HouseholdMemberGroup.objects.create(name="GENERAL", order=1)
        general_group = HouseholdMemberGroup.objects.create(name="GENERAL", order=2)

        general_condition = GroupCondition.objects.create(attribute="GENERAL", value="HEAD", condition='EQUALS')
        general_group.conditions.add(general_condition)

        general_question = Question.objects.create(group=general_group, text="General Question 1",
                                                   answer_type=Question.NUMBER,
                                                   order=4, identifier='Q3')
        another_group_question = Question.objects.create(group=another_group, text="General Question 2",
                                                         answer_type=Question.NUMBER,
                                                         order=5, identifier='Q4')

        self.assertTrue(general_question.belongs_to(general_group))
        self.assertFalse(general_question.belongs_to(another_group))

        self.assertTrue(another_group_question.belongs_to(another_group))
        self.assertFalse(another_group_question.belongs_to(general_group))


class QuestionOptionTest(TestCase):
    def setUp(self):
        batch = Batch.objects.create(order=1)
        self.question = Question.objects.create(text="This is a question", answer_type="multichoice")
        batch.questions.add(self.question)

    def test_store(self):
        option_2 = QuestionOption.objects.create(question=self.question, text="OPTION 1", order=2)
        option_1 = QuestionOption.objects.create(question=self.question, text="OPTION 2", order=1)
        options = self.question.options.order_by('order').all()
        self.assertEqual(len(options), 2)
        options_in_text = "1: %s\n2: %s" % (option_1.text, option_2.text)
        self.assertEqual(self.question.options_in_text(), options_in_text)

    def test_question_text(self):
        option_2 = QuestionOption.objects.create(question=self.question, text="OPTION 1", order=2)
        option_1 = QuestionOption.objects.create(question=self.question, text="OPTION 2", order=1)
        question_in_text = "%s\n%s" % (self.question.text, self.question.options_in_text())
        self.assertEqual(self.question.to_ussd(), question_in_text)