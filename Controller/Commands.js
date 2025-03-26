//variaveis
let loadingInterval;
let makingConsult = false;

//Varaiveis Principais
let selectedGenres;
let RateSelection;
let SelectedAuthor;
let SelectedTitle;
let PagesNum;
let SimilarsCount;
let _Info
let Books

//Eventos
document.getElementById("Clear").addEventListener("click", function() {
    ClearAll();
});

document.getElementById("Consult").addEventListener("click", function() {
    makeConsult();
});

//Funções API
async function getGenderKey(genre) {
    try {
        const response = await fetch("http://127.0.0.1:5000/get_gender_key", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ genre })
        });

        const data = await response.json();        
        return data.key

    } catch (error) {
        console.error("Erro ao chamar o servidor:", error.message);
    }
}

async function GetBooks(_Info) {    
    try {
        const response = await fetch("http://127.0.0.1:5000/get_Books", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ _Info })
        });

        const data = await response.json();            
        return data

    } catch (error) {
        console.error("Erro ao chamar o servidor:", error.message);
    }
}

async function GetGenders() {           
    let checkedGenres = document.querySelectorAll(".container_genero input[type='checkbox']:checked");
    
    selectedGenres = Array.from(checkedGenres).map(checkbox => 
        checkbox.previousElementSibling.textContent.trim());
    
    if (selectedGenres.length == 1)
        selectedGenres = await getGenderKey(selectedGenres); 
}

//Funções
function ClearAll(){
    document.getElementById("Selections_Forms").reset();
    document.getElementById("Books_Bar").style.display = "none";    
    document.getElementById("Books_border").style.display = "none";
    makingConsult = false;    
}

function GetMainVars(){
    const bookData = {};

    //Valores Padrão sempre que Iniciar //RESET
    selectedGenres  = "";
    RateSelection   = "0";
    PagesNum        = 0;
    SelectedAuthor  = "";
    SelectedTitle   = "";
    SimilarsCount   = "5";

    //Coleta os Valores informados
    GetGenders();
    RateSelection  = document.getElementById('Rate_Selection').value //Idade Informada
    PagesNum       = document.getElementById('Pages_IPT').value //Paginas    
    SelectedAuthor = document.getElementById('Author_IPT').value // Autor    
    SelectedTitle  = document.getElementById('Title_IPT').value // Titulo    
    SimilarsCount  = document.getElementById('SimilarNum_IPT').value //Contagem de Similares    

    //Atribui os Valores de Forma selecionada
    if (selectedGenres.length > 0) bookData[1] = selectedGenres;
    if (RateSelection  != "0")     bookData[2] = RateSelection;
    if (PagesNum       != 0)       bookData[3] = PagesNum;
    if (SelectedAuthor != "")      bookData[4] = SelectedAuthor;
    if (SelectedTitle  != "")      bookData[5] = SelectedTitle;

    return Object.keys(bookData).length > 0 ? bookData : null;
}

function FillBooks(){
    //Melhor Opção Primeiro    
    const bestSelection = Books.key[0]      
    const GenderList    = bestSelection['Genero'].split(',');
    document.getElementById("Best_Selection_IMG").src = bestSelection['Capa']
    document.getElementById("Rate").textContent       = bestSelection['Classificação Indicativa']
    document.getElementById("PagesNum").textContent   = bestSelection['Paginas']
    document.getElementById("Author").textContent     = bestSelection['Autor']
    document.getElementById("Title").textContent      = bestSelection['Titulo']
    document.getElementById("Genders").textContent    = (GenderList.length > 0) ? GenderList[0] : "";    
}

async function makeConsult() {        
    let   dots = "";
    const bestSelectionH = document.getElementById("Best_Selection_H");
    
    clearInterval(loadingInterval);
    
    makingConsult = true; 

    loadingInterval = setInterval(() => {
        if (!makingConsult) {
            clearInterval(loadingInterval);
            return;
        }
        dots = dots.length < 3 ? dots + "." : "";
        bestSelectionH.innerText = `Buscando Livros${dots}`;
    }, 400); 

    document.getElementById("Books_Bar").style.display = "block";
    document.getElementById("Books_border").style.display= "block";
    
    /*document.getElementById("Best_Selection").style.visibility = "hidden";
    document.getElementById("Best_Selection_IMG").style.visibility = "hidden";
    document.getElementById("Similars_H").style.visibility = "hidden";
    document.getElementById("Similars").style.visibility = "hidden";*/
    
    _Info = GetMainVars(); 

    if(_Info != null){
        Books = await GetBooks([(_Info && Object.keys(_Info).length > 1 ? 2 : 1), _Info,SimilarsCount])
        if(Books >= 1)            
            clearInterval(loadingInterval);
            FillBooks();
            bestSelectionH.innerText = "Melhor Opção";
    }
    else{
        clearInterval(loadingInterval);
        bestSelectionH.innerText = "Nenhum Dado Informado"
    }

    makingConsult = false
    
    document.getElementById("Similars_H").innerText = ((SimilarsCount == 0) ? "Similares não solicitados" : 'Similares');
    
    /*document.getElementById("Best_Selection").style.visibility = "visible";
    document.getElementById("Best_Selection_IMG").style.visibility = "visible";

    document.getElementById("Similars_H").style.visibility = "visible";
    document.getElementById("Similars").style.visibility = "visible";*/
}