import json
from collections import Counter
from pathlib import Path
from typing import Union

import arabic_reshaper
from bidi.algorithm import get_display
from hazm import Normalizer, word_tokenize
from loguru import logger
from src.data import DATA_DIR
from wordcloud import WordCloud


class ChatStatistics:
    """Generate chat statistics from a telegram chat json file
    """
    def __init__(self, chat_json: Union[str, Path]):
        """Generate a word cloud from a chat data
        :pram output_dir: path to output directory
        :type chat_json: Union[str, path]
        """

        #load chat data
        logger.info(f'Loading chat data from {chat_json}')
        with open(chat_json) as f:
            self.chat_data = json.load(f)
        

        self.normalizer = Normalizer()


        #load stopwords
        logger.info(f"Loading stopwords from {DATA_DIR / 'stopwords.txt'}")
        stop_words = open(DATA_DIR / 'stopwords.txt').readlines()
        stop_words = list(map(str.strip, stop_words))
        self.stop_words = list(map(self.normalizer.normalize, stop_words))


    #generate word cloud
    def generate_word_cloud ( 
        self,
        output_dir: Union[str, Path], 
        width: int= 800, height: int =1200,
        max_font_size: int = 250,
        background_color : str = "white",
        ):
        """Generates a word cloud from the chat data
        :param output_dir: path to output directory for word cloud image
        """
        logger.info(f"Loading text content")
        text_content = ''

        for msg in self.chat_data['messages']:
            if type(msg['text']) is str:
                tokens = word_tokenize(msg['text'])
                tokens = list(filter(lambda item: item not in self.stop_words, tokens))
                text_content += f"{''.join(tokens)}"

        
        # Normaliz, reshape for final word cloud
        text_content = self.normalizer.normalize(text_content)
        text_content = arabic_reshaper.reshape(text_content)
        text_content = get_display(text_content)

        logger.info(f"Generating word cloud...")
        # generate word cloud
        wordcloud = WordCloud(
            height = 1200,
            width= 1200,
            font_path= str(DATA_DIR / 'BHoma.ttf'),
            background_color= background_color
        ).generate(text_content)
        
        logger.info(f"Saving word cloud to {output_dir}")
        wordcloud.to_file(Path(output_dir) / 'wordcloud.png')

if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json=DATA_DIR / 'online.json')
    chat_stats.generate_word_cloud(output_dir= DATA_DIR)

    print('Done!')
