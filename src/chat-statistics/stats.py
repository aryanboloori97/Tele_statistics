import json
from pathlib import Path
from typing import Union
from collections import defaultdict


from hazm import Normalizer, word_tokenize
from loguru import logger
from wordcloud import WordCloud

from src.data import DATA_DIR


class ChatStatistics(object):
    """
    Generates chat statistics for any given JSON file of telegram groups or channels 
    """
    def __init__(self, input_json:Union[str, Path]): 
        """
        :param input_json: This is the address of JSON file in pathlib.Path format, or in string representing the absoulte address
        """
        logger.info(f'Loading chat data from {input_json}...')
        self.normalizer = Normalizer()
        with open(input_json, 'r') as f:
            self.input_json = json.load(f)
        logger.info('Loading chat data from  " DATA_DIR / stop_words.txt " ...') 
        # Load the stop words, which should be removed
        with open(DATA_DIR / 'stop_words.txt', 'r') as f:
            self.stop_words = list(map(str.strip, (list(f.readlines()))))
    
        self.stop_words = list(map(self.normalizer.normalize, self.stop_words))

    def generate_word_cloud(self, output_name:str):
        """ This method is used to figure out which words exist most in any telegram group or channel
        
        :param output_name : This argument is the name of an output png file as string on which the word cloud picture will be saved.
        Note: The output png file will be saved in this path:
        --->>> /src/data 
        
            
        """
        logger.info("Generating word cloud...")
        messages = ''
        for msg in self.input_json['messages']:
            if isinstance(msg['text'], str):
                messages += (msg['text'] + " ")
            elif isinstance(msg['text'], list):
                for sub_msg in msg['text']:
                    if isinstance(sub_msg, str):
                        messages += (sub_msg + " ")
                    elif isinstance(sub_msg, dict):
                        if not(sub_msg['type'] == 'link') and not(sub_msg['type'] == 'text_link'):
                            messages += (sub_msg['text'] + " ")
        
        tokens = word_tokenize(messages)
        tokens = list(filter(lambda item:item not in self.stop_words, tokens))
        messages = " ".join(tokens)
        messages = self.normalizer.normalize(messages)
        # lower max_font_size
        wordcloud = WordCloud(width=1200, height=1200, background_color='white', max_font_size=50, font_path='/home/aryan/Desktop/pytopia_python/Practices/Tele_statistics/src/data/NotoNaskhArabic-Regular.ttf').generate(messages)
        logger.info(f"Saving word cloud as png file to {DATA_DIR}...")
        wordcloud.to_file(Path(DATA_DIR /output_name))
        logger.info("Successfully Done!")
        logger.info("Please go to src/data path to see your png file :)")

    def users_most_replied(self, number:int=1):
        list_of_users = defaultdict()
        for message in self.input_json['messages']:
            if message['type'] == 'message':
                list_of_users[(message['from'])] = 0
        for message in self.input_json['messages']:
            if message.get('reply_to_message_id'):
                list_of_users[(message['from'])] +=1

        list_of_users_sorted = sorted(list_of_users.items(), key=lambda k_v: k_v[1], reverse=True)
        for item in list_of_users_sorted[0:number]:
        
            print(f'User: {item[0]}, Replies: {item[1]}')








if __name__ == '__main__':
    test = ChatStatistics(input_json=DATA_DIR / 'result.json')
    # test.generate_word_cloud('first.png')
    test.users_most_replied(30)
    