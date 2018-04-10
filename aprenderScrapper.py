import os
import re
from bs4 import BeautifulSoup
import requests
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#urllib3.disable_warnings() # desabilita verificação de certificados.
"""
Criado por Wagner Alberto 04/2018

 """
file = open('credenciais.json')
credenciais = json.load(file)
URL_APRENDER = "https://aprender.unb.br/"

class Aprender():
    
    
    url = URL_APRENDER
    _logado = False
    nome = None
    links_cursos = None

    def __init__(self):
        self.session = requests.Session()
        self._form_url = None 

    def login(self, cpf, senha):
        self.cpf = cpf
        self.senha = senha
 
        if self.is_online is False:
            raise SystemError('Aprender Offline') 
        #HOME        
        r = self.session.get(self.url,verify=False, allow_redirects=False) 
        
        #pega informação de headers.
        url_login_php = "https://aprender.ead.unb.br/login/index.php" 
        
        data = {"username": self.cpf,
                "password" : self.senha}

        r = self.session.post(url_login_php, data = data, verify=False)
       
        try: 
            res = BeautifulSoup(r.text,"lxml").find("div",{"class":"logininfo"})
            self.nome = (res.text.split("como")[1].split("(")[0].strip())
        except:  
            print("Não foi possível fazer o login, verifique usuário e senha.")
        self._logado = True 
        self.html = r.content 
        return True

    def busca_cursos(self):
        if(not self._logado):
            print("você deve estar logado para acessar") 
            return

        url_home_cursos = "https://aprender.ead.unb.br/"
        
        
        r = self.session.get(url_home_cursos,verify=False, allow_redirects=False) 
        #print(r.text)
        soup = BeautifulSoup(r.text, "lxml").find_all("a")
        result = []
        for elem in soup:
            elem = str(elem)
            if "course" in elem and "view" in elem and not "user" in elem:
                link = elem.split('href="')[1].split('"')[0]
                if ("moodle2013") not in link:
                    result.append(link)
        self.links_cursos = list(result)
        return True

    def acessa_disciplina(self,link):
        
        r = self.session.get(link,verify=False, allow_redirects=False)
        soup = BeautifulSoup(r.text)
        try:
            titulo  = str(soup.title).split('Curso: ')[1].split('<')[0]
        except:
            return
        print('Baixando a disciplina:',titulo)
        directory = os.path.dirname(os.path.abspath(__file__))
        directory = os.path.join(directory, titulo)

        for elem in soup.find_all('a'):

            if not os.path.exists(directory):
                os.makedirs(directory)
            if('resource') in  elem['href']:
                #print(elem['href'],elem.get_text())
                print('Baixando o arquivo : ', elem.get_text())
                try:
                    arq = open(os.path.join(directory,elem.get_text()),"wb")
                    r = self.session.get(elem['href'])
                    arq.write(r.content)
                    arq.close()
                except Exception as e:
                    print(e)
                    continue
        return

    @property
    def is_online(self):
        r = requests.get(self.url, verify=False, allow_redirects=False) 
        if (r.status_code == 200):
            return True 
        return False

if __name__ == '__main__':
    
    obj = Aprender()
    obj.login(credenciais['cpf'],credenciais['senha']) 

    obj.busca_cursos()
#    print(obj.links_cursos[0])
    for elem in obj.links_cursos:
        obj.acessa_disciplina(elem)
    #obj.acessa_disciplina(obj.links_cursos[0])
#   print(obj.links_cursos)

