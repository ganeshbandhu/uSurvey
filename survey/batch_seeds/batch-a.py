from survey.models import *

survey = Survey.objects.create(name='MICS Uganda 2013', description='MICS Uganda 2013')
batch = Batch.objects.create(survey=survey, order=1, name="Batch A")

indicator = Indicator.objects.create(batch=batch, order=1, identifier="TN1")
question_1 = Question.objects.create(indicator=indicator, text="How many people usually live in this household?", answer_type=Question.NUMBER, order=1)

indicator = Indicator.objects.create(batch=batch, order=2, identifier="WS1")
question_2 = Question.objects.create(indicator=indicator, text="What is the household’s main source of drinking water?", answer_type=Question.MULTICHOICE, order=1)
QuestionOption.objects.create(question=question_2, text="Piped tap water", order=1)
QuestionOption.objects.create(question=question_2, text="Borehole", order=2)
QuestionOption.objects.create(question=question_2, text="Protected well/spring", order=3)
QuestionOption.objects.create(question=question_2, text="Unprotected well/spring", order=4)
QuestionOption.objects.create(question=question_2, text="Public tap", order=5)
QuestionOption.objects.create(question=question_2, text="Gravity Flow scheme", order=6)
QuestionOption.objects.create(question=question_2, text="Bottled water", order=7)
QuestionOption.objects.create(question=question_2, text="Tanker-truck/cart", order=8)
QuestionOption.objects.create(question=question_2, text="Surface water (river, stream, dam, lake, pond, canal, irrigation channel)", order=9)
other_option_1 = QuestionOption.objects.create(question=question_2, text="Others", order=10)
sub_question_1 = Question.objects.create(indicator=indicator, text="Describe the source of drinking water", answer_type=Question.TEXT, subquestion=True, parent=question_2)

indicator = Indicator.objects.create(batch=batch, order=3, identifier="WS8")
question_3 = Question.objects.create(indicator=indicator, text="What is the type of toilet that is mainly used in this household?", answer_type=Question.MULTICHOICE, order=1)
QuestionOption.objects.create(question=question_3, text="Flush/Pour flush", order=1)
QuestionOption.objects.create(question=question_3, text="Ventilated Improved Pit (VIP) latrine", order=2)
QuestionOption.objects.create(question=question_3, text="Pit latrine with slab /covered pit", order=3)
QuestionOption.objects.create(question=question_3, text="Pit latrine without slab /uncovered pit", order=4)
QuestionOption.objects.create(question=question_3, text="ECOSAN/Composting toilet", order=5)
QuestionOption.objects.create(question=question_3, text="Hanging toilet/latrine", order=6)
QuestionOption.objects.create(question=question_3, text="No facility, Bush, Field", order=7)
other_option_2 = QuestionOption.objects.create(question=question_3, text="Others", order=8)
sub_question_2 = Question.objects.create(indicator=indicator, text="Describe the type of toilet being used", answer_type=Question.TEXT, subquestion=True, parent=question_3)

indicator = Indicator.objects.create(batch=batch, order=4, identifier="HW4")
question_4 = Question.objects.create(indicator=indicator, text="Does this household have a hand-washing facility at the toilet?", answer_type=Question.MULTICHOICE, order=1)
QuestionOption.objects.create(question=question_4, text="Yes, with water & soap", order=1)
QuestionOption.objects.create(question=question_4, text="Yes, with water only", order=2)
QuestionOption.objects.create(question=question_4, text="No", order=3)

indicator = Indicator.objects.create(batch=batch, order=5, identifier="TN1")
question_5 = Question.objects.create(indicator=indicator, text="Does your household have any mosquito nets that are used while sleeping?", answer_type=Question.MULTICHOICE, order=1)
QuestionOption.objects.create(question=question_5, text="Yes", order=1)
option_5_2 = QuestionOption.objects.create(question=question_5, text="No", order=2)

question_6 = Question.objects.create(indicator=indicator, text="Are these insecticide-treated mosquito nets?", answer_type=Question.MULTICHOICE, order=2)
QuestionOption.objects.create(question=question_6, text="Yes", order=1)
QuestionOption.objects.create(question=question_6, text="No", order=2)
QuestionOption.objects.create(question=question_6, text="Don't Know", order=3)

indicator = Indicator.objects.create(batch=batch, order=6, identifier="TN12")
question_7 = Question.objects.create(indicator=indicator, text="How many children are aged under 5 (FIVE) years in this household?", answer_type=Question.NUMBER, order=1)

question_8 = Question.objects.create(indicator=indicator, text="How many of them slept under a mosquito net last night?", answer_type=Question.NUMBER, order=2)

question_9 = Question.objects.create(indicator=indicator, text="How many pregnant women aged between 15-49 years are in this household?", answer_type=Question.NUMBER, order=3)

question_10 = Question.objects.create(indicator=indicator, text="How many of the currently pregnant women slept under an Insecticide-Treated mosquito net last night?", answer_type=Question.NUMBER, order=4)

# Rules
AnswerRule.objects.create(question=question_2, action=AnswerRule.ACTIONS['ASK_SUBQUESTION'], condition=AnswerRule.CONDITIONS['EQUALS_OPTION'], validate_with_option=other_option_1, next_question=sub_question_1)

AnswerRule.objects.create(question=question_3, action=AnswerRule.ACTIONS['ASK_SUBQUESTION'], condition=AnswerRule.CONDITIONS['EQUALS_OPTION'], validate_with_option=other_option_2, next_question=sub_question_2)

AnswerRule.objects.create(question=question_5, action=AnswerRule.ACTIONS['END_INTERVIEW'], condition=AnswerRule.CONDITIONS['EQUALS_OPTION'], validate_with_option=option_5_2)

AnswerRule.objects.create(question=question_7, action=AnswerRule.ACTIONS['SKIP_TO'], condition=AnswerRule.CONDITIONS['EQUALS'], validate_with_value=0, next_question=question_9)

AnswerRule.objects.create(question=question_5, action=AnswerRule.ACTIONS['SKIP_TO'], condition=AnswerRule.CONDITIONS['EQUALS'], validate_with_option=option_5_2, next_question=question_9)

AnswerRule.objects.create(question=question_8, action=AnswerRule.ACTIONS['REANSWER'], condition=AnswerRule.CONDITIONS['GREATER_THAN_QUESTION'], validate_with_question=question_7)

AnswerRule.objects.create(question=question_9, action=AnswerRule.ACTIONS['END_INTERVIEW'], condition=AnswerRule.CONDITIONS['EQUALS'], validate_with_value=0)

AnswerRule.objects.create(question=question_10, action=AnswerRule.ACTIONS['REANSWER'], condition=AnswerRule.CONDITIONS['GREATER_THAN_QUESTION'], validate_with_question=question_9)