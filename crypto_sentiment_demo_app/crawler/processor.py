import pandas as pd
from spacy.lang.en import English as SpacyEnglishPipeline
from spacy.language import Language
from spacy_langdetect import LanguageDetector


class TitleProcessor:
    def __init__(self, spacy_model: SpacyEnglishPipeline):
        """
        :param spacy_model: Spacy pipeline: spacy.lang.en.English object
        """
        self.spacy_model = spacy_model
        TitleProcessor.__enable_langdetect_with_spacy(spacy_model=self.spacy_model)

    @staticmethod
    def get_lang_detector_spacy(nlp: SpacyEnglishPipeline, name: str):
        """
        A function to be used to add a Spacy language detector pipeline.
        Taken from here:
        https://stackoverflow.com/questions/66712753/how-to-use-languagedetector-from-spacy-langdetect-package
        :param nlp: Spacy pipeline: spacy.lang.en.English object
        :param name: pipeline name
        :return:
        """
        return LanguageDetector()

    @staticmethod
    def __enable_langdetect_with_spacy(spacy_model: SpacyEnglishPipeline):
        Language.factory("language_detector", func=TitleProcessor.get_lang_detector_spacy)
        spacy_model.add_pipe("language_detector", last=True)

    @staticmethod
    def __filter_out_question_marks(df: pd.DataFrame, text_col_name: str = "title") -> pd.DataFrame:
        """
        A primitive method returning True if a question mark is found in the text
        :param df: a DataFrame
        :param text_col_name: column name to filter on
        :return: bool
        """
        return df.loc[~df[text_col_name].str.contains(r"\?")]

    def __filter_verbs_spacy(self, df: pd.DataFrame, text_col_name: str = "title") -> pd.DataFrame:
        """
        A primitive method returning True if a question mark is found in the text
        :param df: a DataFrame
        :param text_col_name: column name to filter on
        :return: bool
        """
        return df.loc[
            df[text_col_name].apply(
                lambda sent: TitleProcessor.__has_verb_spacy(sent=sent, spacy_model=self.spacy_model)
            )
        ]

    @staticmethod
    def __has_verb_spacy(sent: str, spacy_model: SpacyEnglishPipeline) -> bool:
        """
        Determines whether a string `sent` contains a verb, according to the Spacy model.
        :param sent: any string
        :param spacy_model: Spacy pipeline: spacy.lang.en.English object
        :return: bool
        """
        # https://ashutoshtripathi.com/2020/04/13/parts-of-speech-tagging-and-dependency-parsing-using-spacy-nlp/
        doc = spacy_model(sent)

        verb_found = False
        for t in doc:
            if t.pos_ == "VERB":
                verb_found = True
                break

        return verb_found

    @staticmethod
    def __filter_on_text_length(
        df: pd.DataFrame, text_col_name: str = "title", min_length_words: int = 6
    ) -> pd.DataFrame:
        """
        Leave only texts in `text_col_name` column of the DataFrame `df` that are longer than
        `min_length_words` words.
        :param df: a DataFrame
        :param text_col_name: column name to filter on
        :param min_length_words: minimal number of words
        :return: bool
        """
        return df.loc[df[text_col_name].apply(lambda sent: len(sent.split())) >= min_length_words]

    def __filter_out_non_english_spacy(self, df: pd.DataFrame, text_col_name: str = "title") -> pd.DataFrame:
        """
        A primitive method returning True if a question mark is found in the text
        :param df: a DataFrame
        :param text_col_name: column name to filter on
        :return: bool
        """
        return df.loc[
            df[text_col_name].apply(
                lambda sent: TitleProcessor.__is_english_spacy(text=sent, spacy_model=self.spacy_model)
            )
        ]

    @staticmethod
    def __is_english_spacy(text: str, spacy_model: SpacyEnglishPipeline, min_confidence: float = 0.8) -> bool:
        """
        Determines if  a text is in English, according to the Spacy language detector.
        :param text: any string
        :param spacy_model: Spacy pipeline: spacy.lang.en.English object
        :param min_confidence: minimal language classifier confidence
        :return: whether the text is in English, according to the Spacy language detector
        """
        doc = spacy_model(text, disable=["ner", "tok2vec"])
        lang, confidence = doc._.language["language"], doc._.language["score"]

        return (lang == "en") and (confidence >= min_confidence)

    @staticmethod
    def __filter_on_publication_date(
        df: pd.DataFrame, min_date: str, pub_timestamp_col_name: str = "pub_time"
    ) -> pd.DataFrame:
        """
        Leave only texts in `text_col_name` column of the DataFrame `df` that are longer than
        `min_length_words` words.
        :param df: a DataFrame
        :param min_date: date formatted as YYYY-MM-DD
        :param pub_timestamp_col_name: column name to filter on
        :return: bool
        """
        return df.loc[df[pub_timestamp_col_name] >= min_date]

    def filter_titles(
        self, df: pd.DataFrame, min_date: str, text_col_name: str = "title", pub_timestamp_col_name: str = "pub_time"
    ) -> pd.DataFrame:
        """
        Applies filters on `text_col_name` column of the DataFrame `df`.
        :param df: a crawled pandas DataFrame
        :param min_date: oldest publication date to keep, formatted as YYYY-MM-DD
        :param text_col_name: column name with text to filter on
        :param pub_timestamp_col_name: column name with publication date to filter on
        :return: a filtered DataFrame
        """

        tmp_df = self.__filter_on_publication_date(
            df=df, pub_timestamp_col_name=pub_timestamp_col_name, min_date=min_date
        )
        tmp_df1 = self.__filter_out_question_marks(df=tmp_df, text_col_name=text_col_name)
        tmp_df2 = self.__filter_on_text_length(df=tmp_df1, text_col_name=text_col_name)
        tmp_df3 = self.__filter_verbs_spacy(df=tmp_df2, text_col_name=text_col_name)
        result_df = self.__filter_out_non_english_spacy(df=tmp_df3, text_col_name=text_col_name)

        return result_df
