# -*- coding:utf-8 -*-

from watson_developer_cloud import conversation_v1
import json
import sys
import os

class WatsonServer:
    def __init__(self):
        self.watson_username = os.getenv('watson_username')
        self.watson_password = os.getenv('watson_password')
        self.watson_workspace = os.getenv('watson_workspace')
        self.watson_url = os.getenv('watson_url')
        self.watson_version = os.getenv('watson_version')

        self.context = {'timezone': 'Asia/Seoul'}
        self.watson_conv_id = ''
        self.conversation = None
        self.aibril_conv_connect()

    def aibril_conv_connect(self):
        try:
            self.conversation = conversation_v1.ConversationV1(username=self.watson_username,
                                                               password=self.watson_password,
                                                               version=self.watson_version,
                                                               url=self.watson_url)
            response = self.conversation.message(workspace_id=self.watson_workspace,
                                                 message_input={'text': ''},
                                                 context=self.context)
            self.watson_conv_id = response['context']['conversation_id']
            self.context['conversation_id'] = self.watson_conv_id

        except Exception as e:
            # self.logger.write_critical("cannot connect Aibril conversation server!!!")
            return "에이브릴 대화서버에 접속 할 수 없습니다."

        print("Connected to Aibril Conversation Server")

    def aibril_conv(self, text):
        if self.watson_conv_id == '':
             self.aibril_conv_connect()

        response = self.conversation.message(workspace_id=self.watson_workspace,
                                             message_input={'text': text},
                                             context=self.context)
        json_response = json.dumps(response, indent=2, ensure_ascii=False)
        dict_response = json.loads(json_response)

        # ==================================================
        #   Debug response print
        # ==================================================
        # self.logger.write_debug(dict_response)

        try:
            # ==================================================
            #   Parsing response
            # ==================================================
            result_conv = dict_response['output']['text'][0]
            if len(dict_response['output']['text']) > 1:
                result_conv += " " + dict_response['output']['text'][1]

            # ==================================================
            #   Update context
            # ==================================================
            self.context.update(dict_response['context'])

            # ==================================================
            #   Check conversation is end or durable
            # ==================================================
            if 'branch_exited' in dict_response['context']['system']:
                conv_flag = True
            else:
                conv_flag = False

        except Exception as e:
            # self.logger.write_critical(e)
            result_conv =  "다시 한번 말씀해주세요."

        return result_conv