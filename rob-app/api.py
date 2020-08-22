#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 22:03:40 2020

@author: qwang
"""

from flask import Flask, request
from flask_restful import Resource, Api
import os

import sys
import re
import json
from pred import pred_prob, pred_prob_bert, extract_sents



             
             
             
#%%
PROB_PATH = {
    'arg-r': 'pth/awr_13.json',
    'pth-r': 'pth/awr_13.pth.tar',
    'fld-r': 'fld/awr_13.Field',
    
    'arg-b': 'pth/awb_32.json',
    'pth-b': 'pth/awb_32.pth.tar',
    'fld-b': 'fld/awb_32.Field',
    
    'arg-i': 'pth/cwi_6.json',
    'pth-i': 'pth/cwi_6.pth.tar',
    'fld-i': 'fld/cwi_6.Field',
    
    'arg-w': 'pth/bert_w0.json',
    'pth-w': 'pth/biobert/bert_w0.pth.tar',
    'wgt-w': 'pth/biobert',
    
    'arg-e': 'pth/awe_8.json',
    'pth-e': 'pth/awe_8.pth.tar',
    'fld-e': 'fld/awe_8.Field',
}

SENT_PATH = {
    'arg-r': 'pth/hr_4.json',
    'pth-r': 'pth/hr_4.pth.tar',
    'fld-r': 'fld/hr_4.Field',
    
    'arg-b': 'pth/hb_5.json',
    'pth-b': 'pth/hb_5.pth.tar',
    'fld-b': 'fld/hb_5.Field',
    
    'arg-i': 'pth/hi_4.json',
    'pth-i': 'pth/hi_4.pth.tar',
    'fld-i': 'fld/hi_4.Field',
    
    'arg-w': 'pth/hw_17.json',
    'pth-w': 'pth/hw_17.pth.tar',
    'fld-w': 'fld/hw_17.Field',
    
    'arg-e': 'pth/he_26.json',
    'pth-e': 'pth/he_26.pth.tar',
    'fld-e': 'fld/he_26.Field'
}


class PreRob():
    def __init__(self, prob_path, sent_path, txt_info):      
    
        for key, value in prob_path.items():
            prob_path[key] = os.path.join(os.getcwd(), value)
        self.prob_path = prob_path
        self.sent_path = sent_path
        self.txt_info = txt_info
        self.txt_paths = []
        
    def get_txt_path(self):       
        txt_info = self.txt_info
        txt_paths = self.txt_paths
        
        # If 'txt_info' is a folder
        if os.path.isdir(txt_info) == True:
            # txt_info = os.path.join(os.getcwd(), txt_info)      
            for root, _, files in os.walk(txt_info):            
                for f in files:
                    if f.endswith(".txt"):
                        txt_paths.append(os.path.join(root, f))
               
        # if 'txt_info' is a single txt path
        if os.path.exists(txt_info) == True and txt_info.endswith(".txt") == True:
            txt_paths.append(txt_info)
        
        # if 'txt_info' is a string containing multiple txt paths       
        if len(txt_info.split(".txt,")) > 1:
            paths = txt_info.split(".txt,")
            for p in paths[:-1]:
                txt_paths.append(p+'.txt')
            txt_paths.append(paths[-1])   
            
        self.txt_paths = txt_paths
    
    
    def process_text(self, text):       
        text = re.sub(r"^(?:[\t ]*(?:\r?\n|\r))+", " ", text, flags=re.MULTILINE)  # Remove emtpy lines        
        text = text.encode("ascii", errors="ignore").decode()  # Remove non-ascii characters         
        text = re.sub(r'\s+', " ", text)  # Strip whitespaces     
        text = re.sub(r'^[\s]', "", text)  # Remove the whitespace at start and end of line
        text = re.sub(r'[\s]$', "", text)
        return text 
          
    def pred_probs(self, num_sents=0): 
        if self.txt_paths == []:
            output = {"message": "Folder/TXTs not found"}  # folder doesn't exist or no txt files found in the folder
            
        else:          
            output = []
            Id = 0
            for path in self.txt_paths:
                try:
                    if os.path.isabs(path) == False:
                        path = os.path.join(os.getcwd(), path)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fin:
                        text = fin.read()           
                    text = self.process_text(text)   
                                
                    pr = pred_prob(self.prob_path['arg-r'], self.prob_path['fld-r'], self.prob_path['pth-r'], text).astype(float)
                    pb = pred_prob(self.prob_path['arg-b'], self.prob_path['fld-b'], self.prob_path['pth-b'], text).astype(float)
                    pi = pred_prob(self.prob_path['arg-i'], self.prob_path['fld-i'], self.prob_path['pth-i'], text).astype(float)
                    pw = pred_prob_bert(self.prob_path['arg-w'], self.prob_path['wgt-w'], self.prob_path['pth-w'], text).astype(float)
                    pe = pred_prob(self.prob_path['arg-e'], self.prob_path['fld-e'], self.prob_path['pth-e'], text).astype(float)  
                    
                    score = {"txt_id": Id, "txt_path": path,
                			 "random": pr,
                			 "blind": pb,
                			 "interest": pi,
                			 "welfare": pw,
                			 "exclusion": pe}
                    
                    if num_sents > 0:
                        sr = extract_sents(self.sent_path['arg-r'], self.sent_path['fld-r'], self.sent_path['pth-r'], text, num_sents)
                        sb = extract_sents(self.sent_path['arg-b'], self.sent_path['fld-b'], self.sent_path['pth-b'], text, num_sents)
                        si = extract_sents(self.sent_path['arg-i'], self.sent_path['fld-i'], self.sent_path['pth-i'], text, num_sents)
                        sw = extract_sents(self.sent_path['arg-w'], self.sent_path['fld-w'], self.sent_path['pth-w'], text, num_sents)
                        se = extract_sents(self.sent_path['arg-e'], self.sent_path['fld-e'], self.sent_path['pth-e'], text, num_sents)
                        score['sentences'] = {"random": sr, "blind": sb, "interest": si, "welfare": sw, "exclusion": se}             
                    
                except: 
                    score = {"txt_id": Id, "txt_path": path, "message": "Path not found"}                    
                Id = Id + 1
                output.append(score)
        return output


#%%
app = Flask(__name__)
api = Api(app)

class ROB(Resource):
    def get(self):
        return {}

    def put(self):
        txt_info = request.form['data'] 
         
        rober = PreRob(PROB_PATH, SENT_PATH, txt_info)
        rober.get_txt_path()
        
        if (len(request.form)) == 1:
            output = rober.pred_probs()
    
        if (len(request.form)) == 2:
            try:
                json_path = request.form['out']
                output = rober.pred_probs()
                if os.path.dirname(json_path):  # if output dir exists
                    with open(request.form['out'], 'w') as fp:
                        json.dump(output, fp)
            except:
                num_sents = int(request.form['sent'])
                output = rober.pred_probs(num_sents)  
        
        if (len(request.form)) == 3:
            json_path = request.form['out']
            num_sents = request.form['sent'] 
            output = rober.pred_probs(num_sents)  
            if os.path.dirname(json_path):  # if output dir exists
                with open(request.form['out'], 'w') as fp:
                    json.dump(output, fp)          
                
        return output

api.add_resource(ROB, '/')
# api.add_resource(ROB, '/<string:task_id>')

if __name__ == '__main__':
    # app.run(debug=False)
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
