from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

import pandas as pd

app = Flask(__name__)
CORS(app)

class Similarity_Books:    
    gender_mapping = {
        1: 'Ação',
        2: 'Autoajuda',
        3: 'Comédia',
        4: 'Culinária',
        5: 'Estudos',
        6: 'Finanças',
        7: 'Infantil',
        8: 'Mistério',
        9: 'Psicologia',
        10: 'Religião',
        11: 'Romance',
        12: 'Suspense',
        13: 'Técnico',
        14: 'Terror',
        15: 'Aventura'
    }

    Rate_mapping_Calc = {
        2:  10,
        3:  12,
        4:  14,
        5:  16,
        6:  18
    }
    Rate_mapping = {
        1: 'Livre',
        2:  10,
        3:  12,
        4:  14,
        5:  16,
        6:  18
    }

    filterBy = {
        1: 'Genero',
        2: 'Classificação Indicativa',
        3: 'Paginas',
        4: 'Autor',
        5: 'Título'
    }

    Books_Num = 5

    BooksExcel = pd.read_excel('D:\Similaridade_Model\Similaridade.xlsx')
    books      = BooksExcel.to_dict(orient='records')
    
    def getSimilarsGenders(_gender: int) -> str:
        Filtered_Similars = ""
        if _gender == 1: #ação
            Filtered_Similars = '1,12,15'
        if _gender == 12 or _gender == 14:  # Suspense, Terror
            Filtered_Similars = '12,14' if _gender == 12 else \
                                '14,12'
        elif _gender == 3 or _gender == 11:  # Comédia, Romance
            Filtered_Similars = '3,11' if _gender == 3 else '11,3'
        elif _gender == 2 or _gender == 9:  # Autoajuda, Psicologia
            Filtered_Similars = '2,9' if _gender == 2 else '9,2'
        elif _gender == 4 or _gender == 5:  # Culinária, Estudos
            Filtered_Similars = '4,5' if _gender == 4 else '5,4'
        elif _gender == 6:  # Finanças / estudos
            Filtered_Similars = '6,5'
        elif _gender == 7:  # Infantil
            Filtered_Similars = '7'
        elif _gender == 8:  # Mistério
            Filtered_Similars = '8,12'
        elif _gender == 10:  # Religião
            Filtered_Similars = '10,13'
        elif _gender == 13:  # Técnico
            Filtered_Similars = '13,9,10,4,6'
        elif _gender == 15: #Aventura
            Filtered_Similars = '15,1,11'
        return Filtered_Similars
        
    def mostSimilar(selectedBook: list,_Select_Filter: int,_select_age: int,_Pages: int) -> list:
        filterSelection = []
        bestSelection   = []
        for i in range(len(selectedBook)):
            _refbook = selectedBook[i]      
            _refbook_Genderidx  = _refbook['Genero']
            if any(_IDX in Similarity_Books.gender_mapping[_Select_Filter] for _IDX in _refbook_Genderidx)  \
            and _refbook['Classificação Indicativa'] == Similarity_Books.Rate_mapping[_select_age]:
                filterSelection.append({'Index': i,'Paginas': _refbook['Paginas']})
                if len(bestSelection) == 0:
                    bestSelection.append(_refbook)
        if len(bestSelection) != 0 and len(filterSelection) > 1: #Considera as paginas mais proximas
            best_selection_diff = abs(bestSelection[0]['Paginas'] - _Pages)  
            for i in range(len(filterSelection)):
                _refbook = selectedBook[filterSelection[i]['Index']]
                diff = abs(_refbook['Paginas'] - _Pages)
                if diff < best_selection_diff:
                    bestSelection[0]    = _refbook
                    best_selection_diff = diff
        return bestSelection
        
    def searchSimilarBook(_Select_Filter: int,_select_age: int,_Pages: int, _GenderFiltered: str = ''):
        ByFilter        = True
        bestSelection   = []
        selectedBook    = []
        Genderidx       = [int(num) for num in _GenderFiltered.split(',')]
        for _refbook in Similarity_Books.books: #Primeira busca com todos os livros              
            _refbook_Genderidx  = _refbook['Genero']
            _Gender_List        = [Similarity_Books.gender_mapping[(idx)] for idx in Genderidx]
            if  any(letter in _refbook_Genderidx for letter in _Gender_List)     \
            and _refbook['Classificação Indicativa'] == Similarity_Books.Rate_mapping[_select_age]\
            and _refbook['Paginas']                  >= _Pages:            
                if len(bestSelection) != 0 and int(_refbook['Paginas']) < int(bestSelection[0]['Paginas']):
                    del bestSelection[0]
                    bestSelection.append(_refbook)
                elif len(bestSelection) == 0:
                    bestSelection.append(_refbook)        
                    
            if _refbook['Classificação Indicativa'] != 'livre' and \
                _refbook['Classificação Indicativa'] != 'Livre' and _select_age != 1:
                if  any(letter in _refbook_Genderidx for letter in _Gender_List)                      \
                and int(_refbook['Classificação Indicativa']) <= int(Similarity_Books.Rate_mapping_Calc[_select_age]):
                    selectedBook.append(_refbook)        
            else:
                if  any(letter in _refbook_Genderidx for letter in _Gender_List):            
                    selectedBook.append(_refbook)
                    
        if(len(bestSelection) == 0):
            ByFilter = False
        while(len(bestSelection) == 0):
            for Gender in Genderidx:
                bestSelection = Similarity_Books.mostSimilar(selectedBook,Gender,_select_age,_Pages) #Busca com base nos selecionados
                if(len(bestSelection) != 0):
                    break;
            if(len(bestSelection) == 0):
                if(_select_age == 1):
                    break;
                else:
                    _select_age = _select_age - 1
                    
        if(len(bestSelection) != 0):
            IDX = selectedBook.index(bestSelection[0])
            del selectedBook[IDX]
        if len(bestSelection) != 0 and ByFilter == True:
            print(f'\n{"="*30} Melhor livro localizado: {"="*30}\n{bestSelection[0]}\n')
        elif len(bestSelection) != 0 and ByFilter == False:
            print(f'\n{"="*30} melhor Sugestão: {"="*30}\n{bestSelection[0]}\n')
        else:
            print('\nNão foi possivel localizar um livro especifico com seus filtros, mas aqui esta alguns semelhantes:\n')
        ref = (Similarity_Books.Books_Num if len(selectedBook) > Similarity_Books.Books_Num else len(selectedBook))
        for i in range(ref):
            print(f'{"="*30} Considere essas outras opções: {"="*30}\n\n' if i == 0 else "", selectedBook[i], sep="")

    def makeConsult(_type: int, _info: str):
        Selections = []
        if(_type == 1):
            if(len(_info) == 1): # busca similares em caso de ser digitado somente um genero
                _info = Similarity_Books.getSimilarsGenders(int(_info))
            gender_Idx   = [int(num) for num in _info.split(',')]
            Gender_List = [Similarity_Books.gender_mapping[(idx)] for idx in gender_Idx]
            
        for _refbook in Similarity_Books.books: #Primeira busca com todos os livros 
            AppendBook          = False        
            if(_type == 1):
                _refbook_Genderidx  = _refbook['Genero']
                AppendBook  = True if any(letter in _refbook_Genderidx for letter in Gender_List) else False
            elif(_type == 2):
                AppendBook  =  True if (_refbook['Classificação Indicativa'] == Similarity_Books.Rate_mapping[_info]) else False
            elif(_type == 3):
                AppendBook  =  True if (_refbook['Paginas'] >= _info) else False
            elif(_type == 4):
                RefbookInfo = str(_refbook['Autor']).lower()
                _info       = _info.lower()                    
                AppendBook  =  True if (_info in RefbookInfo) else False 
            elif(_type == 5):
                RefbookInfo = str(_refbook['Titulo']).lower()
                _info       = _info.lower()
                AppendBook  =  True if (_info in RefbookInfo) else False
                
            if(AppendBook == True):
                Selections.append(_refbook)

        if(_type == 3):
            Selections = sorted([_book for _book in Selections if _book['Paginas'] >= _info], key=lambda x: x['Paginas'])
                
        ref = (Similarity_Books.Books_Num if len(Selections) > Similarity_Books.Books_Num else len(Selections))
        if len(Selections) != 0:
            for i in range(ref):
                print(f'{"="*30} opções Localizadas: {"="*30}\n' if i == 0 else "", Selections[i], sep="")
        else:
            print('não foi possivel localizar nenhum livro')

    def MakeMistConsult(MistInfo: dict):
        Selections = []

        if 1 in MistInfo:
            _info = MistInfo[1]
            if len(_info) == 1:  # Se só um gênero foi digitado, buscar similares
                _info = Similarity_Books.getSimilarsGenders(int(_info))
            gender_Idx = [int(num) for num in _info.split(',')]
            Gender_List = [Similarity_Books.gender_mapping[idx] for idx in gender_Idx]

        for _refbook in Similarity_Books.books:         
            valid = True
            
            if 1 in MistInfo:  # Gênero
                _refbook_Genderidx = _refbook['Genero']
                if not any(gender in _refbook_Genderidx for gender in Gender_List):
                    valid = False

            if 2 in MistInfo:  # Classificação indicativa
                if _refbook['Classificação Indicativa'] != Similarity_Books.Rate_mapping[MistInfo[2]]:
                    valid = False

            if 3 in MistInfo:  # Número de páginas (mínimo)
                if _refbook['Paginas'] < MistInfo[3]:
                    valid = False

            if 4 in MistInfo:  # Autor
                RefbookInfo = str(_refbook['Autor']).lower()
                _info = str(MistInfo[4]).lower()
                if _info not in RefbookInfo:
                    valid = False

            if 5 in MistInfo:  # Título
                RefbookInfo = str(_refbook['Titulo']).lower()
                _info = str(MistInfo[5]).lower()
                if _info not in RefbookInfo:
                    valid = False

            # Se o livro passou em TODOS os critérios fornecidos, ele entra na lista
            if valid:  
                Selections.append(_refbook)

        if 3 in MistInfo:
            Selections = sorted(Selections, key=lambda x: x['Paginas'])

        ref = min(len(Selections), Similarity_Books.Books_Num)
        if Selections:
            for i in range(ref):
                print(f'{"="*30} Opções Localizadas: {"="*30}\n' if i == 0 else "", Selections[i], sep="")
        else:
            print('Não foi possível localizar nenhum livro.')

    def GetRateSelection() -> int:
        choices = [1,2,3,4,5,6]
        Age_Input = input(
            "Qual classificação Indicativa?\n"
            "[1]LIVRE\n"
            "[2]10 ANOS\n"
            "[3]12 ANOS\n"
            "[4]14 ANOS\n"
            "[5]16 ANOS\n"
            "[6]18 ANOS\n"
            )
        try:
            Age_Input_int = int(Age_Input)   
            if not(Age_Input_int in choices):
                print('Dados informados de Forma incorreta, Reiniciando....')
                Similarity_Books.GetRateSelection()    
            return Age_Input_int    
        except ValueError:
            print('Dados informados de Forma incorreta, Reiniciando....')
            Similarity_Books.GetRateSelection()
            
    def init():
        Age_Input   = Similarity_Books.GetRateSelection()  
        Gender_Input = Similarity_Books.GetGenderSelection()
        Pages_Input  = input(
            "Quantas paginas deseja?"
            "\nNumero de Paginas: "
            )
        try:                        
            GenderFilter = Similarity_Books.getSimilarsGenders(Gender_Input)
            pagesNum     = int(Pages_Input)
            Similarity_Books.searchSimilarBook(Gender_Input,Age_Input,pagesNum,GenderFilter)
        except ValueError:
            print('Dados informados de Forma incorreta, Reiniciando....')
            Similarity_Books.init()
            
    def FilterType():
        FilterInfo      = ''
        _SpecificGender = 0
        GendersNum      = 0
        FilterType = input('Que Filtragem Deseja?\n'
                        '[1]Basica(Genero,Idade,Paginas)\n'
                        '[2]Especifica\n'
                        '[3]Mista\n'
                        )
        try:
            FilterType_Int = int(FilterType)
            if(FilterType_Int != 1 and FilterType_Int != 2 and FilterType_Int != 3):
                print('Dado Não Reconhecido, Tente Novamente')
                FilterType()
            elif(FilterType_Int == 1):
                Similarity_Books.init()
            elif(FilterType_Int == 2):
                while True:
                    SpecificType_Int = int(input("\nDeseja Consultar por:"
                                                "\n[1]Genero"
                                                "\n[2]Classificação Indicativa"
                                                "\n[3]Numero de Paginas"
                                                "\n[4]Autor"
                                                "\n[5]Nome do Livro\n"
                                                ))
                    if(SpecificType_Int >= 1 and SpecificType_Int <= 5):
                        break;
                    else:
                        print("Dados Não reconhecidos...")
                if(SpecificType_Int == 1):
                    while _SpecificGender != 1 and _SpecificGender != 2:
                        _SpecificGender = int(input("Deseja + de um genero especifico?\n[1]SIM\n[2]NÃO\n"))
                    if(_SpecificGender == 1):
                        GendersNum = int(input("Quantos Generos deseja?"))
                    i = GendersNum if GendersNum != 0 else 1
                    while i > 0:                    
                        selectedGender = Similarity_Books.GetGenderSelection()
                        if not(str(selectedGender) in FilterInfo):
                            i = i - 1
                            FilterInfo     = FilterInfo + str(selectedGender) +(',' if i > 0 else "")
                        else:
                            print(f'Genero de {Similarity_Books.gender_mapping[selectedGender]} ja Selecionado')
                if(SpecificType_Int == 2):
                    FilterInfo = Similarity_Books.GetRateSelection()
                if(SpecificType_Int == 3):
                    FilterInfo  = int(input("Quantas paginas deseja?"
                                        "\nNumero de Paginas: "
                                    ))
                if(SpecificType_Int == 4):
                    FilterInfo = input("Digite o Autor Desejado: \n")
                if(SpecificType_Int == 5):
                    FilterInfo = input("Digite o livro Desejado: \n")

                Similarity_Books.makeConsult(SpecificType_Int,FilterInfo)
            elif(FilterType_Int == 3):
                MistInfo = {}            
                alreadySet = []
                while True:                
                    SpecificType_Int = int(input("\nDeseja Consultar por:"
                                                "\n[1]Genero"
                                                "\n[2]Classificação Indicativa"
                                                "\n[3]Numero de Paginas"
                                                "\n[4]Autor"
                                                "\n[5]Nome do Livro"
                                                "\n[6]Finalizar\n"
                                                ))
                    if(len(alreadySet) != 0):
                        if(SpecificType_Int in alreadySet):
                            print("consulta ja atribuida, Seleciona uma diferente ou Finalize")
                            continue
                    if(SpecificType_Int == 1):
                        while _SpecificGender != 1 and _SpecificGender != 2:
                            _SpecificGender = int(input("Deseja + de um genero especifico?\n[1]SIM\n[2]NÃO\n"))
                        if(_SpecificGender == 1):
                            GendersNum = int(input("Quantos Generos deseja?"))
                        i = GendersNum if GendersNum != 0 else 1
                        while i > 0:                    
                            selectedGender = Similarity_Books.GetGenderSelection()
                            if not(str(selectedGender) in FilterInfo):
                                i = i - 1
                                FilterInfo     = FilterInfo + str(selectedGender) +(',' if i > 0 else "")
                            else:
                                print(f'Genero de {Similarity_Books.gender_mapping[selectedGender]} ja Selecionado')
                    elif(SpecificType_Int == 2):
                        FilterInfo = Similarity_Books.GetRateSelection()
                    elif(SpecificType_Int == 3):
                        FilterInfo  = int(input("Quantas paginas deseja?"
                                            "\nNumero de Paginas: "))
                    elif(SpecificType_Int == 4):
                        FilterInfo = input("Digite o Autor Desejado: \n")
                    elif(SpecificType_Int == 5):
                        FilterInfo = input("Digite o livro Desejado: \n")
                    elif(SpecificType_Int == 6):                        
                        break
                    
                    alreadySet.append(SpecificType_Int)
                    MistInfo[SpecificType_Int] = (FilterInfo)
                Similarity_Books.MakeMistConsult(MistInfo)
        except ValueError:
            print('Dado Não Reconhecido, Tente Novamente')
            FilterType()    
    @staticmethod
    def get_key(genre_name: str) -> int:        
        genre_name = genre_name.lower()
        _key = 0
                
        gender_key = {v.lower(): k for k, v in Similarity_Books.gender_mapping.items()}
                
        for key,value in gender_key.items():
            if(key == genre_name):  
                _key = value         
        
        return _key

@app.route('/get_gender_key', methods=['POST'])
def get_gender_key():
    data       = request.json
    genre_name = data.get('genre') 

    if not genre_name:
        return jsonify({"error": "No genre provided"}), 400

    key = Similarity_Books.get_key(genre_name[0])    
    
    if key is None:
        return jsonify({"error": "Genre not found"}), 404
    
    SimilarGender = Similarity_Books.getSimilarsGenders(key)
    SimilarGender = [int(num) for  num in SimilarGender.split(',')]
    Gender_List = [Similarity_Books.gender_mapping[idx] for idx in SimilarGender]    

    return jsonify({"key": Gender_List})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)