import language_tool_python
from transformers import T5ForConditionalGeneration, T5Tokenizer

class TextProcessingAgent:
    def __init__(self, t5_model_name='t5-small'):
        """
        Initializes the TextProcessingAgent.
        Args:
            t5_model_name (str): The name of the T5 model to use for translation
                                 (e.g., 't5-small', 't5-base', or a specific Indic T5 model).
                                 For actual Telugu to English, a model fine-tuned for this
                                 task would be best (e.g., 'ai4bharat/IndicT5-base').
                                 Using 't5-small' as a generic placeholder for now.
        """
        print("Initializing TextProcessingAgent...")
        try:
            self.grammar_tool = language_tool_python.LanguageTool('en-US') # Default to English US for correction
            print("LanguageTool for grammar correction initialized.")
        except Exception as e:
            print(f"Failed to initialize LanguageTool: {e}. Grammar correction might not work.")
            print("Make sure you have a Java runtime installed and language_tool_python is set up correctly.")
            self.grammar_tool = None

        # Initialize T5 model and tokenizer for translation
        # For actual Telugu to English, 'ai4bharat/IndicT5-base' or similar would be more appropriate.
        # We'll use a generic T5 model and prefix for demonstration if a specific one isn't available.
        # The task prefix for T5 for translation from language X to Y is "translate X to Y: "
        self.t5_model_name = t5_model_name
        self.translation_tokenizer = None
        self.translation_model = None
        try:
            print(f"Loading T5 model and tokenizer: {self.t5_model_name} (placeholder for actual Te-En model)...")
            # For a real scenario, you might use:
            # self.actual_t5_model_name = "ai4bharat/IndicT5-base" # or another suitable model
            # self.translation_tokenizer = T5Tokenizer.from_pretrained(self.actual_t5_model_name)
            # self.translation_model = T5ForConditionalGeneration.from_pretrained(self.actual_t5_model_name)

            # Using a generic t5-small as a placeholder for now.
            # This model is NOT trained for Telugu to English.
            self.translation_tokenizer = T5Tokenizer.from_pretrained(self.t5_model_name)
            self.translation_model = T5ForConditionalGeneration.from_pretrained(self.t5_model_name)
            print("T5 model and tokenizer loaded.")
        except Exception as e:
            print(f"Failed to load T5 model '{self.t5_model_name}': {e}")
            print("Translation functionality will be limited.")

        print("TextProcessingAgent initialized.")

    def correct_grammar(self, text: str, language: str = 'en-US') -> str:
        """
        Corrects the grammar of the given text.
        Args:
            text (str): The text to correct.
            language (str): The language of the text (e.g., 'en-US').
                            LanguageTool needs to support this language.
        Returns:
            str: The corrected text.
        """
        if not self.grammar_tool:
            print("Grammar tool not available. Skipping correction.")
            return text

        # If the language of the text is not what the tool is set for, re-initialize.
        # This is a simple way; a more robust way would be to manage multiple tool instances.
        if self.grammar_tool.language != language:
            try:
                print(f"Re-initializing LanguageTool for language: {language}")
                self.grammar_tool = language_tool_python.LanguageTool(language)
            except Exception as e:
                print(f"Failed to initialize LanguageTool for {language}: {e}. Using default.")
                # Fallback to the initially loaded language tool or skip
                if self.grammar_tool.language != 'en-US': # Try to fallback to en-US if not already
                     self.grammar_tool = language_tool_python.LanguageTool('en-US')


        matches = self.grammar_tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)
        if text != corrected_text:
            print(f"Grammar corrected: '{text}' -> '{corrected_text}'")
        return corrected_text

    def translate_telugu_to_english(self, text: str) -> str:
        """
        Translates Telugu text to English using the T5 model.
        Args:
            text (str): The Telugu text to translate.
        Returns:
            str: The translated English text. Returns original text if model not loaded.
        """
        if not self.translation_model or not self.translation_tokenizer:
            print("T5 model/tokenizer not loaded. Skipping translation.")
            return text

        # The prefix is crucial for T5. For a multilingual model like IndicT5,
        # the prefix might be different or it might infer from input.
        # For generic T5, we must specify source and target.
        # This assumes the loaded 't5_model_name' can handle this.
        # A model like 'ai4bharat/IndicT5' would be better suited for Telugu.
        # Example prefix for standard T5: "translate Telugu to English: "
        # Example prefix for IndicT5 (might vary, check model card): "<te> text <en>"

        # Using a generic prefix for the placeholder t5-small.
        # This will likely NOT produce good Telugu to English translation.
        input_text = f"translate Telugu to English: {text}"

        print(f"Translating (T5 placeholder): '{text}'")
        try:
            inputs = self.translation_tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
            outputs = self.translation_model.generate(inputs, max_length=512, num_beams=4, early_stopping=True)
            translated_text = self.translation_tokenizer.decode(outputs[0], skip_special_tokens=True)
            print(f"Translated text: {translated_text}")
            return translated_text
        except Exception as e:
            print(f"Error during T5 translation: {e}")
            return text # Return original text on error

    def process_text(self, text: str, input_language: str = 'en') -> str:
        """
        Processes the text: performs translation if input is Telugu, then grammar correction.
        Args:
            text (str): The input text.
            input_language (str): The language of the input text ('en' for English, 'te' for Telugu).
        Returns:
            str: The processed English text.
        """
        print(f"Processing text. Input language: {input_language}")
        processed_text = text

        if input_language == 'te':
            print("Input is Telugu, attempting translation to English.")
            processed_text = self.translate_telugu_to_english(text)
            # After translation, the text is English, so grammar correction should use 'en-US'
            processed_text = self.correct_grammar(processed_text, language='en-US')
        elif input_language == 'en':
            print("Input is English, attempting grammar correction.")
            processed_text = self.correct_grammar(text, language='en-US')
        else:
            print(f"Unsupported language: {input_language}. Skipping processing.")
            return text

        print(f"Final processed text: {processed_text}")
        return processed_text

if __name__ == '__main__':
    # Example Usage:
    # For real Telugu translation, you'd pass a model like 'ai4bharat/IndicT5-base'
    # For this example, 't5-small' is used as a placeholder and WILL NOT translate Telugu well.
    agent = TextProcessingAgent(t5_model_name='t5-small')

    print("\n--- English Grammar Correction Example ---")
    english_text_bad_grammar = "he go to school yesterday. she dont like ice cream."
    corrected_english = agent.process_text(english_text_bad_grammar, input_language='en')
    # Expected: "He went to school yesterday. She doesn't like ice cream." (or similar)

    print("\n--- Telugu to English Translation Example (using t5-small placeholder) ---")
    # This Telugu phrase means "My name is Copilot."
    # The t5-small model is not trained for this and will likely output garbage or repeat the input.
    telugu_text = "నా పేరు కోపైలట్"
    translated_and_corrected_telugu = agent.process_text(telugu_text, input_language='te')
    # Expected with a proper Te-En model: "My name is Copilot." (or similar, then grammar checked)
    # With t5-small, expect something nonsensical.

    print("\nNote: Telugu to English translation with 't5-small' is a placeholder.")
    print("A model fine-tuned for Telugu to English (e.g., from ai4bharat) is required for accurate translation.")
    print("LanguageTool requires a Java Runtime Environment.")
