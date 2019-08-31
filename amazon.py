from botocore.vendored import requests







def lambda_handler(event, context):
    if event['session']['new']:
        on_start()
    if event['request']['type'] == "IntentRequest":
        return intent_scheme(event)
    elif event['request']['type'] == "LaunchRequest":
        return on_launch(event)
    elif event['request']['type'] == "SessionEndedRequest":
        return on_end()


def on_start():
    print("Session Started.")



def on_launch(event):
    onlunch_MSG = (
        "Hi, welcome to Daily Value."
        + " Provide any ingredient and a nutrition value, "
        + "and I will respond with the amount of said value present in 100 grams of the ingridient, "
        + "and it's daily value percentage"
    )
    reprompt_MSG = "please provide an ingredient"
    card_TEXT = "Provide an ingredient."
    card_TITLE = "Provide an ingredient."
    return output_json_builder_with_reprompt_and_card(
        onlunch_MSG, card_TEXT, card_TITLE, reprompt_MSG, False
    )


def intent_scheme(event):
    intent_name = event['request']['intent']['name']

    if intent_name == "GetValueIntent":
        return GetValue(event)
    elif intent_name in [
        "AMAZON.NoIntent",
        "AMAZON.StopIntent",
        "AMAZON.CancelIntent",
    ]:
        return stop_the_skill(event)
    elif intent_name == "AMAZON.HelpIntent":
        return assistance(event)
    elif intent_name == "AMAZON.FallbackIntent":
        return fallback_call(event)
    elif intent_name == "LaunchRequest":
        return on_launch(event)


def on_end():
    print("Session Ended.")


def GetValue(event):
    ingredient = event['request']['intent']['slots']['ingredient']['value']
    value = event['request']['intent']['slots']['nutrition']['value']
    ingredient.replace("", "%20")
    url = (
        'https://api.edamam.com/api/nutrition-data?app_id=f6be31fa&app_key=660e5eed08584478030c8b7ceed10b36&ingr=100%20gram%20'
        + ingredient
    )
    response = requests.get(url)
    print(response.json())
    if value == 'calories':
        key = int(response.json()['totalNutrients']['ENERC_KCAL']['quantity'])
        dailyValue = int(response.json()['totalDaily']['ENERC_KCAL']['quantity'])
        value = "".join(
            [
                "the number of calories in ",
                ingredient,
                " is ",
                str(key),
                " calories, which is ",
                str(dailyValue),
                "% of the recommended daily value."
            ]
        )
        reprompt_MSG = "please provide an ingredient"
        card_TEXT = "processing " + ingredient
        card_TITLE = "processing " + ingredient
        return output_json_builder_with_reprompt_and_card(
            value, card_TEXT, card_TITLE, reprompt_MSG, True)
    else:
        for v in response.json()['totalNutrients']:
            if (response.json()['totalNutrients'][v]['label']).lower() == value:
                key = response.json()['totalNutrients'][v]['quantity']
                dailyValue = int(response.json()['totalDaily'][v]['quantity'])
                if response.json()['totalNutrients'][v]['unit'] == 'mg':
                    unit = 'miligrams'
                else:
                    unit = 'grams'
                value = "".join(
                    [
                        "the amount of " + value +  " in ",
                        ingredient,
                        " is ",
                        str(key),
                        " " + unit + ", which is ",
                        str(dailyValue),
                        "% of the recommended daily value."
                    ]
                )
                reprompt_MSG = "please provide an ingredient"
                card_TEXT = "processing " + ingredient
                card_TITLE = "processing " + ingredient
                return output_json_builder_with_reprompt_and_card(
                    value, card_TEXT, card_TITLE, reprompt_MSG, True)


def stop_the_skill(event):
    stop_MSG = "Thank you. Bye!"
    reprompt_MSG = ""
    card_TEXT = "Bye."
    card_TITLE = "Bye Bye."
    return output_json_builder_with_reprompt_and_card(
        stop_MSG, card_TEXT, card_TITLE, reprompt_MSG, True
    )


def assistance(event):
    assistance_MSG = (
        "you need to provide an ingredient in order"
        + " to receive it's daily value."
    )
    reprompt_MSG = "please provide an ingredient"
    card_TEXT = "You've asked for help."
    card_TITLE = "Help"
    return output_json_builder_with_reprompt_and_card(
        assistance_MSG, card_TEXT, card_TITLE, reprompt_MSG, False
    )


def fallback_call(event):
    fallback_MSG = (
        "I can't help you with that, try rephrasing the"
        + " question or ask for help by saying HELP."
    )
    reprompt_MSG = "please provide an ingredient"
    card_TEXT = "You've asked a wrong question."
    card_TITLE = "Wrong question."
    return output_json_builder_with_reprompt_and_card(
        fallback_MSG, card_TEXT, card_TITLE, reprompt_MSG, False
    )


def plain_text_builder(text_body):
    text_dict = {}
    text_dict['type'] = 'PlainText'
    text_dict['text'] = text_body
    return text_dict


def reprompt_builder(repr_text):
    reprompt_dict = {}
    reprompt_dict['outputSpeech'] = plain_text_builder(repr_text)
    return reprompt_dict


def card_builder(c_text, c_title):
    card_dict = {}
    card_dict['type'] = "Simple"
    card_dict['title'] = c_title
    card_dict['content'] = c_text
    return card_dict


def response_field_builder_with_reprompt_and_card(
    outputSpeach_text, card_text, card_title, reprompt_text, value
):
    speech_dict = {}
    speech_dict['outputSpeech'] = plain_text_builder(outputSpeach_text)
    speech_dict['card'] = card_builder(card_text, card_title)
    speech_dict['reprompt'] = reprompt_builder(reprompt_text)
    speech_dict['shouldEndSession'] = value
    return speech_dict


def output_json_builder_with_reprompt_and_card(
    outputSpeach_text, card_text, card_title, reprompt_text, value
):
    response_dict = {}
    response_dict['version'] = '1.0'
    response_dict['response'] = response_field_builder_with_reprompt_and_card(
        outputSpeach_text, card_text, card_title, reprompt_text, value
    )
    return response_dict
