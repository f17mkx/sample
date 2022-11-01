#!/usr/bin/env python
import os
import traceback
import openai
import json
from datetime import datetime

from openai import InvalidRequestError

param_names = [
    'max_tokens', 'n', 'temperature',
    'top_p', 'frequency_penalty', 'presence_penalty',
    'stop', 'start_sequence', 'restart_sequence']


def get_param_profiles():
    file = open('config/profiles.json', 'r')
    param_profiles = json.load(file)
    file.close()
    return param_profiles


class Profil:
    def __init__(self, name=None):
        self.prompt = ''
        self.kind = 'completion'
        self.engine = 'text-davinci-002'
        self.max_tokens = 150
        self.n = 1
        self.temperature = 0.7
        self.top_p = 1.0
        self.frequency_penalty = 1.0
        self.presence_penalty = 1.0
        self.stop = []
        self.start_sequence = []
        self.restart_sequence = []

        self.good_runs = []

        if isinstance(name, str):
            self.name = name
        else:
            # create instance from existing class object
            if isinstance(name, Profil):
                self.__dict__ = name.__dict__
            # use assigned variable name for name of instance
            def_name = traceback.extract_stack()[-2][3]
            self.name = def_name[:def_name.find('=')].strip()

        self.requests = []

        self.profil_dir = 'profiles' + '/' + str(self.name)
        self.self_files = 'profiles' + '/' + str(self.name) + '/' + str(self.name)

        try:
            os.makedirs(self.profil_dir)
            self.save()
        except OSError:
            self.load()

        if not self.requests:
            self.requests.append({
                'info': {'id': 0},
                'params': None,
                'prompt': None,
                'response': None})

    def get_path(self, path):
        if path:
            return path
        return self.self_files

    def get_path_form_time(self, time, good=False):
        if good:
            out_path = self.profil_dir \
                       + '/good'
        else:
            out_path = self.profil_dir \
                       + '/out/' \
                       + time.strftime("%y/%m/%d")
        try:
            os.makedirs(out_path)
        finally:
            return out_path \
                   + '/' \
                   + time.strftime("%y-%m-%d_%H-%M-%S") \
                   + '_' \
                   + self.name

    def save(self):
        self.save_prompt()
        self.save_params()
        self.save_requests()

    def load(self):
        self.load_prompt()
        self.load_params()
        self.load_requests()

    def save_params(self, path=None):
        file = open(self.get_path(path) + '_params.json', 'w')
        json.dump(self.get_params_dict(), file, indent=1)
        file.close()

    def load_params(self):
        file = open(self.self_files + '_params.json', 'r')
        self.update_params(json.loads(file.read()))
        file.close()

    def save_prompt(self, path=None):
        file = open(self.get_path(path) + '_prompt', 'w')
        file.write(self.prompt)
        file.close()

    def save_request(self, path=None):
        file = open(self.get_path(path) + '_request.json', 'w')
        json.dump(self.requests[-1], file, indent=2)
        file.close()

    def load_prompt(self):
        file = open(self.self_files + '_prompt', 'r')
        self.prompt = file.read()
        file.close()

    def save_requests(self, path=None):
        file = open(self.get_path(path) + '_requests.json', 'w')
        json.dump(self.requests, file, indent=2)
        file.close()

    def load_requests(self):
        file = open(self.self_files + '_requests.json', 'r')
        self.requests = json.load(file)
        file.close()

    def save_good_requests(self, path=None):
        file = open(self.get_path(path) + '_requests_good.json', 'w')
        json.dump(self.good_runs, file, indent=2)
        file.close()

    def load_good_requests(self):
        file = open(self.self_files + '_requests_good.json', 'r')
        self.good_runs = json.load(file)
        file.close()

    def save_good_run(self):
        out_file_path = self.get_path_form_time(
            datetime.now(), good=True)
        self.save_request(out_file_path)
        self.good_runs.append(self.requests[-1])
        self.save_good_requests()

    def get_params_dict(self):
        return {param: self.__dict__[param]
                for param in param_names}

    def params_dict__for__param_names(self):
        return {param: self.__dict__[param]
                for param in param_names
                if not self.__dict__[param] == []}

    def update_params(self, param_updates):
        self.__dict__.update(param_updates)
        self.get_params_dict()
        self.save_params()

    def append_request_file(self, time_received, response_text):
        file = open(self.self_files + '_requests', 'a')
        file.write(
            '\n-------------------------------------\n' +
            time_received.strftime("%y/%m/%d %H:%M:%S") +
            '\n-------------------------------------\n' +
            self.prompt +
            '\n-------------------------------------\n' +
            response_text
        )
        file.close()

    def append_request_list(self, response, time_send, time_received):
        times = {'iso': time_received.strftime("%y/%m/%d %H:%M:%S"),
                 'send': int(datetime.timestamp(time_send)),
                 'created': response.created,
                 'received': int(datetime.timestamp(time_received)),
                 'response_ms_server': response.response_ms,
                 'response_ms_local': int(datetime.timestamp(
                     time_received) - datetime.timestamp(time_send))}

        info = {'id': self.requests[-1]['info']['id'] + 1,
                'times': times,
                'finish_reason': response.get("choices")[0].finish_reason,
                'usage': dict(
                    response.get("usage")),
                'msg_id': response.id,
                'openai_id': response.openai_id} #,
                # 'openai_id_choices': response.get("choices").openai_id,
                # 'openai_id_usage': response.get("usage").openai_id}

        request = {'info': info,
                   'params': self.params_dict__for__param_names(),
                   'prompt': self.prompt,
                   'response': response.get("choices")[0]['text']}

        self.requests.append(request)
        return request

    def save_response(self, response, time_send, time_received):

        response_text = response.get("choices")[0]['text']
        self.append_request_file(time_received, response_text)
        request = self.append_request_list(response, time_send, time_received)
        self.save_requests()
        out_file_path = self.get_path_form_time(time_received)
        self.prompt = self.prompt + response_text
        self.save_prompt()
        self.save_prompt(out_file_path)
        self.save_params(out_file_path)
        self.save_request(out_file_path)
        # return response_text
        # return response
        return response, request

    def generate_response(self):

        previous_request = self.requests[-1]

        previous_prompt = previous_request['prompt']
        previous_params = previous_request['params']

        current_params = self.params_dict__for__param_names()

        self.load_prompt()
        self.load_params()

        if self.prompt == previous_prompt and current_params == previous_params:
            return

        time_send = datetime.now()
        # if 'start_sequence' in params.keys():
        #     start_sequence = self.start_sequence
        # if 'restart_sequence' in params.keys():
        #     restart_sequence = self.restart_sequence
        try:
            if self.stop:
                response = openai.Completion.create(
                    engine=self.engine,
                    prompt=self.prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty,
                    stop=self.stop
                )
            else:
                response = openai.Completion.create(
                    engine=self.engine,
                    prompt=self.prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    frequency_penalty=self.frequency_penalty,
                    presence_penalty=self.presence_penalty
                )
        except InvalidRequestError as ERROR:
            print(ERROR)
            return ERROR

        time_received = datetime.now()
        return self.save_response(response, time_send, time_received)

    def __str__(self):
        return 'Hello, my name is' + self.name


class Robert:
    def __init__(self):
        self.profiles = {}
        try:
            os.makedirs('config')
            self.generate_profile('default')

        except OSError:
            for name in get_param_profiles().keys():
                self.generate_profile(name)

        self.load_config_save_to_profiles()
        # self.load_profiles_save_to_config()

    def generate_profile(self, profil_name):
        self.profiles.update(
            {profil_name: Profil(profil_name)})

    def load_config_save_to_profiles(self):
        for name, params in get_param_profiles().items():
            self.profiles[name].update_params(params)

    def load_profiles_save_to_config(self):
        # for name in get_param_profiles().keys():
        #     self.profiles[name].get_params_dict()

        param_profiles = {
            name: profil.get_params_dict()
            for name, profil in self.profiles.items()
        }
        param_profiles_sorted = dict(
            sorted(param_profiles.items(), key=lambda x: x)
        )
        file = open('config/profiles.json', 'w')
        json.dump(param_profiles_sorted, file, indent=2)
        file.close()

    def generate_response(self):

        # for name in get_param_profiles().keys():
        #     # self.profiles[name].generate_response()
        #     return self.profiles[name].generate_response()

        response = [self.profiles[name].generate_response() for name in get_param_profiles().keys()]
        self.save_params()
        return response

    def __str__(self):
        return '''Hallo,
    ich bin Robert, Ihnen zu dienen regle ich 
    die Verwaltung deiner Anfragen.
        
    FUNCTIONS:
        load()
            Steht's zu Ihren Diensten.

        save()
            reverse load()
            
        generate_profiles( profile_names )
            generates Profile class object 
            per profile_name
            
        load_prompts( name2file )
            receives zip( profile_names, prompt_dirs )
            to manually load prompt files.
            Can be used to initiate Robert's Profiles 
            from exsisting Prompts.
            
        update_params()
            pushes manual param updates in 
            config/profiles.json to their
            corresponding Profiles.
                
        save_params()
            saves param updates within Profiles to 
            config/profiles.json for manual review.
            
        generate_response()
            triggers all Profiles to generate a response
            if their parameters have been altered.
        '''


if __name__ == "__main__":
    Robert = Robert()
    print("done")
