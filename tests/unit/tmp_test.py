from unittest import TestCase
import translator as translator

class Tests(TestCase):
    def test_french_to_english_none(self):
        self.assertIsNone(translator.french_to_english(None))

    def test_english_to_french_none(self):
        self.assertIsNone(translator.english_to_french(None))

    def test_french_to_english(self):
        self.assertEqual(translator.french_to_english("Bonjour"), "Hello")

    def test_english_to_french(self):
        self.assertEqual(translator.english_to_french("Hello"), "Bonjour")



"""
Translate text from English to French and French to English
"""
import os
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

load_dotenv()

apikey = os.environ['apikey']
url = os.environ['url']
print (apikey)
print (url)

authenticator = IAMAuthenticator(apikey)
language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=authenticator
)

language_translator.set_service_url(url)

def english_to_french(english_text):
    """
    Translate english to french
    """
    translation = language_translator.translate(
    text=english_text,
    model_id='en-fr').get_result()
    return translation

def french_to_english(french_text):
    """
    Translate french to english
    """
    translation = language_translator.translate(
    text=french_text,
    model_id='fr-en').get_result()
    return translation