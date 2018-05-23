# -*- coding:utf-8 -*-
# master project

from watson_developer_cloud import conversation_v1
import json
import os

# ================================================
#   watson info
# ================================================
WATSON_USERNAME = os.getenv('watson_username')
WATSON_PASSWORD = os.getenv('watson_password')
WATSON_URL = 'https://gateway.aibril-watson.kr/conversation/api'
WATSON_WORKSPACE = os.getenv('watson_workspace')
WATSON_VERSION = '2017-10-26'
# WATSON_VERSION = '2018-02-16'
CONTEXT = {'timezone': 'Asia/Seoul'}


class Aibril:
    def __init__(self):
        self.context = {'timezone': 'Asia/Seoul'}
        self.watson_conv_id = ''
        self.conversation = None

        # print('check check >> {}'.format(WATSON_USERNAME))

        self.connection()

    def connection(self):
        try:
            self.conversation = conversation_v1.ConversationV1(
                username=WATSON_USERNAME,
                password=WATSON_PASSWORD,
                version=WATSON_VERSION,
                url=WATSON_URL
            )
            response = self.conversation.message(workspace_id=WATSON_WORKSPACE,
                                                 message_input={'text': ''},
                                                 context=self.context)
            self.watson_conv_id = response['context']['conversation_id']
            # print('self.watson_conv_id >> {}'.format(self.watson_conv_id))
            self.context['conversation_id'] = self.watson_conv_id

        except Exception as e:
            print('\n\t connected to Aibril conversation server >> ', e)

    # def translator_connection(self):
    #     try:
    #         self.language_translator = Lan
    #
    # def translation(self, trans_text, model_id):
    #     if self.connection()

    def response(self, rec_stt):
        if self.watson_conv_id == '':
            self.connection()

        response = self.conversation.message(
            workspace_id=WATSON_WORKSPACE,
            message_input={'text': rec_stt},
            context=self.context
        )

        json_response = json.dumps(response, indent=2, ensure_ascii=False)
        dict_response = json.loads(json_response)
        # print('\njson_response >> {}'.format(json_response))

        try:
            # --------------------------------------------------
            #   << parsing response >>

            result_conv = dict_response['output']['text'][0]

            try:
                header = dict_response['output']['header']
                print('header type {}'.format(type(header)))
            except Exception as e:
                header = {"command": "chat"}
                print("It dosen't have Header >> {}".format(e))

            # check this action
            # 다음 문장 추가해서 읽는 것 같은데, 이건 왜 하는 건가?
            # if len(dict_response['output']['text']) > 1:
            #     result_conv += " " + dict_response['output']['text'][1]

            # --------------------------------------------------
            #   << update context >>

            self.context.update(dict_response['context'])
            # print('\n\nself.context.update >> {}'.format(self.context))

            # --------------------------------------------------
            #  <<  Check conversation is end or durable >>

            if 'branch_exited' in dict_response['context']['system']:
                conv_flag = True
            else:
                conv_flag = False
            # --------------------------------------------------
            #   << Check Translate >>
            try:
                language = (result_conv.split())[-1]
            except Exception as e:
                language = 'trans_ko'
                print("It dosen't have Text >> {}".format(e))

            if language == 'trans_en':
                language = 'en'
            elif language == 'trans_ja':
                language = 'ja'
            elif language == 'trans_zh':
                language = 'zh'
            else:
                language = 'ko'

        except Exception as e:
            # self.logger.write_critical(e)
            result_conv = "다시 한번 말씀해주세요."
            # --------------------------------------------------

        return header, result_conv, language


if __name__ == "__main__":
    aibril = Aibril()
    text = '안녕'
    while True:
        header, text, language = aibril.response(text)
        print('header >> {}\ntext >> {}\nlanguage >> {}'.format(header, text, language))
        text = input('\n\t 입력 >> ')
        if text == '종료':
            break
